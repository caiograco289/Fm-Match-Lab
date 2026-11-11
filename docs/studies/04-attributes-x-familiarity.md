# Study 4: do attributes matter more with a familiar tactic?

**Status:** done (10 November, 7,800 matches).

## Design

- The six attributes with the largest xGD effects in [Study 1](01-attribute-values.md): Pace, Acceleration, Jumping
  Reach, Stamina, Anticipation and Dribbling.
- Each is moved by −5 and +5 in-game points for the team's whole squad (as in Study 1), at two familiarity levels:
  the eight tactical areas of every team player's effectiveness record held at **20 (low)** or **80 (high)**
  (all 24 area bytes, as in [Study 3](03-tactical-familiarity.md)).
- 10 real matches × seeds 1-30 = 300 pairs per cell. Effect = (+5 − −5) / 2, i.e. per 5 in-game points.
- **Interaction** = effect at high familiarity − effect at low, paired on the same matches and seeds. Positive means
  the attribute is worth more with a familiar tactic.

## Results

Per +5 in-game points for the squad (t in brackets):

| Attribute (+5 for the squad) | at low familiarity: ppg | xGD | at high familiarity: ppg | xGD | Interaction: ppg | xGD |
|---|---|---|---|---|---|---|
| Pace | +0.39 (+8.0) | +0.49 (+11.6) | +0.36 (+7.8) | +0.56 (+13.5) | -0.03 (-0.5) | +0.07 (+1.2) |
| Acceleration | +0.30 (+6.6) | +0.44 (+10.2) | +0.25 (+5.0) | +0.45 (+10.4) | -0.04 (-0.7) | +0.01 (+0.1) |
| Jumping Reach | +0.19 (+3.9) | +0.30 (+6.7) | +0.10 (+2.0) | +0.33 (+7.6) | -0.09 (-1.3) | +0.03 (+0.6) |
| Stamina | +0.24 (+5.1) | +0.24 (+5.9) | +0.18 (+3.8) | +0.38 (+8.5) | -0.05 (-0.8) | +0.14 (+2.2) |
| Anticipation | +0.09 (+1.8) | +0.26 (+6.5) | +0.11 (+2.4) | +0.28 (+6.3) | +0.03 (+0.4) | +0.02 (+0.3) |
| Dribbling | +0.08 (+1.6) | +0.14 (+3.5) | -0.05 (-1.2) | +0.12 (+2.8) | -0.13 (-2.0) | -0.02 (-0.4) |

Familiarity on its own (high against low, attributes unchanged): **+0.52 points per game (t 5.3), +0.54 xG
difference (t 6.4).**

## What it means

1. **No clear interaction.** Every attribute is worth about the same at low and at high familiarity. Five of the six
   interactions are under 0.07 xGD with |t| ≤ 1.2. Stamina is the only hint (+0.14 xGD, t 2.2), and with six tests
   one result near t = 2 is expected by chance.
2. **Attributes and familiarity add up.** Good players don't need a familiar tactic to show it, and quality doesn't
   make up for an unfamiliar tactic either. Each counts on its own.
3. **The size of familiarity:** going from 20 to 80 in every area is worth about +0.5 points per game. That's similar
   to +7 Pace across the whole squad, or about 4 in-game points of both Pace and Acceleration.
4. The attribute effects at both levels agree with Study 1 (Pace +0.49 to +0.56 xGD per 5 points here, +0.51 in
   Study 1), which supports both results.

## Caveats

- Two familiarity levels only, both fixed for every player and area. A real squad has a mix.
- Six attributes. Attributes with small main effects (Passing, Technique) were not tested; a small interaction
  would be hard to see for them anyway.
- 300 pairs per cell. An interaction below about 0.15 xGD would not be detected.

## Reproduce

```sh
.venv/bin/python port/validation/study4_interaction.py build port/mac_host/runs/study4 port/mac_host/runs/attr_real_2701 \
  Pace,Acceleration,JumpingReach,Stamina,Anticipation,Dribbling
FM27_STUDY_HOST=<frozen host> .venv/bin/python port/validation/overnight.py run port/mac_host/runs/study4 6
.venv/bin/python port/validation/study4_interaction.py analyse port/mac_host/runs/study4
```
