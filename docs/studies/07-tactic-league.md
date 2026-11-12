# Study 7: a tactic league

**Status:** done (11 November, 5,440 matches).

## Design

- **17 tactics:** the 10 installed FM27 presets (one per style, from the game's own data) and 7 user tactics: the
  team's own (STORMBRINGER), HIGHWAY STAR 27 BBM 4231 P90, ARGUS 27 3430 P97 and ZaZ's four Ace tactics.
- **Round robin:** every tactic plays every other twice, once on each side, on 20 seeds each: 40 matches per pair,
  640 per tactic.
- **Match:** one of the team's saved Premier League matches (Man City v the team). The home side always has the Man
  City squad and the away side the team's squad; because each pair plays both ways round, every tactic plays as
  often with each squad.
- **Fair conditions:** each side picks its starting XI from its matchday squad by position for its tactic, both
  sides are managed by the assistant during the match, and both sides' tactical familiarity is held at the same
  level (80 in all eight areas, equal complexity).

`scripts/study.py league` runs this for any tactics on any saved match (see the README).

## Table

| # | Tactic | W | D | L | Goals for | Goals against | xG for | xG against | Points per game |
|---|---|---|---|---|---|---|---|---|---|
| 1 | STORMBRINGER 27 BBMIW 424 P102 FA | 313 | 155 | 172 | 1.70 | 1.17 | 1.94 | 1.32 | **1.71** |
| 2 | HIGHWAY STAR 27 BBM 4231 P90 FA | 313 | 152 | 175 | 1.68 | 1.19 | 1.81 | 1.26 | **1.70** |
| 3 | ARGUS 27 3430 P97 FA CC | 300 | 146 | 194 | 1.59 | 1.20 | 1.71 | 1.32 | **1.63** |
| 4 | ZaZ - Ace of Hearts 0.1 | 285 | 146 | 209 | 1.55 | 1.26 | 1.77 | 1.43 | 1.56 |
| 5 | ZaZ - Ace of Clubs 0.1 ST | 275 | 165 | 200 | 1.45 | 1.18 | 1.74 | 1.42 | 1.55 |
| 6 | ZaZ - Ace of Spades 0.1 ST | 278 | 152 | 210 | 1.59 | 1.33 | 1.83 | 1.49 | 1.54 |
| 7 | Preset: Gegenpress | 258 | 171 | 211 | 1.38 | 1.24 | 1.50 | 1.38 | 1.48 |
| 8 | Preset: Fluid Counter-Attack | 241 | 165 | 234 | 1.13 | 1.14 | 1.26 | 1.33 | 1.39 |
| 9 | ZaZ - Ace of Diamonds 0.1 ST | 221 | 179 | 240 | 1.22 | 1.25 | 1.55 | 1.33 | 1.32 |
| 10 | Preset: Direct Counter-Attack | 214 | 169 | 257 | 1.05 | 1.30 | 1.13 | 1.44 | 1.27 |
| 11 | Preset: Wing Play | 214 | 164 | 262 | 1.12 | 1.28 | 1.24 | 1.49 | 1.26 |
| 12 | Preset: Control Possession | 206 | 182 | 252 | 1.10 | 1.24 | 1.32 | 1.34 | 1.25 |
| 13 | Preset: Route One | 214 | 158 | 268 | 1.08 | 1.31 | 1.12 | 1.53 | 1.25 |
| 14 | Preset: Vertical Tiki-Taka | 213 | 160 | 267 | 1.29 | 1.42 | 1.47 | 1.50 | 1.25 |
| 15 | Preset: Tiki-Taka | 197 | 187 | 256 | 0.85 | 1.15 | 1.05 | 1.31 | 1.22 |
| 16 | Preset: Catenaccio | 169 | 168 | 303 | 0.93 | 1.39 | 1.03 | 1.71 | 1.05 |
| 17 | Preset: Park the Bus | 131 | 177 | 332 | 0.69 | 1.34 | 0.73 | 1.62 | 0.89 |

With 640 matches per tactic, differences of about 0.1 points per game between rows are meaningful; smaller ones
(for example among places 10-15) are not.

## Head to head

Points per game of the row tactic against the column tactic. Each cell is 40 matches, so single cells are rough
(about ±0.4); patterns across a row matter more than any one cell.

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 STORMBRINGER | · | 1.6 | 1.9 | 1.5 | 1.3 | 1.8 | 1.3 | 1.5 | 1.9 | 1.9 | 1.9 | 1.8 | 1.8 | 1.7 | 1.6 | 2.0 | 2.0 |
| 2 HIGHWAY STAR P90 | 1.2 | · | 1.4 | 1.5 | 1.7 | 1.4 | 1.5 | 2.0 | 2.0 | 1.8 | 1.8 | 1.6 | 1.8 | 1.9 | 1.8 | 1.8 | 2.1 |
| 3 ARGUS 3430 P97 | 0.9 | 1.6 | · | 1.3 | 1.4 | 1.4 | 1.4 | 1.6 | 1.5 | 1.5 | 1.9 | 1.9 | 1.6 | 1.8 | 1.7 | 2.3 | 2.2 |
| 4 ZaZ Hearts | 1.2 | 1.2 | 1.4 | · | 1.1 | 1.6 | 1.4 | 1.5 | 1.6 | 1.7 | 1.6 | 1.9 | 2.1 | 1.4 | 1.8 | 1.8 | 1.6 |
| 5 ZaZ Clubs | 1.3 | 1.1 | 1.4 | 1.7 | · | 1.7 | 1.2 | 1.2 | 1.3 | 1.7 | 1.9 | 1.4 | 1.9 | 1.5 | 1.8 | 1.8 | 1.9 |
| 6 ZaZ Spades | 1.0 | 1.3 | 1.3 | 1.2 | 1.0 | · | 1.3 | 1.7 | 1.8 | 1.6 | 1.9 | 1.2 | 2.0 | 1.6 | 1.9 | 1.8 | 2.1 |
| 7 Gegenpress | 1.5 | 1.2 | 1.2 | 1.4 | 1.5 | 1.6 | · | 1.2 | 1.6 | 1.4 | 1.4 | 1.8 | 1.1 | 1.6 | 1.5 | 1.6 | 2.1 |
| 8 Fluid Counter-Attack | 1.2 | 0.7 | 1.1 | 1.3 | 1.6 | 1.1 | 1.4 | · | 1.4 | 1.5 | 1.6 | 1.6 | 1.1 | 1.5 | 1.4 | 1.8 | 1.8 |
| 9 ZaZ Diamonds | 0.8 | 0.8 | 1.2 | 1.2 | 1.4 | 0.9 | 1.0 | 1.4 | · | 1.6 | 1.1 | 1.2 | 1.4 | 1.3 | 1.6 | 1.9 | 2.0 |
| 10 Direct Counter-Attack | 0.9 | 1.0 | 1.3 | 1.1 | 1.0 | 1.1 | 1.2 | 1.2 | 1.2 | · | 0.8 | 1.5 | 1.4 | 1.8 | 1.4 | 1.4 | 1.8 |
| 11 Wing Play | 0.9 | 0.9 | 0.9 | 1.1 | 0.9 | 0.9 | 1.4 | 1.2 | 1.6 | 1.8 | · | 1.4 | 1.4 | 1.1 | 1.2 | 1.5 | 1.8 |
| 12 Control Possession | 1.0 | 0.9 | 0.9 | 0.8 | 1.4 | 1.5 | 1.1 | 1.1 | 1.4 | 1.3 | 1.4 | · | 1.2 | 1.5 | 1.2 | 1.7 | 1.6 |
| 13 Route One | 1.1 | 0.9 | 1.2 | 0.7 | 0.9 | 0.8 | 1.6 | 1.6 | 1.3 | 1.2 | 1.4 | 1.5 | · | 1.8 | 1.4 | 1.1 | 1.4 |
| 14 Vertical Tiki-Taka | 1.1 | 1.0 | 1.0 | 1.4 | 1.2 | 1.1 | 1.2 | 1.2 | 1.4 | 1.0 | 1.6 | 1.2 | 1.0 | · | 1.5 | 1.5 | 1.6 |
| 15 Tiki-Taka | 1.1 | 1.1 | 1.0 | 0.9 | 0.9 | 0.9 | 1.2 | 1.3 | 0.9 | 1.2 | 1.5 | 1.5 | 1.4 | 1.2 | · | 1.6 | 1.9 |
| 16 Catenaccio | 0.7 | 0.9 | 0.5 | 1.0 | 1.0 | 1.0 | 1.1 | 1.1 | 0.8 | 1.3 | 1.3 | 0.9 | 1.5 | 1.1 | 1.1 | · | 1.4 |
| 17 Park the Bus | 0.8 | 0.7 | 0.5 | 1.2 | 0.8 | 0.8 | 0.6 | 0.9 | 0.7 | 0.9 | 0.8 | 1.1 | 1.2 | 1.2 | 0.8 | 1.2 | · |

## What it means

1. **The user tactics beat every preset.** Six of the seven take the top six places, clearly ahead of the best
   preset (Gegenpress, 1.48). They create more and better chances (xG for 1.71-1.94 against 1.50 for Gegenpress)
   while conceding about the same (xG against 1.26-1.49 against 1.38).
2. **STORMBRINGER and HIGHWAY STAR P90 are level at the top** (1.71 and 1.70), as in Study 6.
3. **The back-three ARGUS P97 comes third.** In Study 6, played with a 4-2-4 lineup, it looked mid-table; with its
   own XI and equal conditions it is one of the strongest. That supports ZaZ's point that a fixed lineup handicaps
   back-three systems, even though the Study 6 rerun changed less.
4. **ZaZ's Aces:** Hearts, Clubs and Spades are level with each other (1.54-1.56) and ahead of every preset; Diamonds
   is clearly behind them (1.32), mid-table among the presets.
5. **Among the presets, Gegenpress and Fluid Counter-Attack lead,** a group of five follows level at about 1.25, and
   the defensive presets are last: Catenaccio 1.05 and Park the Bus 0.89. Park the Bus concedes no fewer goals than
   the others (1.34 per game) while scoring far fewer.
6. **No tactic beats everything.** Even STORMBRINGER drops points against Ace of Clubs and Gegenpress (1.3 in both
   cells), though with 40 matches per cell that needs confirming.

## Caveats

- **One match as the container,** with the Man City squad on one side and the team's on the other. A league with
  one club's squad on both sides (`--squad`, from a save) would remove the squad difference entirely.
- **Equal, fixed familiarity (80)** for every tactic. In a real save a new tactic starts lower: see Study 3 for what
  that costs.
- **Preset formations:** one formation per preset style, as exported from the game. Other formations of the same
  style may rank differently (harvestgreen22's test found Wing Play strongest in its 4-2-4 / 4-4-2 form).
- **Head-to-head cells are small** (40 matches); the overall table is the reliable part.

## Reproduce

```sh
.venv/bin/python scripts/study.py league runs/league --team "<team>" --seeds 20 --tactics presets \
  "<tactics folder>/STORMBRINGER 27 BBMIW 424 P102 FA.fmf" "<tactics folder>/HIGHWAY STAR 27 BBM 4231 P90 FA.fmf" \
  "<tactics folder>/ARGUS 27 3430 P97 FA CC.fmf" "<tactics folder>/ZaZ - Ace of Hearts 0.1.fmf" ...
```
