# Study 7: a tactic league

**Status:** done. Main version on neutral ground (12 November, 5,440 matches); a first version on the team's own
match (11 November, 5,440 matches) is kept below for comparison.

The question: which tactics are strongest when they play each other, with nothing else different? Seventeen
tactics play a full league: every tactic against every other, at home and away, over 20 seasons.

## Design (neutral ground)

- **17 tactics:** the 10 installed FM27 presets (one per style, from the game's own data) and 7 community tactics:
  STORMBRINGER 27 BBMIW 424 P102, HIGHWAY STAR 27 BBM 4231 P90, ARGUS 27 3430 P97 and ZaZ's four Ace tactics.
- **The same squad for every team:** the synthetic Premier League middle-eight reference squad (invented players
  calibrated on FM27's database; see the README), so only the tactics differ.
- **No real team involved:** fixtures are played in two template matches between other clubs (Leeds v Tottenham and
  Everton v West Ham), one per season in turn; only their stadium and conditions are used, never their players.
- **Equal conditions:** both sides start alike (full fitness and sharpness, the same morale and cohesion), tactical
  familiarity is held at 80 in all eight areas for every team, each side picks its XI by position for its tactic,
  and the assistant manages both sides during the match.
- **20 seasons** (each on new seeds): 32 matches per tactic per season, 640 in all.

## Table

Per season of 32 matches, averaged over the 20 seasons; ± is the spread of a tactic's points across seasons.

| # | Tactic | W | D | L | Goals for | Goals against | xG for | xG against | Points | ± | Points per game |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | STORMBRINGER 27 BBMIW 424 P102 | 16.4 | 8.0 | 7.7 | 59.3 | 39.6 | 1.99 | 1.37 | 57.0 | 7.2 | **1.78** |
| 2 | ARGUS 27 3430 P97 | 15.8 | 8.2 | 7.9 | 59.1 | 42.0 | 1.90 | 1.35 | 55.8 | 7.0 | **1.74** |
| 3 | ZaZ - Ace of Clubs | 15.8 | 6.8 | 9.4 | 60.0 | 45.0 | 1.93 | 1.43 | 54.3 | 7.5 | **1.70** |
| 4 | ZaZ - Ace of Diamonds | 14.2 | 8.4 | 9.4 | 52.6 | 41.5 | 1.77 | 1.38 | 50.9 | 8.8 | **1.59** |
| 5 | HIGHWAY STAR 27 BBM 4231 P90 | 13.2 | 8.6 | 10.2 | 50.2 | 44.9 | 1.79 | 1.38 | 48.4 | 7.4 | **1.51** |
| 6 | ZaZ - Ace of Spades | 13.6 | 7.3 | 11.1 | 54.3 | 48.0 | 1.87 | 1.63 | 48.0 | 6.0 | **1.50** |
| 7 | ZaZ - Ace of Hearts | 12.8 | 7.6 | 11.6 | 54.5 | 51.4 | 1.81 | 1.56 | 46.0 | 7.0 | **1.44** |
| 8 | Preset: Gegenpress | 12.1 | 8.3 | 11.6 | 45.1 | 44.0 | 1.53 | 1.45 | 44.6 | 7.8 | 1.39 |
| 9 | Preset: Fluid Counter-Attack | 11.8 | 8.8 | 11.4 | 39.9 | 39.1 | 1.34 | 1.36 | 44.0 | 6.5 | 1.38 |
| 10 | Preset: Wing Play | 11.5 | 7.8 | 12.7 | 42.0 | 48.0 | 1.39 | 1.61 | 42.3 | 6.0 | 1.32 |
| 11 | Preset: Control Possession | 10.8 | 8.3 | 12.8 | 40.6 | 44.4 | 1.37 | 1.44 | 40.9 | 7.5 | 1.28 |
| 12 | Preset: Route One | 10.2 | 8.2 | 13.6 | 36.0 | 42.5 | 1.19 | 1.59 | 38.8 | 6.2 | 1.21 |
| 13 | Preset: Direct Counter-Attack | 9.7 | 9.3 | 12.9 | 34.9 | 42.0 | 1.20 | 1.48 | 38.5 | 5.6 | 1.20 |
| 14 | Preset: Vertical Tiki-Taka | 9.9 | 8.3 | 13.8 | 44.5 | 53.2 | 1.46 | 1.66 | 38.1 | 7.7 | 1.19 |
| 15 | Preset: Tiki-Taka | 9.6 | 8.1 | 14.4 | 32.9 | 43.8 | 1.13 | 1.37 | 36.7 | 7.8 | 1.15 |
| 16 | Preset: Catenaccio | 8.3 | 8.0 | 15.8 | 32.3 | 48.8 | 1.06 | 1.78 | 32.9 | 7.5 | 1.03 |
| 17 | Preset: Park the Bus | 6.9 | 8.8 | 16.4 | 25.8 | 45.8 | 0.83 | 1.73 | 29.4 | 7.0 | 0.92 |

**How sure:** one season's points swing by about ±7, but over 20 seasons a tactic's points per game is known to
about ±0.05. Gaps of 0.1 points per game or more between rows are real; smaller ones (for example among places
10-15) are not.

## Head to head

Points per match of the row tactic against the column tactic (40 matches per cell: both venues, 20 seasons; single
cells are rough, about ±0.35).

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 STORMBRINGER | · | 1.6 | 1.6 | 1.4 | 1.9 | 1.5 | 2.2 | 1.3 | 2.0 | 1.7 | 1.8 | 1.9 | 1.7 | 1.8 | 1.9 | 2.3 | 2.3 |
| 2 ARGUS 3430 P97 | 1.1 | · | 1.6 | 1.6 | 1.8 | 1.6 | 2.0 | 1.6 | 1.5 | 1.5 | 1.8 | 2.0 | 1.6 | 2.3 | 2.2 | 1.9 | 1.8 |
| 3 ZaZ Clubs | 1.2 | 1.1 | · | 1.2 | 1.4 | 1.8 | 1.2 | 1.7 | 1.6 | 2.0 | 2.2 | 1.7 | 1.6 | 1.7 | 2.0 | 2.3 | 2.2 |
| 4 ZaZ Diamonds | 1.3 | 1.1 | 1.4 | · | 1.1 | 1.6 | 1.6 | 1.2 | 1.4 | 1.8 | 1.6 | 2.0 | 1.8 | 2.0 | 1.8 | 1.6 | 2.0 |
| 5 HIGHWAY STAR P90 | 0.9 | 1.1 | 1.3 | 1.6 | · | 1.4 | 1.7 | 1.5 | 1.8 | 1.3 | 1.4 | 1.4 | 1.9 | 1.5 | 1.4 | 2.0 | 2.1 |
| 6 ZaZ Spades | 1.2 | 1.2 | 1.1 | 1.1 | 1.4 | · | 1.5 | 1.6 | 1.4 | 1.5 | 1.7 | 1.5 | 1.9 | 1.5 | 1.7 | 1.8 | 1.9 |
| 7 ZaZ Hearts | 0.6 | 0.8 | 1.5 | 1.1 | 1.1 | 1.4 | · | 1.5 | 1.2 | 1.6 | 1.6 | 1.8 | 1.7 | 1.4 | 1.9 | 1.9 | 1.9 |
| 8 Gegenpress | 1.4 | 1.1 | 1.1 | 1.4 | 1.4 | 1.2 | 1.2 | · | 1.6 | 1.7 | 1.8 | 1.3 | 1.3 | 1.5 | 1.4 | 1.6 | 1.5 |
| 9 Fluid Counter-Attack | 0.8 | 1.2 | 1.1 | 1.4 | 0.9 | 1.3 | 1.5 | 1.2 | · | 1.5 | 1.4 | 1.4 | 1.2 | 1.6 | 1.6 | 1.7 | 2.0 |
| 10 Wing Play | 1.0 | 1.1 | 0.8 | 1.0 | 1.4 | 1.3 | 1.1 | 1.1 | 1.1 | · | 1.5 | 1.8 | 1.4 | 1.4 | 1.6 | 1.5 | 2.0 |
| 11 Control Possession | 0.9 | 0.9 | 0.6 | 1.1 | 1.4 | 1.0 | 1.1 | 1.1 | 1.3 | 1.4 | · | 1.7 | 1.6 | 1.3 | 1.9 | 1.6 | 1.7 |
| 12 Route One | 1.0 | 0.8 | 1.2 | 0.8 | 1.1 | 1.2 | 1.1 | 1.5 | 1.2 | 0.9 | 1.1 | · | 1.6 | 1.6 | 1.1 | 1.6 | 1.6 |
| 13 Direct Counter-Attack | 1.1 | 1.1 | 1.2 | 1.1 | 0.8 | 0.8 | 0.9 | 1.3 | 1.4 | 1.3 | 1.2 | 1.1 | · | 1.2 | 1.3 | 1.6 | 1.7 |
| 14 Vertical Tiki-Taka | 0.9 | 0.5 | 1.0 | 0.8 | 1.2 | 1.2 | 1.2 | 1.4 | 1.1 | 1.4 | 1.5 | 1.1 | 1.5 | · | 1.2 | 1.6 | 1.5 |
| 15 Tiki-Taka | 0.9 | 0.7 | 0.8 | 0.9 | 1.1 | 1.1 | 0.8 | 1.4 | 1.1 | 1.2 | 0.8 | 1.6 | 1.4 | 1.5 | · | 1.4 | 1.4 |
| 16 Catenaccio | 0.6 | 0.8 | 0.5 | 1.1 | 0.7 | 1.0 | 1.0 | 1.1 | 1.0 | 1.3 | 1.2 | 1.1 | 1.1 | 1.1 | 1.4 | · | 1.4 |
| 17 Park the Bus | 0.6 | 1.0 | 0.6 | 0.8 | 0.7 | 0.9 | 0.9 | 1.0 | 0.8 | 0.7 | 1.1 | 1.1 | 0.8 | 1.1 | 1.4 | 1.1 | · |

## What it means

1. **Every community tactic beats every preset.** The weakest of the seven (Ace of Hearts, 1.44) is ahead of the best
   preset (Gegenpress, 1.39). They create more and better chances (xG for 1.77-1.99 against 1.06-1.53 for the
   presets) without conceding more.
2. **STORMBRINGER and ARGUS lead** (1.78 and 1.74), then Ace of Clubs (1.70). STORMBRINGER also tops the head to head:
   it takes more than 1.5 points per match against 13 of the 16 others.
3. **Among the presets,** Gegenpress and Fluid Counter-Attack lead, a middle group follows within noise of each
   other, and the defensive presets are last: Catenaccio (1.03) and Park the Bus (0.92), which concede no fewer goals
   than the others while scoring far fewer.
4. **No tactic beats everything.** Even STORMBRINGER takes less than 1.5 points per match against Ace of Diamonds (1.4)
   and Gegenpress (1.3); single cells need more seasons to confirm.

## Does the setting matter?

- **The template match hardly matters.** The table from the Leeds v Tottenham seasons alone and from the Everton v
  West Ham seasons alone correlate at 0.95 (rankings 0.96). The largest gap is Ace of Diamonds (1.69 against 1.49):
  it may suit some settings better than others.
- **The team and match of the first version hardly matter either.** Points per game here and in the first version
  (one real saved match, its real squads on each side) correlate at 0.90 over the 17 tactics. The conclusions above
  hold in both. What moved: ARGUS (third → second), Ace of Clubs (fifth → third) and Ace of Diamonds (ninth → fourth)
  rose; HIGHWAY STAR P90 fell (joint first → fifth) and Gegenpress slipped (1.48 → 1.39).
- **Home advantage** in these leagues: the home side won 39% of matches and drew 26%.

## Caveats

- **One squad level:** a Premier League middle-eight squad on both sides. A much stronger or weaker squad may suit
  different tactics; the League page can repeat this with the top-six or bottom-six reference squads.
- **Equal, fixed familiarity (80)** for every tactic. In a real save a new tactic starts lower: see Study 3.
- **One formation per preset style,** as exported from the game; other formations of the same style may rank
  differently.
- **Head-to-head cells are small** (40 matches); the table is the reliable part.

## Reproduce

In the app: **Test a league**, add the presets and the tactic files, squad *Synthetic: Premier League, middle eight*,
familiarity 80, 20 seasons, template Leeds v Tottenham alternating with Everton v West Ham (or any two matches between
other clubs). From the command line:

```sh
.venv/bin/python scripts/study.py league runs/league --match "<template 1>.pkm" "<template 2>.pkm" --seeds 20 \
  --familiarity 80 --reference pl-middle --equal-start --tactics presets "<tactics folder>/<tactic>.fmf" ...
```

# First version: on the team's match (11 November)

The same 17 tactics in one of the team's real saved matches (Man City v the team), with that match's real squads:
the home side always had the Man City squad, the away side the team's, and every pair played both ways round.
Familiarity was held at 80 for both sides; the start state was the match's own.

### Table

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

### Head to head

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

### What it means

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

### Caveats

- **One match as the container,** with the Man City squad on one side and the team's on the other. A league with
  one club's squad on both sides (`--squad`, from a save) would remove the squad difference entirely.
- **Equal, fixed familiarity (80)** for every tactic. In a real save a new tactic starts lower: see Study 3 for what
  that costs.
- **Preset formations:** one formation per preset style, as exported from the game. Other formations of the same
  style may rank differently (harvestgreen22's test found Wing Play strongest in its 4-2-4 / 4-4-2 form).
- **Head-to-head cells are small** (40 matches); the overall table is the reliable part.

### Reproduce

```sh
.venv/bin/python scripts/study.py league runs/league --team "<team>" --seeds 20 --tactics presets \
  "<tactics folder>/STORMBRINGER 27 BBMIW 424 P102 FA.fmf" "<tactics folder>/HIGHWAY STAR 27 BBM 4231 P90 FA.fmf" \
  "<tactics folder>/ARGUS 27 3430 P97 FA CC.fmf" "<tactics folder>/ZaZ - Ace of Hearts 0.1.fmf" ...
```
