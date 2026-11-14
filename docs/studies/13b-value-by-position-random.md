# Study 13b: what is an attribute worth in each position? Random configurations

**Status:** Gegenpress done (14 November, 50,000 matches); Catenaccio running. Study 13 changed one attribute in one
position group at a time and found no clear position-specific values. A test posted on FM Arena (Purity, 200,000
matches on their own 3-4-2-1) used a different design and did find them. Is the difference the design, the tactic,
or chance? And can the same design finally measure single goalkeeper attributes, which Study 21 could not?

**In short:**
- **Positions do differ.** With every attribute of every starter changed at random in every match, 50,000 matches
  measure all 48 outfield attributes in five positions, and the goalkeeper's, to about ±0.03 expected points a season
  per level. Ten attributes differ between positions beyond chance (2.4 expected); Jumping Reach, Pace, Balance and
  Acceleration clearly (p < 0.005).
- **The same few attributes lead everywhere:** Acceleration, Pace, Jumping Reach, Stamina, Anticipation. What changes
  with the position is how much, and whether it works in attack or defence.
- **Jumping Reach is a centre-back's and a striker's attribute** (+0.32 and +0.19 xPts a season per level), much less a
  defensive midfielder's (+0.06). Balance also pays for centre-backs and strikers, hardly elsewhere.
- **Goalkeepers: Agility and Reflexes matter, each on its own.** +1 level of either saves about 0.8-0.9 goals a season
  (t −19 to −23), worth about half a point; +5 of each is worth about 5 points a season together. The xG the keeper
  faces doesn't change: it is all at the save, so xPts tables miss it.
- **This agrees with Study 13 and with Purity's table.** Study 13's numbers fit these within its noise; it lacked the
  precision to separate positions. Purity's goal-difference weights correlate 0.80 with ours over 240 cells; their
  striker values are about twice ours, plausibly because their side has one striker and Gegenpress has two.

## Design

- **Random configurations,** as in Purity's test: in each match, every attribute of every starter of the tested side
  moves by +5 or −5 at random (clamped to 1-20), independently. One regression on the per-position sums of the changes
  then estimates every attribute in every position at once, from the same matches.
  - **Fields:** 52 attributes (all except the feet) and the seven personality attributes. The eleven goalkeeping
    attributes are changed for the goalkeeper only.
  - **Positions:** goalkeeper; full-backs (DL, DR); centre-backs (DCL, DCR); defensive midfielders (DML, DMR); wide
    attacking midfielders (AML, AMR); strikers (STL, STR). Each estimate is for **one** player of the group.
- **Neutral ground,** as in Study 13: the synthetic Premier League middle-eight squad on both sides, Gegenpress for the
  tested side, tactical familiarity held at 80, four preset opponents home and away, two template matches between
  other clubs: 16 settings, each with its own constant in the regression.
- **50,000 matches,** one configuration each, on its own seed.
- **Checks before the run:** on fabricated results with known effects the analysis recovered them (Pace for the
  striker 0.0085 for a true 0.010, goalkeeper Reflexes on xG against −0.0073 for −0.008); 4.5% false |t| > 2, 1 false
  confirmation in 292, 6.5% false position differences. A 320-match pilot played every configuration with every change
  accepted by the game's validator.
- **Confirmed** (*) means |t| > 2 in both random halves of the configurations, with the same sign.

**Units:** per season (38 games), for +1 level in one player of the position. Multiply by 5 for a +5 change, by the
number of players for a whole group.

## Expected points by position

The attributes with any effect above ±0.04; the other 34 outfield attributes are within ±0.04 in every position and
mostly within ±0.02. Typical 95% margin ±0.03.

| Attribute | Team (per player) | ST | AM | DM | FB | CB | Positions differ? (p) |
|---|---|---|---|---|---|---|---|
| Acceleration | +0.18 | +0.20* | +0.15* | +0.15* | +0.17* | +0.20* | 0.003 |
| Pace | +0.16 | +0.21* | +0.17* | +0.12* | +0.17* | +0.13* | < 0.001 |
| Jumping Reach | +0.13 | +0.19* | +0.10* | +0.06 | +0.08* | **+0.32*** | < 0.001 |
| Stamina | +0.09 | +0.07* | +0.10* | +0.09* | +0.10* | +0.08* | 0.50 |
| Anticipation | +0.08 | +0.10* | +0.07* | +0.07* | +0.07* | +0.10* | 0.20 |
| Balance | +0.06 | +0.09* | +0.03 | +0.04 | +0.06* | +0.10* | < 0.001 |
| Dribbling | +0.05 | +0.05* | +0.07* | +0.02 | +0.08* | +0.03 | 0.004 |
| Concentration | +0.05 | +0.06* | +0.03 | +0.02 | +0.07* | +0.05* | 0.08 |
| Vision | +0.02 | +0.02 | +0.01 | +0.05* | −0.00 | +0.03 | 0.08 |
| Strength | +0.03 | +0.03 | +0.02 | +0.04 | +0.02 | +0.04 | 0.81 |

- **Ten of 48 attributes differ between positions at p < 0.05** (2.4 expected by chance); Jumping Reach, Pace, Balance
  (p < 0.001) and Acceleration (0.003) clearly.
- **Strikers gain most** from Pace and Acceleration, then Jumping Reach and Balance; **centre-backs** from Jumping Reach, Acceleration,
  Balance and Anticipation; **full-backs** from Pace, Acceleration, Dribbling and Concentration; **defensive
  midfielders** least from almost everything (Vision is the only attribute where they lead).
- **Technical and mental attributes show almost nothing** in any position: Passing, Technique, Tackling, Marking,
  Positioning, Crossing, Decisions, Composure, First Touch, Off the Ball, Flair are within ±0.04 everywhere.

## How each position's attributes work

xG for and against per season, +1 level for one player (t in brackets):

| | Striker | Wide attacker | Defensive midfielder | Full-back | Centre-back |
|---|---|---|---|---|---|
| Pace | xG for +0.35 (+22) | +0.18 for, −0.10 against | −0.16 against (−10) | −0.21 against (−14) | −0.18 against (−12) |
| Acceleration | xG for +0.28 (+17) | +0.17 for, −0.10 against | −0.16 against (−10) | +0.13 for, −0.17 against | −0.30 against (−20) |
| Jumping Reach | xG for +0.23 (+14) | +0.12 for (+7) | −0.08 against (−5) | −0.13 against (−8) | **+0.25 for, −0.30 against** |
| Stamina | xG for +0.13 (+8) | +0.10 for, −0.07 against | −0.14 against (−9) | −0.12 against (−8) | −0.10 against (−6) |
| Balance | xG for +0.14 (+9) | nothing | nothing | −0.07 against (−4) | −0.14 against (−9) |

- **The same attribute does different jobs.** For a striker, speed and jumping create chances; for a defender they
  prevent them. A centre-back's Jumping Reach does both (set pieces at both ends).
- **Finishing and Strength work through conversion,** not chances, so expected points don't show them. Goals for, per
  level:
  - Finishing: striker +0.21 (t 7.5), wide attacker +0.09 (t 3.2), at the same xG.
  - Strength: striker +0.18, wide attacker +0.19 (t 6-7), against +0.06 xG.

## Goal difference

Goals for minus against per season, per level for one player; typical 95% margin ±0.08. Points follow the same
pattern (about 0.6 points per goal) with twice the noise of expected points.

| Attribute | ST | AM | DM | FB | CB |
|---|---|---|---|---|---|
| Acceleration | +0.49* | +0.24* | +0.27* | +0.29* | +0.41* |
| Pace | +0.45* | +0.27* | +0.26* | +0.36* | +0.31* |
| Jumping Reach | +0.34* | +0.21* | +0.09 | +0.11 | +0.44* |
| Stamina | +0.15* | +0.16* | +0.20* | +0.25* | +0.20* |
| Balance | +0.21* | +0.00 | +0.06 | +0.09 | +0.24* |
| Strength | +0.16* | +0.14* | +0.15* | +0.09 | +0.17* |
| Finishing | +0.21* | +0.06 | +0.04 | +0.00 | +0.04 |
| Anticipation | +0.13 | +0.11 | +0.10 | +0.14 | +0.15 |
| Concentration | +0.08 | +0.06 | +0.08 | +0.19* | +0.12 |

## The goalkeeper

Per season, +1 level of the goalkeeper's attribute; t in brackets. The rest are within ±0.1 goals and |t| < 2.

| Attribute | Goals against | xG against | Points | Expected points |
|---|---|---|---|---|
| Agility | **−0.93 (−23)** | −0.01 (−0.3) | **+0.58 (+13.5)** | −0.02 |
| Reflexes | **−0.76 (−19)** | +0.01 (+0.4) | **+0.50 (+11.6)** | −0.01 |
| Aerial Reach | −0.23 (−4.0) | −0.06 (−1.9) | +0.16 (+2.5) | +0.03 |
| Acceleration | −0.15 (−3.8) | −0.21 (−9.8) | +0.16 (+3.7) | +0.15 |
| Determination | −0.13 (−3.2) | −0.04 (−1.7) | +0.12 (+2.8) | +0.03 |
| Handling | −0.11 (−2.7) | −0.09 (−4.2) | +0.05 (+1.2) | +0.06 |
| Concentration | −0.08 (−1.9) | −0.01 | +0.07 | +0.02 |
| Positioning | −0.02 | −0.04 | +0.05 | +0.02 |
| One on Ones | −0.00 | +0.02 | +0.06 | +0.02 |

- **Agility and Reflexes are shot-stopping:** goals against fall, xG against doesn't move. +5 in both saves about 8.5
  goals and is worth about 5 points a season.
- **Acceleration and Handling act on the chances themselves:** they lower the xG the keeper faces (a keeper who comes
  off his line sooner; fewer rebounds), worth less in goals.
- **Study 21's leads don't hold:** Positioning and Concentration are close to zero here.
- **Consistent with Study 21.** There, Reflexes and Agility +5 alone lowered goals against by 0.06 and 0.05 per game
  (t below 1), and 0.14 together. Here +5 is 0.10 and 0.12 per game each: within Study 21's error, which was about
  ±0.15. Study 21 was right that the effects are real but too small for 400 pairs; 50,000 random configurations
  resolve them.

## Against Study 13 and Purity's test

- **Study 13** (+5 for the two players of a group, 320 pairs each): its 40 cells match this study's predictions within
  noise (chi-square 36 on 40). Its "no position differences" was a lack of power: its margin, ±0.08 xPts per game,
  is about the size of the largest differences here (Jumping Reach for two centre-backs +0.08 per game, for two
  defensive midfielders +0.02).
- **Study 13's "the first players are worth more" (Jumping Reach)** is much weaker here. With ten players each at +5
  or −5, a pairwise interaction would show as diminishing returns: −0.03 xPts a season per pair of +5 players (t −2.1),
  about a fifth of the main effect when all ten are +5. Study 13's first three players included a centre-back and a
  striker, the two positions where Jumping Reach is worth most: this study predicts those three give 44% of the team's
  gain, against Study 13's 64% (t about 2 there). Position, not diminishing returns, explains most of that finding.
- **Purity's test** (Brentford's 3-4-2-1, real players and fixtures, goals per season):
  - The pattern agrees: correlation 0.80 over 240 attribute × position cells; the same top five; the same positions
    for Jumping Reach (striker and centre-back, little for defensive midfielders); Finishing only for forwards;
    technical attributes near zero.
  - **The size differs for the striker:** ours are about half theirs (Pace +0.45 against +0.90, Jumping Reach +0.34
    against +0.73). A lone striker does the work Gegenpress's two share. Their centre-backs (three) and our
    centre-backs (two) are close; other positions are within about 30%.
  - **The goalkeeper** was not covered in their test.

## What this means

- **Recruit by position for the physical attributes:** Pace and Acceleration everywhere; Jumping Reach and Balance for
  centre-backs and strikers; Stamina for full-backs and midfielders; Finishing and Strength for forwards (goals, not
  xG).
- **Goalkeepers: Agility and Reflexes first,** then Aerial Reach. Don't pay for One on Ones, Positioning or
  Concentration on this evidence.
- **Most technical and mental attributes are worth little anywhere** in these matches, as in Studies 1 and 13.

## Caveats

- **One style so far** (Gegenpress, two strikers); the Catenaccio run will show how much the weights depend on the
  tactic and the formation.
- **One synthetic squad,** levels mostly 6-18. Each estimate is the average slope over a ±5 range; a two-level design
  can't show curvature within it (Study 12 measured that).
- **Single matches:** no injuries, fitness or form over a season, so Natural Fitness and Injury Proneness can't show.
- **Personality attributes** are changed as the match sees them; their effects (Pressure, Important Matches,
  Determination) are small and mostly unconfirmed.

## Reproduce

```sh
.venv/bin/python port/validation/random_study.py build runs/random/gegenpress --configs 50000 --style Gegenpress
.venv/bin/python port/validation/random_study.py pilot runs/random/gegenpress --workers 7
.venv/bin/python port/validation/random_study.py run runs/random/gegenpress --workers 7     # about 10 hours with 7 workers
.venv/bin/python port/validation/random_study.py report runs/random/gegenpress
```

Regression: the outcome on the per-position sums of the level changes (one column per attribute and position), with a
constant per setting; the team model has one column per attribute for the ten outfield players. Position differences:
a Wald test that the five outfield coefficients are equal (4 degrees of freedom).
