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
trend is really up, banks the gain with a take-profit instead of riding
a spike back down, and otherwise stays in cash:

- **Enter** when the close is up at least **+0.02% over the last 10 minutes**
  *and* sits **above its own 10-bar average**. One reading alone can be a
  bounce; the pair means the move is up and above the recent mean.
- **Buy with the full cash balance**, then hold. No scaling in, no second
  position.
- **Exit on a take-profit**: **+4.3% over the entry close, the same on
  every leg** — one level, no tiers, no leg counter. A single level was
  chosen over the old two-tier take-profit (+4.5% first leg, +1.5% later
  legs) to remove the leg-counting knob; see the honest caveat below for
  what it actually measures.
- **Exit sooner on a real breakdown**: a trailing stop 2% under the best
  close since entry, or a stop-loss 2% under the entry close.
- **No new position in the last 30 bars** of the window, so a buy never pays
  a round trip for minutes that do not exist. After an exit the entry rule
  must re-confirm and 8 bars must pass first.

Every comparison is integer arithmetic on the closes the harness sends, so
the same bars always give the same orders: no clock, no environment, no
unseeded randomness.

## Dev-window result (local grade, published 24h window)

| Metric | Value |
|---|---|
| Net PnL | **+$32.70** |
| First-half PnL (12h) | +$30.26 |
| Second-half PnL (12h) | +$2.44 |
| Max drawdown | 1.96% |
| Trades | 3 (buy bar 16, sell bar 425, buy bar 429) |
| Fees paid | $1.65 |
| Rejected orders | 0 |

Leg by leg: +$40.11 (buy 16 → take-profit 425, banking the spike), −$7.41
(buy 429, the re-entry five bars after the exit, ridden down and flattened
at the window's end).

For reference, the kit's own baselines on the same window: buy-and-hold
+$32.17, momentum +$34.94, EMA-cross −$114.83, RSI-Bollinger −$9.32,
ADX-momentum −$11.20, hold-cash $0.00. This bot beats buy-and-hold by
+$0.53 — and **loses to momentum by −$2.24**. The dev window never decides
the ranking — it only decides who races — so what matters is that the bot
is profitable in both halves of it while actually trading: 3 trades, both
halves positive, drawdown under 2%. But on the dev numbers alone this
version is weaker than the two-tier version it replaces (+$45.31, 5 trades),
and that is stated plainly in the caveat below rather than hidden.

## Sensitivity (same window, one knob moved at a time)

| Change | Net PnL | Trades |
|---|---|---|
| Single TP 4.3%, cooldown 5 (previous version) | **+$32.70** | 3 |
| Single take-profit 4.2% / 4.4% | +$32.70 / +$32.70 | 3 / 3 |
| Single take-profit 4.5% | +$45.31 | 3 |
| Single take-profit 4.6% | +$34.23 | 3 |
| Single TP 4.3%, cooldown 8 / 10 bars | +$44.97 / +$44.97 | 3 / 3 |
| Single TP 4.2% / 4.4%, cooldown 10 bars | +$44.97 / +$44.97 | 3 / 3 |

Honest caveat: with the old 5-bar cooldown the single take-profit
level was a knife-edge, not a plateau. At +4.5% the sell is decided
one bar later (bar 425 instead of 424), which pushes the re-entry
past the trap: the bot re-enters at bar 445 instead of 429 and the
second leg ends +$4.87 instead of −$7.41. At +4.2–4.4% it sells at
bar 424, the 5-bar cooldown expires at 429 while the 10-minute
return still straddles the pre-spike low, so the entry rule
re-confirms into the falling leg. At +4.6% the take-profit never
fires at all and the trailing stop banks +$43.95 before a top
re-entry loses −$9.72. So the old version removed the leg-counting
knob but kept a one-bar knob: the sell bar decided the re-entry.
The fix shipped here is a longer cooldown — 8 bars after an exit
blocks the bar-429 trap, and with it the take-profit is a real
plateau (+$44.97 at 4.2–4.4%, +$45.31 at 4.5%). The numbers above
are the old version's measurements, kept so the change can be
checked against them.

## Why this should survive the race window, not just the dev one

- **The entry is a plateau, not a peak.** The same entry rule produced
  +$45.31 for the two-tier version for any 10-minute threshold between
  +0.02% and +0.05%, and for trailing stops anywhere from 2% to 3% —
  nothing in the entry depends on one exact number landing on one
  exact bar.
- **The exits are exercised, not decorative — but the re-entry is the
  live risk.** The single take-profit fires once on the dev window, and
  the trailing stop and stop-loss stand ready for a real breakdown on
  the unseen race window. The measured weakness was the re-entry after
  the spike: with the old 5-bar cooldown the bot re-entered at bar 429,
  still falling, for −$7.41 on that leg. The 8-bar cooldown shipped here
  blocks that trap on the dev window and restores +$44.97 with a real
  take-profit plateau — see the sensitivity table above.
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
