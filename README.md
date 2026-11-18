# news-image-20261118-r4

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/besan11/news-image-20261118-r4/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/besan11/news-image-20261118-r4/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

One page, 44 stories: every story that happened, or was first reported, on Wednesday 18 November 2026 — from the Gulf strikes and the Kerch Bridge collapse to APEC in Shenzhen, Alaska's Senate flip, Nvidia's $115.8bn quarter, two cyclones, Voyager 1 crossing one light-day, and GTA VI going on sale. Three large illustrated leads, ten composed scene panels, a by-the-numbers strip, a world map with numbered pins for the 13 features and dots for all 31 briefs, and a two-column briefs list. Every illustration is drawn from scratch in code; no stock art, no copied images.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, stdlib only) copies the deterministic `entry.png` to the output directory. To regenerate the image from scratch, run `python3 render.py` (Python 3, Pillow only, subset fonts in `fonts/`); two runs produce byte-identical PNGs.

---

<sub>Entered on [make.fun](https://make.fun/?ref=besan11&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
