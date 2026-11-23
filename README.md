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
- **Exit on a take-profit**: **+4.5% over the entry close on the first
  leg**, **+1.5% on later legs** — the first leg banks the big move, later
  legs scalp the smaller ones a maturing trend still offers. The leg
  counter advances only once a sell has actually filled, so a rejected
  sell can never switch the tier.
- **Exit sooner on a real breakdown**: a trailing stop 2% under the best
  close since entry, or a stop-loss 2% under the entry close.
- **No new position in the last 30 bars** of the window, so a buy never pays
  a round trip for minutes that do not exist. After an exit the entry rule
  must re-confirm and 5 bars must pass first.

Every comparison is integer arithmetic on the closes the harness sends, so
the same bars always give the same orders: no clock, no environment, no
unseeded randomness.

## Dev-window result (local grade, published 24h window)

| Metric | Value |
|---|---|
| Net PnL | **+$45.31** |
| First-half PnL (12h) | +$42.86 |
| Second-half PnL (12h) | +$2.45 |
| Max drawdown | 1.58% |
| Trades | 5 (buys at bars 16, 445, 1335; sells at 426, 1330) |
| Fees paid | $2.50 |
| Rejected orders | 0 |

Leg by leg: +$40.44 (buy 16 → take-profit 426, banking the spike to
$61,544), +$14.71 (buy 445 → take-profit 1330), −$9.85 (buy 1335, the
re-entry right at the window's top, ridden down to the flatten).

For reference, the kit's own baselines on the same window: buy-and-hold
+$32.17, momentum +$34.94, EMA-cross −$114.83, RSI-Bollinger −$9.32,
ADX-momentum −$11.20, hold-cash $0.00. This bot beats buy-and-hold by
+$13.14 and momentum by +$10.37. The dev window never decides the
ranking — it only decides who races — so what matters is that the bot is
profitable in both halves of it while actually trading: 5 trades, both
halves positive, drawdown under 2%.

## Sensitivity (same window, one knob moved at a time)

| Change | Net PnL | Trades |
|---|---|---|
| As shipped | **+$45.31** | 5 |
| Entry threshold +0.05% / +0.10% | +$45.31 / +$44.78 | 5 / 5 |
| Entry window 15 min | +$33.04 | 3 |
| Trailing stop 1.5% | +$37.44 | 7 |
| Trailing stop 2.5% / 3% | +$45.31 / +$45.31 | 5 / 5 |
| Stop-loss 1.5% / 3% | +$45.31 / +$45.31 | 5 / 5 |
| Cooldown 3 bars | +$33.03 | 3 |
| Cooldown 8 / 10 bars | +$44.26 / +$44.26 | 5 / 5 |
| No-entry tail 60 / 90 bars | +$45.31 / +$45.31 | 5 / 5 |
| Later-leg take-profit 2.0% | +$45.31 | 3 |
| Later-leg take-profit 1.2% | +$40.04 | 5 |

Honest caveat: the first-leg take-profit is the narrow knob. At +4.5%
it fires into the window's one sharp spike (bars 424–426, $61,146 →
$61,544) and the re-entry waits the cliff out; at +4.2–4.3% it fires a
bar or two earlier for +$44.97 in the single-tier form, and at +4.6% it
never fires (+$34.23). The entry threshold, trailing stop, stop-loss,
cooldown and tail are plateaus; the take-profit level is a genuine
parameter of the strategy (bank a ~4–5% leg, scalp ~1.5% later legs),
tuned on this window only — on the unseen race window it fires whenever
a leg reaches those gains, or not at all, and the trailing stop is what
protects the position then.

## Why this should survive the race window, not just the dev one

- **The entry is a plateau, not a peak.** The same +$45.31 comes out for
  any 10-minute threshold between +0.02% and +0.05%, and for trailing
  stops anywhere from 2% to 3% — nothing here depends on one exact
  number landing on one exact bar.
- **The exits are exercised, not decorative.** Both take-profit tiers
  fire on the dev window, the trailing stop and stop-loss stand ready
  for a real breakdown on the unseen race window, and the 5-bar cooldown
  is what keeps the re-entry after the cliff from buying the falling
  knife (3 bars re-enters at bar 429, still falling, for +$33.03).
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
