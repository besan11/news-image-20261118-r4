# NOTES — news-image-20261118 round 4

Rebuilt from zero in one session. All 44 stories were re-verified against live
sources (Reuters, AP, BBC, Al Jazeera, NASA, UN, WHO, IMD, ONS) on 19 Nov 2026.

## Story changes vs the spec draft
- Brief 29: the spec's Eswatini border-clash brief failed verification (no such
  clashes found) — replaced with the verified backup: Ethiopia–Eritrea border
  fighting resumes, raising fears of a wider war.
- Brief 38: the spec's Fela Kuti Rock Hall induction was 14 Nov, not 18 Nov —
  replaced with the verified backup: Robert Pattinson named the new James Bond
  (announced 16 Nov, reactions continuing through 18 Nov).
- Brief 16: PNG quake is M6.0 per GFZ (USGS M5.8); Romania M5.3, two hurt.
- Brief 22: UK blacklists 8 Israeli construction companies; Australia lists
  3 people + 4 organisations (the spec's "Australia lists 7 firms" was wrong).
- Brief 23: market numbers are Tuesday 17 Nov closes reported Wed 18 Nov:
  S&P 500 −1.03%, Nasdaq −0.74%, Dow −1.64%, VIX 25.46 (+11%), gold −2%.
  FTSE/Brent specifics dropped (unconfirmed).
- Feature 9 headline: spec's "COLD KILLS IN TENTS" is unsafe (that death was
  13 Nov news) — headline is "GAZA TRUCE MAY COLLAPSE" (Board of Peace report).
- Feature 13: Ebola in DR Congo is 11,432 cases / 5,593 deaths (as of 15 Nov).
- Alaska + Nvidia kept as 18 Nov features (top entries feature them the same way).

## Build
- `render.py` — Python 3 + Pillow only. Draws every scene, the map, the
  numbers strip and all text from scratch. No randomness, no clock: two runs
  produce byte-identical PNGs (sha256 verified).
- `main.ts` — Node 22 stdlib only; copies `entry.png` to the output dir.
- `fonts/` — Liberation Serif/Sans subsets made with pyftsubset from system
  fonts. No base64 font data anywhere in the code.
- Region-count bar: EUROPE 15 · AMERICAS 9 · ASIA 6 · MIDDLE EAST 4 ·
  OCEANIA 4 · GLOBAL 4 · AFRICA 2 = 44.

## Self-check
- 1024×1024 PNG, 205,334 bytes (< 1 MiB), deterministic (2 renders, same sha256).
- Full-res crops of every section inspected: no overlapping or garbled text;
  all 13 decks complete (2 lines each); all 31 briefs on one line each.
- Map: 12 numbered pins on-map (1–7, 9–13) + Voyager 1 (8) and solar flare
  (33) marked off-map with a legend note; dots for briefs 14–44.
