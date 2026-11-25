# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/ifulchina-ops/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/ifulchina-ops/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

The World Today — 25 November 2026: one front-page image summing up the
day's world news. The lead story is Ukraine's strikes on Russian ships —
Zelenskyy confirming the Gulf of Finland drone strike and a warship sunk
off Benghazi, Libya — with NATO's early-warning aircraft for Poland,
naval mines hitting three tankers in the Strait of Hormuz, the Houthi
strike on Riyadh's tallest tower, Nvidia's $1 trillion day as Huang
returns as CEO, and Trump's Thanksgiving pardon of turkeys Freedom and
Feathers. A ticker carries the rest of the day: the Nepal quake, the
Sarkozy case going to trial, the 700,000 Russian soldiers killed, and
England's T20 win.

`main.py` draws the whole page from scratch in pure-stdlib Python 3.13 —
a hand-written PNG encoder, a 5x7 bitmap font, and geometric pictures —
and writes `entry.png` (1024x1024, 21,219 bytes, deterministic: two runs
are byte-identical). No network, no image libraries, no files read.

![The World Today — 25 November 2026](entry.png)

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
