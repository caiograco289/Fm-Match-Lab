# Study 2: real matches against "everyone 12" tests

**Status:** done (11 November, 65,400 matches).

## The question

Earlier tests, before the studies, used the sample match that came with the original tool: two strong sides,
every attribute levelled to 12, natural in every position. They found that physical attributes dominate and that
technical and mental ones barely register. Is that a property of the engine, or of the test?

## Design

Three arms. Each moves one attribute by −5 and +5 in-game points for one side's whole squad and reports the effect
of +5 points, paired by match and seed.

| Arm | Squads | Match context | Pairs per attribute |
|---|---|---|---|
| A (= [Study 1](01-attribute-values.md)) | real players of both sides | the team's 10 real matches (real tactics, start states, opponents) | 300 |
| B | both squads levelled: every attribute 12, positions as saved | the same 10 real matches | 300 |
| C | both squads levelled: every attribute 12, natural in every position, 180 cm / 70 kg | the old sample match, the assistant managing both sides | 300 (seeds 1-300) |

- A against B isolates **squad realism** (stars and weak spots, real attribute profiles).
- B against C isolates **match context** (real tactics, opponents and start states against the sample's).

## Results

**Overall agreement** of the 54 per-attribute effects (correlation):

| | xG difference | Points per game |
|---|---|---|
| A (real) vs B (levelled, real matches) | **0.88** | 0.79 |
| A (real) vs C (levelled sample) | 0.77 | 0.58 |
| B vs C | 0.70 | 0.52 |

**Size:** the eight largest effects from Study 1 add up to +2.5 xG difference per 5 points in A, +2.7 in B and only
+1.0 in C. Across all attributes, C's effects are about 40% of A's.

Per +5 in-game points for the whole squad (t in brackets), sorted by arm A:

| Attribute | A real: xGD | B levelled, real matches: xGD | C levelled sample: xGD | A: ppg | B: ppg | C: ppg |
|---|---|---|---|---|---|---|
| Pace | +0.51 (+11.1) | +0.69 (+15.3) | +0.15 (+7.4) | +0.35 (+7.5) | +0.46 (+8.7) | +0.12 (+2.8) |
| Acceleration | +0.47 (+10.8) | +0.44 (+10.5) | +0.26 (+13.2) | +0.33 (+6.5) | +0.31 (+6.1) | +0.19 (+5.0) |
| Jumping Reach | +0.34 (+8.2) | +0.28 (+6.9) | +0.32 (+14.4) | +0.16 (+3.4) | +0.18 (+3.4) | +0.28 (+7.4) |
| Stamina | +0.30 (+7.3) | +0.42 (+9.4) | +0.05 (+2.4) | +0.18 (+3.7) | +0.39 (+7.2) | +0.01 (+0.2) |
| Anticipation | +0.24 (+6.1) | +0.24 (+5.9) | +0.05 (+2.6) | +0.12 (+2.5) | +0.15 (+2.9) | +0.01 (+0.3) |
| Dribbling | +0.24 (+5.7) | +0.22 (+5.0) | +0.09 (+4.9) | +0.17 (+3.5) | +0.18 (+3.5) | +0.03 (+0.8) |
| Concentration | +0.22 (+4.9) | +0.22 (+5.5) | +0.02 (+1.0) | +0.09 (+1.8) | +0.13 (+2.4) | +0.01 (+0.3) |
| Balance | +0.16 (+4.0) | +0.19 (+4.7) | +0.05 (+2.6) | -0.02 (-0.4) | +0.07 (+1.4) | +0.06 (+1.5) |
| Composure | +0.14 (+3.0) | -0.03 (-0.8) | +0.01 (+0.3) | +0.08 (+1.6) | +0.01 (+0.1) | -0.01 (-0.1) |
| Work Rate | +0.10 (+2.6) | +0.02 (+0.5) | +0.01 (+0.7) | +0.12 (+2.5) | +0.04 (+0.8) | +0.04 (+1.1) |
| Vision | +0.09 (+2.1) | +0.05 (+1.3) | +0.00 (+0.2) | +0.08 (+1.6) | +0.07 (+1.3) | +0.06 (+1.5) |
| Marking | +0.07 (+1.7) | +0.00 (+0.0) | +0.01 (+0.7) | +0.01 (+0.2) | -0.05 (-0.9) | +0.04 (+1.1) |
| First Touch | +0.07 (+1.6) | +0.03 (+0.6) | -0.01 (-0.5) | +0.06 (+1.2) | -0.10 (-1.8) | -0.00 (-0.0) |
| Command Of Area | +0.06 (+1.5) | +0.00 (+0.0) | +0.01 (+0.5) | -0.03 (-0.7) | +0.05 (+0.9) | -0.03 (-0.9) |
| Passing | +0.06 (+1.4) | +0.01 (+0.2) | +0.02 (+1.2) | +0.03 (+0.5) | +0.03 (+0.6) | -0.01 (-0.2) |
| Handling | +0.04 (+1.4) | +0.03 (+1.2) | +0.01 (+0.8) | +0.01 (+0.3) | +0.04 (+1.0) | -0.00 (-0.1) |
| Corners | +0.03 (+0.7) | -0.04 (-1.1) | +0.02 (+1.1) | +0.00 (+0.0) | +0.02 (+0.3) | -0.01 (-0.4) |
| Strength | +0.03 (+0.7) | +0.13 (+3.0) | +0.03 (+1.3) | +0.04 (+0.8) | +0.21 (+3.9) | +0.02 (+0.6) |
| Important Matches | +0.03 (+0.6) | +0.09 (+2.0) | +0.06 (+3.3) | +0.00 (+0.1) | +0.09 (+1.6) | -0.01 (-0.2) |
| Throwing | +0.02 (+0.6) | +0.09 (+2.1) | +0.02 (+0.9) | -0.01 (-0.3) | +0.02 (+0.5) | +0.04 (+1.0) |
| Communication | +0.01 (+0.3) | -0.02 (-0.6) | +0.01 (+0.7) | +0.08 (+1.7) | +0.04 (+0.8) | +0.02 (+0.5) |
| Long Throws | +0.01 (+0.3) | -0.04 (-0.9) | +0.02 (+1.3) | +0.03 (+0.8) | +0.00 (+0.0) | +0.04 (+1.0) |
| Leadership | +0.01 (+0.6) | +0.00 (+0.0) | +0.00 (+0.0) | +0.01 (+0.5) | +0.00 (+0.0) | +0.00 (+0.0) |
| One On Ones | +0.01 (+0.8) | +0.03 (+2.5) | -0.00 (-0.2) | -0.01 (-0.8) | +0.03 (+1.7) | -0.01 (-0.2) |
| Decisions | +0.01 (+0.2) | +0.05 (+1.2) | -0.00 (-0.1) | -0.02 (-0.4) | +0.03 (+0.5) | -0.05 (-1.3) |
| Aggression | +0.01 (+0.2) | -0.02 (-0.5) | -0.00 (-0.2) | -0.04 (-0.9) | -0.09 (-1.6) | +0.00 (+0.1) |
| Technique | +0.01 (+0.2) | -0.01 (-0.2) | +0.02 (+0.9) | -0.04 (-0.7) | +0.04 (+0.7) | -0.02 (-0.4) |
| Penalty Taking | +0.00 (+0.2) | +0.00 (+0.1) | +0.00 (+1.2) | -0.00 (-0.6) | +0.01 (+0.7) | +0.01 (+1.5) |
| Natural Fitness | +0.00 (+0.0) | +0.00 (+0.0) | +0.00 (+0.0) | +0.00 (+0.0) | +0.00 (+0.0) | +0.00 (+0.0) |
| Tendency To Punch | -0.00 (-0.2) | +0.00 (+0.3) | +0.01 (+0.8) | -0.03 (-1.1) | -0.01 (-0.2) | -0.01 (-0.6) |
| Versatility | -0.00 (-0.1) | -0.00 (-0.0) | +0.01 (+0.7) | +0.02 (+0.4) | +0.09 (+1.7) | +0.06 (+1.5) |
| Rushing Out | -0.01 (-0.2) | -0.04 (-1.2) | -0.01 (-1.0) | -0.03 (-0.7) | -0.07 (-1.5) | -0.04 (-2.0) |
| Dirtiness | -0.01 (-0.2) | -0.08 (-2.1) | -0.07 (-3.5) | -0.02 (-0.4) | -0.08 (-1.6) | -0.07 (-1.8) |
| Positioning | -0.01 (-0.3) | +0.02 (+0.4) | +0.03 (+2.0) | -0.03 (-0.6) | +0.02 (+0.4) | +0.03 (+0.7) |
| Determination | -0.01 (-0.3) | +0.06 (+1.4) | +0.01 (+0.3) | +0.05 (+1.2) | +0.03 (+0.5) | -0.01 (-0.2) |
| Tackling | -0.01 (-0.3) | +0.04 (+1.0) | +0.02 (+1.2) | -0.04 (-0.9) | +0.03 (+0.6) | +0.04 (+1.5) |
| Bravery | -0.01 (-0.4) | +0.02 (+0.4) | +0.03 (+1.8) | -0.03 (-0.6) | -0.05 (-1.0) | +0.03 (+0.7) |
| Left Foot | -0.02 (-0.4) | +0.03 (+0.8) | +0.01 (+0.3) | -0.01 (-0.2) | +0.07 (+1.3) | +0.10 (+2.8) |
| Teamwork | -0.02 (-0.4) | -0.05 (-1.1) | +0.02 (+1.1) | -0.01 (-0.2) | -0.07 (-1.3) | +0.03 (+0.6) |
| Injury Proneness | -0.02 (-0.7) | +0.01 (+0.3) | +0.00 (+0.1) | -0.02 (-0.9) | +0.02 (+0.6) | +0.00 (+0.0) |
| Finishing | -0.02 (-0.4) | +0.04 (+0.9) | -0.03 (-1.9) | +0.11 (+2.3) | +0.12 (+2.3) | +0.03 (+0.8) |
| Long Shots | -0.02 (-0.5) | +0.06 (+1.4) | -0.02 (-1.2) | +0.00 (+0.1) | +0.06 (+1.2) | -0.03 (-0.7) |
| Reflexes | -0.02 (-0.5) | +0.04 (+0.9) | +0.01 (+0.8) | +0.01 (+0.2) | +0.12 (+2.4) | +0.06 (+1.6) |
| Heading | -0.02 (-0.6) | -0.01 (-0.2) | -0.00 (-0.0) | +0.01 (+0.3) | +0.00 (+0.0) | -0.05 (-1.4) |
| Flair | -0.02 (-0.6) | +0.05 (+1.2) | +0.02 (+1.0) | +0.05 (+1.1) | -0.01 (-0.1) | +0.02 (+0.4) |
| Aerial Reach | -0.03 (-0.7) | +0.00 (+0.1) | -0.01 (-0.6) | -0.01 (-0.3) | +0.03 (+0.6) | -0.01 (-0.3) |
| Consistency | -0.03 (-0.8) | +0.05 (+1.3) | +0.00 (+0.0) | +0.03 (+0.6) | -0.01 (-0.2) | +0.00 (+0.0) |
| Right Foot | -0.03 (-0.8) | +0.07 (+1.5) | -0.01 (-0.5) | +0.06 (+1.2) | +0.10 (+1.9) | +0.00 (+0.0) |
| Free Kick Taking | -0.04 (-1.2) | +0.01 (+0.2) | +0.01 (+0.3) | +0.03 (+0.6) | +0.03 (+0.7) | +0.02 (+0.5) |
| Crossing | -0.05 (-1.1) | -0.00 (-0.1) | +0.01 (+0.3) | -0.06 (-1.1) | -0.02 (-0.4) | -0.02 (-0.5) |
| Eccentricity | -0.06 (-1.4) | -0.07 (-1.7) | -0.02 (-0.8) | +0.04 (+0.9) | +0.01 (+0.1) | -0.03 (-0.7) |
| Off The Ball | -0.06 (-1.4) | +0.03 (+0.7) | +0.01 (+0.3) | +0.01 (+0.3) | +0.07 (+1.3) | -0.03 (-0.7) |
| Agility | -0.06 (-1.5) | +0.09 (+2.3) | +0.01 (+0.7) | +0.08 (+1.6) | +0.20 (+3.8) | +0.10 (+2.5) |
| Kicking | -0.12 (-3.2) | +0.00 (+0.1) | +0.00 (+0.1) | -0.00 (-0.1) | +0.07 (+1.4) | +0.01 (+0.4) |

## What it means

1. **Levelling the squads changes little.** With every attribute at 12 but the real matches kept (B), the attribute
   values look much like those with the real squads (A): the same leaders (Pace, Acceleration, Stamina, Jumping
   Reach), the same second group (Anticipation, Dribbling, Concentration), and similar sizes.
2. **The match context changes a lot.** On the old sample match (C) every effect shrinks, and several vanish.
   Only Jumping Reach keeps its size.

### "Mental attributes barely matter" was a property of the test match

Before these studies, attributes were tested on the sample match that came with the original tool, with both teams
set to 12 in every attribute. There, raising physical attributes helped a lot and raising mental ones did almost
nothing, which led to the conclusion that the engine barely rewards mental attributes.

Study 2 repeats that test three ways (xG difference per +5 points for the whole squad):

| Attribute | A: real matches, real squads | B: real matches, every player 12 | C: the old sample match, every player 12 |
|---|---|---|---|
| Anticipation | +0.24 | +0.24 | +0.05 |
| Concentration | +0.22 | +0.22 | +0.02 |
| Stamina | +0.30 | +0.42 | +0.05 |
| Dribbling | +0.24 | +0.22 | +0.09 |
| Pace | +0.51 | +0.69 | +0.15 |

Only C reproduces the old result. In real matches the engine clearly rewards Anticipation and Concentration, and it
does so just as much when every player is levelled to 12 (B). So levelling the squads was not the cause: the
particular test match was.

What this does **not** say:

- **Not every mental attribute matters.** Decisions, Teamwork, Determination and Flair show no clear effect even in
  real matches. The accurate statement is: some mental attributes matter a lot in real matches, and the old test
  match hid that.
- **Why the sample match flattens them is unknown.** It differs from real matches in several ways at once: two
  strong teams, the same squad on both sides, the assistant managing both, and no real fitness, morale or tactical
  history. This study does not separate them.
- **All the real matches are one club's.** A dominant team might show a different pattern.

### More results

3. **Physical attributes still lead everywhere.** Pace and Acceleration are among the top three in all arms.
4. **A few effects need real squads.** Goalkeeper Kicking is negative only with real players (−0.12 xGD in A, 0.00
   in B and C), and Composure and Work Rate count only in A. Strength and Agility count only when every player is
   level (B: +0.21 and +0.20 points per game), perhaps because they decide duels between otherwise equal players.

**For your own tests:** test on real matches. A levelled squad is acceptable if you keep the real match (B gives
nearly the same answers as A), but a generic test match understates most attributes and misses some entirely.

## Caveats

- One club's matches for A and B; one sample match for C. C mixes several differences (stronger teams, the same
  squad on both sides, the assistant on both sides, no saved start states); this study doesn't separate them.
- Points per game agree less than xG difference across arms because they're noisier; the xGD columns are the
  better guide.

## Reproduce

```sh
FM27_SAVED_MATCHES=<folder with the saved matches> FM27_STUDY_TEAM="<team>" \
  .venv/bin/python port/validation/study2_levelled.py build port/mac_host/runs/study2
FM27_STUDY_HOST=<frozen host> .venv/bin/python port/validation/overnight.py run port/mac_host/runs/study2 6
.venv/bin/python port/validation/study2_levelled.py analyse port/mac_host/runs/study2
```
