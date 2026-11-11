# Study 6: tactics on real matches, at two familiarity levels

**Status:** done (10 November, 9,600 matches).

## Design

- **Tactics:** 23 in total.
  - The 10 FM27 preset styles, exported by the host from the game's own data.
  - The 13 of the user's 25 `.fmf` files that FM27's own tactic decoder accepts.
  The other 12 are rejected by the decoder. They are mostly FM24/FM26-era files (the HIGHWAY STAR 4231 P107 FC copies,
  PINK MOON 26.3, the older ZaZ ones). Opening and re-exporting them in FM27 will probably fix that.
- **Matches:** The team plays each tactic in the 10 real matches. The opponent keeps its saved tactic and players.
  The team's players keep their saved lineup slots; roles, duties, instructions and mentality come from the
  tactic.
- **Seeds:** 1-20, so 200 pairs per tactic and level, against the saved tactic on the same seeds.
- **Familiarity:**
  - "own": the effectiveness record as the game builds it.
  - "low": the eight tactical areas held at 20 for every player of the team (as in [Study 4](04-attributes-x-familiarity.md)).
- **Check:** the team's saved tactic is STORMBRINGER 27 BBMIW 424 P102 FA. Imported from its `.fmf` file, it gives exactly
  the same 200 matches as the saved match's own tactic.

## Results

Sorted by xG difference against the saved tactic (Δ). Saved tactic: 1.80 points per game.

| Tactic | ppg | Δ ppg (t) | Δ xGD (t) | xG for | xG against | at low familiarity: ppg | Δ xGD (t) |
|---|---|---|---|---|---|---|---|
| STORMBRINGER 27 BBMIW 424 P102 FA | 1.80 | +0.00 (+0.0) | +0.00 (+0.0) | +0.00 | +0.00 | 1.59 | -0.10 (-1.0) |
| ZaZ - Ace of Spades 0.1 ST | 1.68 | -0.12 (-1.0) | -0.06 (-0.6) | +0.06 | +0.12 | 1.64 | -0.26 (-2.5) |
| HIGHWAY STAR 27 BBM 4231 P90 FA | 1.78 | -0.01 (-0.1) | -0.14 (-1.3) | -0.14 | -0.00 | 1.76 | -0.13 (-1.2) |
| ZaZ - Ace of Clubs 0.1 ST | 1.64 | -0.17 (-1.3) | -0.19 (-1.9) | -0.13 | +0.06 | 1.32 | -0.53 (-5.5) |
| Underdog fm27 | 1.64 | -0.17 (-1.3) | -0.20 (-2.0) | -0.17 | +0.03 | 1.46 | -0.42 (-4.5) |
| ZaZ - Ace of Hearts 0.1 | 1.62 | -0.18 (-1.4) | -0.21 (-2.0) | -0.11 | +0.10 | 1.19 | -0.58 (-6.1) |
| GYR - BEAST 4231 FM27 | 1.60 | -0.20 (-1.5) | -0.22 (-2.0) | -0.07 | +0.15 | 1.62 | -0.24 (-2.2) |
| FM preset Gegenpress | 1.58 | -0.21 (-1.8) | -0.23 (-2.4) | -0.33 | -0.10 | 1.45 | -0.44 (-4.4) |
| ZaZ - Ace of Diamonds 0.1 ST | 1.64 | -0.16 (-1.3) | -0.23 (-2.2) | -0.27 | -0.04 | 1.41 | -0.28 (-2.7) |
| ARGUS 27 3430 P97 FA CC | 1.56 | -0.24 (-2.0) | -0.28 (-2.9) | -0.27 | +0.01 | 1.33 | -0.51 (-5.3) |
| Beta 4-1-4-1 believe it | 1.49 | -0.31 (-2.6) | -0.33 (-3.4) | -0.32 | +0.00 | 1.35 | -0.50 (-5.0) |
| FM preset Control Possession | 1.62 | -0.17 (-1.4) | -0.37 (-3.6) | -0.40 | -0.03 | 1.32 | -0.50 (-5.1) |
| ARGUS 27 AWB 3430 P100 FA | 1.61 | -0.19 (-1.5) | -0.39 (-3.9) | -0.21 | +0.18 | 1.54 | -0.46 (-4.6) |
| HIGHWAY STAR 27 4231 P101 EC CC | 1.61 | -0.19 (-1.5) | -0.42 (-4.2) | -0.27 | +0.15 | 1.59 | -0.35 (-3.4) |
| FM preset Fluid Counter-Attack | 1.36 | -0.44 (-3.8) | -0.48 (-4.6) | -0.58 | -0.10 | 1.37 | -0.62 (-6.1) |
| FM preset Direct Counter-Attack | 1.35 | -0.45 (-3.6) | -0.67 (-6.8) | -0.74 | -0.07 | 1.41 | -0.78 (-7.8) |
| FM preset Vertical Tiki-Taka | 1.22 | -0.58 (-4.6) | -0.68 (-7.2) | -0.58 | +0.10 | 1.21 | -0.78 (-7.6) |
| FM preset Wing Play | 1.30 | -0.49 (-3.9) | -0.71 (-6.9) | -0.61 | +0.10 | 1.50 | -0.35 (-3.7) |
| FM preset Tiki-Taka | 1.21 | -0.59 (-4.8) | -0.83 (-8.7) | -0.87 | -0.04 | 1.39 | -0.74 (-8.0) |
| 424 ROUTE1 TORQUAY P93 | 1.49 | -0.32 (-2.5) | -0.85 (-9.2) | -0.74 | +0.11 | 1.50 | -0.64 (-6.5) |
| FM preset Route One | 1.36 | -0.44 (-3.7) | -0.93 (-9.8) | -0.82 | +0.12 | 1.40 | -0.68 (-7.0) |
| FM preset Catenaccio | 1.20 | -0.60 (-5.3) | -1.09 (-11.5) | -0.98 | +0.12 | 1.31 | -1.04 (-10.7) |
| FM preset Park the Bus | 0.86 | -0.94 (-8.2) | -1.41 (-16.0) | -1.24 | +0.17 | 0.98 | -1.29 (-14.2) |

With 200 pairs, a Δ ppg needs to be about ±0.25 to be clear; Δ xGD is more sensitive (about ±0.2).

## What it means

1. **The team's own tactic, STORMBRINGER, is the best of the 23 on these matches.** No tactic beats it. HIGHWAY STAR 27 BBM 4231
   P90 FA (−0.14 xGD, t −1.3) and ZaZ Ace of Spades (−0.06, t −0.6) are statistically level with it.
2. **The installed presets are clearly worse for this squad.** The best, Gegenpress, costs 0.23 xG difference per
   game. The defensive presets are the worst by far:
   - Park the Bus: 0.86 points per game, −1.4 xG difference.
   - Catenaccio: 1.20 points per game, −1.1 xG difference.
   A lower-table side does not gain by sitting deep in this engine: it creates about 1 to 1.2 xG less per game and concedes slightly more, not less.
3. **Familiarity hurts some tactics more than others.**
   - At low familiarity, the saved tactic loses only about 0.2 points per game.
   - ZaZ Ace of Hearts and Ace of Clubs lose 0.4 and 0.3 points per game.
   - The top of the ranking barely changes.
4. **Some presets do as well or better at low familiarity than at "own"** (Wing Play, Tiki-Taka, Route One). This
   is not explained yet. It is not the familiarity records: a check (below) shows that "own" gives every tactic the
   same records. Possibly some styles depend less on familiarity, or this is noise (each "low" result rests on 200
   pairs, so a 0.3 xGD difference between the two columns is about 2.5 standard errors).

### Check: what "own" familiarity means

Replaying one match (Team v Chelsea, seed 1) with the saved tactic, Tiki-Taka and Wing Play, and dumping every
starter's effectiveness record, gives **identical records for all three tactics**. The averages are training 43.6,
exposure 37.3, team complexity 78, role complexity 66.7 and tactical ability 61.1. The saved match carries the
records, and the engine does not rebuild them when the tactic changes. So:

- **"own"** means every tactic is played with the squad's current STORMBRINGER familiarity, including its
  complexity of 78. That is a like-for-like comparison of the tactics themselves, as if each were equally learned.
- **"low"** means every tactic at the same low familiarity.
- **Neither column includes differences in tactic complexity.** A simpler tactic would have a lower complexity value
  in the game; here every tactic carries STORMBRINGER's. ([Study 3](03-tactical-familiarity.md) found no clear effect
  of complexity held during the match, so this probably matters little.)

## Caveats

- **"own" is not what the squad would have with a new tactic.** It is the current tactic's familiarity applied to
  every tactic (see the check above). A tactic the team switched to would start lower, so the "low" column is closer to
  the first weeks with a new tactic.
- **Lineups are fixed.** Every tactic uses the saved XI in their saved slots. A tactic with a different shape (3-4-3,
  4-1-4-1) would normally be played with a different selection, so tactics far from the team's shape are at a
  disadvantage here.
- **Only 13 of the 25 files.** The 12 rejected ones (mostly made for FM24/FM26) would need re-exporting from FM27.

## Reproduce

```sh
.venv/bin/python port/validation/study6_tactics.py build port/mac_host/runs/study6 port/mac_host/runs/attr_real_2701 \
  <presets.jsonl> "$HOME/Library/Application Support/Sports Interactive/Football Manager 27/tactics"
FM27_STUDY_HOST=<frozen host> .venv/bin/python port/validation/overnight.py run port/mac_host/runs/study6 6
.venv/bin/python port/validation/study6_tactics.py analyse port/mac_host/runs/study6
```
