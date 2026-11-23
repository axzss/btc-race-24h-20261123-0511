# cbBTC Trend Rider — make.fun bounty entry

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/axzss/btc-race-24h-20261123-0511/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/axzss/btc-race-24h-20261123-0511/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

A trading bot for [make.fun](https://make.fun/bounty/btc-race-24h-20261123-0511)'s
**Race a BTC trading bot live for 24 hours** bounty. It trades Coinbase
Wrapped BTC (cbBTC) against USDC, minute by minute, on paper money: $1,000
starting capital, long only, at most one open position.

## How it trades

A full-size round trip costs roughly 26 bps in fees, slippage and pool
impact, so the bot only trades when two short-horizon readings agree the
trend is really up, and otherwise stays in cash:

- **Enter** when the close is up at least **+0.10% over the last 30 minutes**
  *and* sits **above its own 30-bar average**. One reading alone can be a
  bounce; the pair means the move is up and above the recent mean.
- **Buy with the full cash balance**, then hold. No scaling in, no second
  position.
- **Exit only on a real breakdown**: a trailing stop 2% under the best
  close since entry, a stop-loss 2% under the entry close, or a hard exit
  when the 240-minute return turns worse than −1.5%.
- **No new position in the last 90 bars** of the window, so a buy never pays
  a round trip for minutes that do not exist. After an exit the entry rule
  must re-confirm and 30 bars must pass first.

Every comparison is integer arithmetic on the closes the harness sends, so
the same bars always give the same orders: no clock, no environment, no
unseeded randomness.

## Dev-window result (local grade, published 24h window)

| Metric | Value |
|---|---|
| Net PnL | **+$33.52** |
| First-half PnL (12h) | +$31.08 |
| Second-half PnL (12h) | +$2.44 |
| Max drawdown | 1.98% |
| Trades | 1 (buy once, hold to the flatten) |
| Fees paid | $0.81 |
| Rejected orders | 0 |

For reference, the kit's own baselines on the same window: buy-and-hold
+$32.17, momentum +$34.94, EMA-cross −$114.83, RSI-Bollinger −$9.32,
ADX-momentum −$11.20, hold-cash $0.00. The dev window never decides the
ranking — it only decides who races — so what matters is that the bot is
profitable in both halves of it without churning: one trade, no whipsaw,
drawdown under 2%.

## Why this should survive the race window, not just the dev one

- **The entry is a plateau, not a peak.** The same entry bar (and the same
  +$33.52) comes out for any 30-minute threshold between +0.08% and
  +0.15%, and for trailing stops anywhere from 2% to 5% — nothing here
  depends on one exact number landing on one exact bar.
- **The exits are insurance, not the strategy.** None of the three exits
  fires on the dev window; they exist so a real breakdown on the unseen
  race window cuts the position instead of riding it to the flatten.
- **Deterministic.** Two local runs over the dev window produce
  byte-identical action logs (same SHA-256), and the bot runs unchanged as
  user `nobody` with a read-only working directory, as the grader runs it.

## Files

- `main.py` — the bot (Python 3.13, standard library only).
- `vendor/makefun_bars.py` — the kit's protocol shim, copied byte for byte
  (excluded from authorship counts, as the rules allow).
- `LICENSE` — MIT.

## Run it

The grader runs `python3 -P -s main.py` with `PYTHONHASHSEED=0`. To grade
locally with the kit:

```sh
node cli/makefun.mjs grade-local --kit <kit-dir> --bot <this-repo> --driver docker
```

## License

MIT — see [LICENSE](LICENSE).

---

<sub>Entered on [make.fun](https://make.fun/?ref=1409h78a&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
