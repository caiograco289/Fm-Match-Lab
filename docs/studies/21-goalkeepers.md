# Study 21: what makes a goalkeeper good?

**Status:** done (13 November, 7,600 matches in Study 21, 2,400 in the follow-up 21b). **[Study 13b](13b-value-by-position-random.md)
resolves the single attributes:** Agility and Reflexes each save about 0.8-0.9 goals a season per level (t −19 to
−23); Positioning and Concentration, the leads below, are close to zero. Goalkeepers are rarely tested
on FM Arena, and players argue about which of their attributes matter: Reflexes, One on Ones, Handling? Which
attributes of the starting keeper change results, and how?

**In short:**
- **No single goalkeeper attribute +5 has a clear effect.** Positioning (+0.25 points per game, t 2.7) and
  Concentration (+0.18, t 2.0) lead, but neither is established.
- **Together they do:** all ten goalkeeping attributes +5 raise the save rate from 75% to 80%. The keeper concedes
  0.18 fewer goals per game at the same xG, worth +0.26 points (t 2.9), about 10 points a season. The single effects
  add up to about this: each is real but too small to see alone.
- **The keeper's goalkeeper position rating matters far more.** At 15 instead of natural (20), his save rate falls
  to 71%; at 10, to 60%, conceding 0.69 more goals per game (t 8.4) and losing 0.53 points.
- **Several attributes are hardly read at all** in these matches: One on Ones, Jumping Reach, Tendency to Punch,
  Handling and First Touch leave most matches exactly as they were.
- **Expected points miss all of this.** Shot-stopping changes goals, not chances, so tables ranked by xG or xPts
  (including Study 1) undervalue goalkeepers.

## Design

- **Neutral ground,** as in the other roadmap studies:
  - The synthetic Premier League middle-eight squad on both sides, Gegenpress.
  - Tactical familiarity held at 80.
  - Four preset opponents, home and away.
  - Two template matches between other clubs.
- **Study 21:** eighteen attributes of the starting goalkeeper, each +5 alone.
  - **Ten goalkeeping attributes:** Reflexes, Agility, Aerial Reach, Handling, Command of Area, Communication, One on
    Ones, Rushing Out, Kicking, Throwing.
  - **Tendency to Punch.**
  - **Seven general attributes:** First Touch, Passing, Positioning, Concentration, Decisions, Anticipation, Jumping
    Reach.
- **Study 21b:** the keeper as a whole.
  - All ten goalkeeping attributes +5 together.
  - All eighteen +5 together.
  - Reflexes and Agility +5 together.
  - His goalkeeper position rating at 15 and at 10 instead of natural (20).
- **Paired:** 50 seeds, giving 400 pairs per condition, each against the same matches unchanged.
- **The keeper's values:** mostly 10-18, so +5 is capped at 20 for his best attributes (Aerial Reach and Jumping
  Reach start near 18 for one keeper).

## One attribute at a time

Per game against the same matches unchanged; t in brackets (|t| ≥ 4 established, 3-4 likely, below that unconfirmed).
"Matches unchanged" counts how many of the 400 replay exactly as without the change: a high count means the engine
rarely reads the attribute.

| Attribute +5 | Points | xPts | Goals against | Goals against minus xG against | Save rate | Matches unchanged |
|---|---|---|---|---|---|---|
| Positioning | +0.25 (+2.7) | +0.07 (+1.7) | −0.14 (−1.9) | −0.06 | 77.1% | 0 |
| Concentration | +0.18 (+2.0) | +0.08 (+1.9) | −0.11 (−1.6) | −0.03 | 76.3% | 0 |
| Agility | +0.16 (+1.8) | +0.05 (+1.2) | −0.05 (−0.7) | −0.03 | 75.3% | 0 |
| Throwing | +0.10 (+1.2) | −0.00 (−0.1) | −0.02 (−0.3) | −0.03 | 76.0% | 1 |
| Decisions | +0.10 (+1.2) | +0.02 (+0.5) | −0.07 (−1.2) | −0.02 | 76.2% | 11 |
| Reflexes | +0.08 (+0.9) | +0.02 (+0.5) | −0.06 (−0.8) | −0.02 | 76.2% | 2 |
| Rushing Out | +0.06 (+0.8) | +0.01 (+0.5) | +0.02 (+0.3) | +0.06 | 74.4% | 51 |
| Kicking | +0.06 (+0.7) | −0.01 (−0.4) | −0.03 (−0.4) | −0.01 | 74.9% | 34 |
| Anticipation | +0.06 (+0.6) | +0.01 (+0.2) | +0.03 (+0.3) | +0.07 | 73.9% | 0 |
| Aerial Reach | +0.05 (+0.7) | +0.00 (+0.1) | −0.04 (−0.9) | −0.02 | 76.1% | 77 |
| Passing | +0.04 (+0.5) | −0.02 (−0.5) | −0.05 (−0.8) | −0.05 | 75.8% | 1 |
| First Touch | +0.03 (+0.9) | −0.01 (−0.5) | +0.01 (+0.3) | −0.01 | 75.4% | 317 |
| Command of Area | +0.01 (+0.1) | +0.03 (+0.7) | +0.06 (+0.9) | +0.05 | 73.7% | 1 |
| Communication | +0.01 (+0.2) | −0.00 (−0.2) | +0.00 (+0.0) | −0.00 | 75.3% | 58 |
| Tendency to Punch | +0.01 (+0.6) | −0.00 (−0.1) | +0.02 (+1.0) | +0.02 | 75.1% | 348 |
| Handling | −0.01 (−0.4) | −0.01 (−1.2) | −0.01 (−0.5) | −0.01 | 75.3% | 334 |
| Jumping Reach | −0.01 (−0.6) | +0.00 (+0.5) | −0.01 (−0.5) | −0.01 | 75.5% | 359 |
| One on Ones | −0.03 (−1.6) | −0.00 (−0.1) | +0.01 (+0.9) | +0.01 | 75.0% | 383 |

Unchanged: 1.48 points per game, 1.18 goals and 1.21 xG against, 4.75 shots on target against, save rate 75.3%.

- **Nothing passes |t| 3.** With eighteen conditions, a |t| of 2-3 can appear by chance, so Positioning and
  Concentration are leads.
- **The leaders act at both ends.** Positioning and Concentration lower goals and shots against a little, but also
  come with more goals for. A keeper who reads the game well may restart play better, as Throwing's +0.16 goals for
  (t 2.1) also hints.
- **Read in every match:** Reflexes, Agility, Positioning, Concentration, Anticipation, Command of Area, Throwing,
  Passing and Decisions change how nearly every match unfolds, even when results barely move.
- **Read only now and then:**
  - **Rarely:** One on Ones (383 of 400 matches unchanged), Jumping Reach (359), Tendency to Punch (348), Handling
    (334) and First Touch (317). These are probably used only in particular situations (a one-on-one, a cross caught
    or punched, a back-pass), which come up in a minority of matches.
  - **Partly:** Aerial Reach, Communication, Rushing Out and Kicking leave 34-77 matches unchanged.

## The keeper as a whole (21b)

| Change to the goalkeeper | Points | xPts | Goals against | Goals against minus xG against | Saves | Save rate |
|---|---|---|---|---|---|---|
| All ten goalkeeping attributes +5 | **+0.26 (+2.9)** | +0.04 (+1.0) | −0.18 (−2.7) | −0.16 (−2.7) | +0.26 | **79.5%** |
| All eighteen attributes +5 | **+0.31 (+3.4)** | +0.03 (+0.8) | −0.18 (−2.7) | −0.14 (−2.3) | +0.40 | **80.0%** |
| Reflexes and Agility +5 | +0.13 (+1.4) | −0.00 (−0.0) | −0.14 (−1.9) | −0.14 (−2.2) | +0.24 | 78.6% |
| Goalkeeper rating 15 | −0.06 (−0.6) | +0.03 (+0.9) | +0.18 (+2.4) | +0.18 (+2.8) | −0.30 | 70.7% |
| Goalkeeper rating 10 | **−0.53 (−5.9)** | −0.12 (−3.1) | **+0.69 (+8.4)** | **+0.62 (+8.3)** | −0.81 | **59.7%** |

- **Better goalkeeping attributes together:** the save rate rises by four to five points, the keeper concedes about
  0.18 fewer goals per game, and the side gains about 0.26-0.31 points per game. The xG he faces does not change.
- **The parts add up.** The ten goalkeeping attributes alone lower goals against by 0.12 per game in total, against
  0.18 together; Reflexes and Agility alone by 0.11, against 0.14 together. There's no sign of synergy: each
  attribute adds a little, too little to see alone with 400 pairs.
- **The position rating is the bigger lever.**
  - A keeper at 15 instead of natural concedes 0.18 more goals per game, about as much as five attribute points on
    every goalkeeping attribute.
  - At 10 he saves 60% of shots on target instead of 75%: +0.69 goals against per game, −0.53 points, about 20 points
    a season. This repeats Study 17b's result (+0.70 goals against) on new seeds.
- **Not shots, saves.** In every condition the shots on target the keeper faces barely move (within ±0.2 per game).
  Everything happens at the save.

## What this means for picking a goalkeeper

- **Play a natural goalkeeper.** A keeper who is only accomplished in goal (rating 15) concedes about as many extra
  goals as a full +5 on his goalkeeping attributes saves; one at 10 concedes nearly four times as many.
- **Overall quality matters more than any one attribute.** No single goalkeeping attribute stands out; a keeper who is
  better across the board is worth about 10 points a season per +5.
- **Don't pay for One on Ones, Handling or Tendency to Punch** on this evidence: the engine rarely reads them in these
  matches, and they change nothing measurable when it does.
- **Positioning and Concentration** are the best candidates for a single attribute that matters. They need a rerun to
  confirm.

## Caveats

- **Expected points don't see keepers.** xPts is computed from the xG of shots, before the keeper acts. Points and
  goals against are the measures here, and they are noisier.
- **One squad, one style.** Premier League middle eight, Gegenpress; the keeper faces about 4.75 shots on target per
  game. A side that concedes more shots would gain more from a better keeper.
- **+5 is capped at 20.** For the attributes the keeper already has near 18, +5 is a smaller change.
- **Sweeping and distribution** may matter more in other styles (a high line, playing out from the back).
- **Within a match.** Injuries, form and development over a season are not measured.

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 21 runs/study21           # and 21b for the follow-up
.venv/bin/python port/validation/neutral_study.py pilot runs/study21 --workers 7
.venv/bin/python port/validation/neutral_study.py run runs/study21 --workers 7      # about 1 hour with 7 workers
.venv/bin/python port/validation/neutral_study.py report runs/study21
```

The specifications (`s21`, `s21b`) are in `port/validation/roadmap_studies.py`. Save rate is saves divided by shots on
target against over all matches; "matches unchanged" compares each match's score and xG with the unchanged one.
