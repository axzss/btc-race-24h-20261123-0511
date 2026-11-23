"""cbBTC trend rider for make.fun's btc-race-24h-20261123-0511.

One asset (CBBTC), long only, at most one open position, paper capital
1,000 USDC. The bot rides a confirmed short-horizon uptrend and otherwise
stays in cash: in a 24-hour window a full-size round trip costs roughly
26 bps in fees, slippage and pool impact, so every trade has to earn its
keep, and chopping in and out of one-minute noise pays the market maker
instead of the bot.

Idea, in one paragraph. A trend is only worth chasing once two independent
short-horizon readings agree: the close has risen over the last 30 minutes
*and* it sits above its own 30-bar average, so the move is both up and
above the recent mean rather than a bounce from below it. The bot then
buys with the whole cash balance and holds, protected by three exits that
only fire on a real breakdown: a trailing stop 2% under the best close
since entry, a stop-loss 2% under the entry close, and a hard exit when
the 240-minute return turns worse than -1.5%. No new position is opened
in the last 90 bars of the window, so a buy never pays a round trip for
minutes that do not exist. After an exit the entry rule must re-confirm
and 30 bars must pass first, so a whipsaw cannot re-enter on the same
noise that stopped it out.

Everything is integer arithmetic on the bar closes the harness sends, so
the same bars give the same orders on every run: no clock, no environment,
no unseeded randomness, nothing read from outside the batches. The
protocol shim lives in vendor/ (a byte-identical copy of the kit's SDK);
the strategy below is mine.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"

# --- entry: both readings must agree -------------------------------------
# 30-minute return of at least +0.10%: close[-1] / close[-31] - 1 >= 1/1000.
ENTRY_RETURN_NUM = 1001  # 1000 * close[-1] >= 1001 * close[-31]
ENTRY_RETURN_DEN = 1000
ENTRY_WINDOW = 30        # bars of history the entry readings need
# Close above its 30-bar mean: 30 * close[-1] > sum of the last 30 closes.

# --- exits: only a real breakdown gets out -------------------------------
# Trailing stop: 2% under the highest close since entry.
TRAIL_NUM = 98           # 100 * close < 98 * peak
TRAIL_DEN = 100
# Stop-loss: 2% under the entry close.
STOP_NUM = 98
STOP_DEN = 100
# Hard reversal exit: 240-minute return worse than -1.5%.
REVERSAL_NUM = 985       # 1000 * close[-1] < 985 * close[-241]
REVERSAL_DEN = 1000
REVERSAL_WINDOW = 240

# --- pacing ---------------------------------------------------------------
COOLDOWN_BARS = 30       # bars to wait after an exit before re-entering
NO_ENTRY_LAST_BARS = 90  # no new position in the window's last 90 bars
WINDOW_BARS = 1440       # one-minute bars per window, per the competition rules
MAX_SLIPPAGE_BPS = 150   # 1.5% past the close the order was decided on


class TrendRider:
    """State for one run: the closes seen so far and the open trade, if any."""

    def __init__(self):
        self.closes = []        # closes of CBBTC, in batch order
        self.peak = None        # highest close since the current entry
        self.entry_close = None
        self.last_exit_seq = -10 ** 9

    def note_bar(self, bar):
        self.closes.append(int(bar["c"]))

    def _entry_confirmed(self):
        """Both short-horizon readings agree the trend is up."""
        closes = self.closes
        if len(closes) <= ENTRY_WINDOW:
            return False
        # 30-minute return >= +0.10%.
        if ENTRY_RETURN_DEN * closes[-1] < ENTRY_RETURN_NUM * closes[-ENTRY_WINDOW - 1]:
            return False
        # Close above its 30-bar mean.
        if ENTRY_WINDOW * closes[-1] <= sum(closes[-ENTRY_WINDOW:]):
            return False
        return True

    def _exit_reason(self):
        """Why the open position should close now, or None to keep holding."""
        closes = self.closes
        close = closes[-1]
        if TRAIL_DEN * close < TRAIL_NUM * self.peak:
            return "trailing-stop"
        if STOP_DEN * close < STOP_NUM * self.entry_close:
            return "stop-loss"
        if len(closes) > REVERSAL_WINDOW:
            if REVERSAL_DEN * close < REVERSAL_NUM * closes[-REVERSAL_WINDOW - 1]:
                return "reversal"
        return None

    def on_batch(self, state, batch):
        for bar in batch["bars"]:
            if bar["symbol"] == SYMBOL:
                self.note_bar(bar)
        if state.warming_up:
            return []
        if not self.closes:
            return []

        held = state.positions.get(SYMBOL)
        if held is not None and held.qty > 0:
            close = self.closes[-1]
            if self.peak is None or close > self.peak:
                self.peak = close
            if self.entry_close is None:
                self.entry_close = close
            if self._exit_reason() is not None:
                # Do not reset peak/entry here: if this sell is rejected
                # (slippage, no bar) the position is still open next batch
                # and the trailing stop must still be measured from the
                # true peak, not from wherever the retry happens.
                self.last_exit_seq = state.seq
                return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            return []

        # Flat: the previous trade is really over, so its memory goes now.
        self.peak = None
        self.entry_close = None

        # Flat: only enter on a confirmed trend, not in the window's tail,
        # and not on the heels of an exit.
        if state.seq > WINDOW_BARS - NO_ENTRY_LAST_BARS:
            return []
        if state.seq - self.last_exit_seq < COOLDOWN_BARS:
            return []
        if state.cash < int(state.hello["fees"]["min_notional_quote_units"]):
            return []
        if self._entry_confirmed():
            self.entry_close = self.closes[-1]
            self.peak = self.closes[-1]
            return [{"side": "buy", "symbol": SYMBOL,
                     "notional_quote_units": state.cash,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []


makefun_bars.run(TrendRider().on_batch)
