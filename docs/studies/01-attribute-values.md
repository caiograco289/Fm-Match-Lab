# Study 1: what is each attribute worth?

**Status:** done (27.0.1, 10 November 2026; 32,700 matches). The same design on the 27.0 engine was run earlier.

## Design

- **Bases:** ten real matches of the team saved by FM27 (see [the common design](README.md#common-design)), replayed
  on the 27.0.1 engine with live in-match decisions (substitutions and assistant changes).
- **Change:** one attribute at a time, for the **team's whole squad** (starters and bench), by −5 and +5 in-game
  points (±25 stored), clamped to 1–20. The opponent is unchanged. The change is made before match preparation, so
  everything the engine derives from attributes (including the tactical-ability byte of the effectiveness record) is
  derived from the changed values.
- **Measure:** effect per in-game point = (result at +5 − result at −5) / 10, paired on the same match and seed; 10
  matches × 30 seeds = 300 pairs per attribute. 54 attributes × 2 + the unchanged baseline = 109 conditions.
- **Baseline (unchanged squads):** 1.79 points per game, xG 2.11 for and 1.45 against.

## Headline

1. **Pace and Acceleration are worth far more than anything else**: about +0.07 points per game and +0.10 xG
   difference per point. One point of Pace across the squad is worth about as much as 3–4 points of Dribbling.
2. A second group matters clearly: **Jumping Reach, Stamina, Anticipation, Dribbling and Concentration** (+0.04 to
   +0.07 xGD per point), then **Balance, Composure, Work Rate and Vision** (+0.02 to +0.03).
3. **Finishing does not create chances; it converts them.** It leaves xG unchanged but adds goals (+0.04 goals per
   point above xG) and points (+0.021 ppg per point, t 2.3). xGD is the wrong yardstick for Finishing.
4. Most technical attributes (Passing, Technique, First Touch, Crossing, Off The Ball, Tackling, Marking,
   Positioning) show **no clear effect** at this resolution (under ±0.015 xGD per point).
5. **The 27.0.1 patch changed almost nothing:** the per-attribute xGD effects on the two engines correlate at
   r = 0.98 over all 54 attributes.

For scale: moving the whole squad by +5 Pace is worth about +0.35 points per game, roughly 13 points over a
38-match season. Real squad changes are smaller and concern fewer players.

## How the main attributes work

Per +5 in-game points for the whole squad (t in brackets; |t| ≥ 3 is solid). "Conversion" is goals minus xG.

| Attribute | Points | xG for | xG against | Shots | Conversion | Possession share | Reading |
|---|---|---|---|---|---|---|---|
| Pace | +0.35 (7.5) | +0.32 (9.6) | −0.19 (−6.7) | +1.5 (9.1) | +0.15 (3.1) | −0.9 pp (−7.6) | more and better chances, faster game, less possession |
| Acceleration | +0.33 (6.5) | +0.24 (7.7) | −0.23 (−8.2) | +1.7 (10.1) | 0.00 | +1.3 pp (10.6) | both ends equally, more of the ball |
| Stamina | +0.18 (3.7) | +0.15 (5.0) | −0.15 (−5.5) | +0.9 (5.3) | +0.05 | −0.2 pp | both ends |
| Dribbling | +0.17 (3.5) | +0.20 (6.8) | −0.03 (−1.2) | +1.0 (5.8) | +0.07 | −0.3 pp | attack only |
| Jumping Reach | +0.16 (3.4) | +0.13 (4.4) | −0.21 (−7.7) | +1.2 (7.1) | −0.04 | −0.3 pp | mainly defence (aerial duels) |
| Anticipation | +0.12 (2.5) | +0.11 (3.5) | −0.13 (−5.5) | +0.7 (4.2) | −0.06 | +0.6 pp (4.3) | mainly defence, more of the ball |
| Work Rate | +0.12 (2.5) | +0.05 (1.7) | −0.05 (−2.0) | +0.4 (2.2) | −0.04 | +0.2 pp | goals against fall (−0.15, t −3.3) |
| Finishing | +0.11 (2.3) | +0.01 (0.3) | +0.03 (1.1) | −0.1 | **+0.20 (4.3)** | 0.0 | conversion only |
| Concentration | +0.09 (1.8) | +0.15 (4.8) | −0.07 (−2.7) | +1.1 (6.5) | −0.03 | +0.3 pp | more shots |
| Composure | +0.08 (1.6) | +0.14 (4.0) | −0.01 | +0.5 (2.7) | −0.03 | +1.0 pp (7.9) | keeps the ball, more xG |
| Vision | +0.08 (1.6) | +0.06 (2.1) | −0.03 | +0.1 | +0.11 (2.1) | +0.2 pp | small |
| Balance | −0.02 | +0.08 (2.6) | −0.08 (−3.4) | +0.4 (2.6) | −0.06 | +0.1 pp | xG better, points not |

Other patterns worth noting (each needs confirming before it is relied on):

- **Strength** and **Long Shots** raise goals above xG (+0.13 and +0.16 per +5, t ≈ 3), but Long Shots also
  raises goals against, and neither moves points clearly.
- **Aggression** lowers conversion (−0.15 per +5, t −3.2).
- **Kicking** (goalkeeper) is the only clearly negative attribute: −0.09 xG for per +5 (t −3.3), on both engines.
  Longer kicks may skip the build-up the tactic relies on.
- **Left Foot** and **Right Foot** shift possession share (−0.8 and −0.7 pp per +5, t ≈ −6 and −5) without
  changing results.
- **Natural Fitness** has exactly zero effect: the engine does not read it during a match (it governs recovery
  between matches).
- **Decisions and Versatility show no effect**, although both feed the player's tactical ability (the median of
  Anticipation, Decisions, Composure, Concentration and Versatility, see
  [Study 3](03-tactical-familiarity.md)). So the effects of Anticipation, Concentration and Composure come mostly
  from their own use in play, not from the familiarity channel. Study 3 measures that channel directly.

## All attributes, per in-game point

Sorted by xGD per point. "27.0" columns are the same design on the 27.0 engine.

| Attribute | ppg per point (t) | xGD per point (t) | xG for | xG against | 27.0: ppg | 27.0: xGD | n |
|---|---|---|---|---|---|---|---|
| Pace | +0.071 (+7.5) | +0.102 (+11.1) | +0.064 | -0.039 | +0.080 | +0.106 | 300 |
| Acceleration | +0.066 (+6.5) | +0.094 (+10.8) | +0.049 | -0.046 | +0.067 | +0.100 | 300 |
| Jumping Reach | +0.033 (+3.4) | +0.068 (+8.2) | +0.027 | -0.042 | +0.027 | +0.070 | 300 |
| Stamina | +0.036 (+3.7) | +0.059 (+7.3) | +0.030 | -0.029 | +0.043 | +0.060 | 300 |
| Anticipation | +0.023 (+2.5) | +0.049 (+6.1) | +0.022 | -0.027 | +0.028 | +0.058 | 300 |
| Dribbling | +0.034 (+3.5) | +0.047 (+5.7) | +0.041 | -0.006 | +0.031 | +0.048 | 300 |
| Concentration | +0.018 (+1.8) | +0.044 (+4.9) | +0.029 | -0.014 | +0.017 | +0.042 | 300 |
| Balance | -0.004 (-0.4) | +0.033 (+4.0) | +0.016 | -0.016 | +0.005 | +0.034 | 300 |
| Composure | +0.016 (+1.6) | +0.028 (+3.0) | +0.027 | -0.001 | +0.015 | +0.026 | 300 |
| Work Rate | +0.025 (+2.5) | +0.021 (+2.6) | +0.011 | -0.010 | +0.033 | +0.022 | 300 |
| Vision | +0.016 (+1.6) | +0.018 (+2.1) | +0.012 | -0.005 | +0.014 | +0.022 | 300 |
| Marking | +0.002 (+0.2) | +0.015 (+1.7) | +0.006 | -0.009 | +0.011 | +0.007 | 300 |
| First Touch | +0.012 (+1.2) | +0.014 (+1.6) | +0.013 | -0.000 | +0.012 | +0.010 | 300 |
| Command Of Area | -0.006 (-0.7) | +0.011 (+1.5) | +0.011 | -0.000 | +0.004 | +0.003 | 300 |
| Passing | +0.005 (+0.5) | +0.011 (+1.4) | +0.002 | -0.010 | +0.013 | +0.014 | 300 |
| Handling | +0.002 (+0.3) | +0.007 (+1.4) | +0.000 | -0.007 | +0.001 | +0.003 | 300 |
| Corners | +0.000 (+0.0) | +0.006 (+0.7) | +0.008 | +0.002 | +0.005 | +0.004 | 300 |
| Strength | +0.008 (+0.8) | +0.005 (+0.7) | +0.007 | +0.002 | +0.022 | +0.003 | 300 |
| Important Matches | +0.001 (+0.1) | +0.005 (+0.6) | +0.007 | +0.001 | +0.010 | +0.007 | 300 |
| Throwing | -0.003 (-0.3) | +0.004 (+0.6) | -0.001 | -0.005 | +0.000 | +0.005 | 300 |
| Communication | +0.015 (+1.7) | +0.003 (+0.3) | -0.003 | -0.005 | +0.008 | +0.011 | 300 |
| Long Throws | +0.007 (+0.8) | +0.002 (+0.3) | +0.004 | +0.002 | +0.009 | -0.003 | 300 |
| Leadership | +0.002 (+0.5) | +0.002 (+0.6) | -0.001 | -0.003 | -0.003 | +0.002 | 300 |
| One On Ones | -0.002 (-0.8) | +0.002 (+0.8) | +0.000 | -0.002 | +0.003 | +0.000 | 300 |
| Decisions | -0.004 (-0.4) | +0.002 (+0.2) | -0.003 | -0.005 | +0.013 | +0.003 | 300 |
| Aggression | -0.008 (-0.9) | +0.002 (+0.2) | -0.000 | -0.002 | -0.003 | -0.004 | 300 |
| Technique | -0.007 (-0.7) | +0.002 (+0.2) | +0.008 | +0.006 | +0.007 | +0.003 | 300 |
| Penalty Taking | -0.001 (-0.6) | +0.000 (+0.2) | +0.001 | +0.000 | +0.001 | +0.000 | 300 |
| Natural Fitness | +0.000 (+0.0) | +0.000 (+0.0) | +0.000 | +0.000 | +0.000 | +0.000 | 300 |
| Tendency To Punch | -0.005 (-1.1) | -0.001 (-0.2) | -0.001 | -0.001 | -0.005 | -0.001 | 300 |
| Versatility | +0.004 (+0.4) | -0.001 (-0.1) | +0.001 | +0.002 | -0.003 | +0.002 | 300 |
| Rushing Out | -0.005 (-0.7) | -0.001 (-0.2) | -0.002 | -0.001 | -0.019 | +0.000 | 300 |
| Dirtiness | -0.004 (-0.4) | -0.002 (-0.2) | +0.006 | +0.008 | -0.008 | +0.002 | 300 |
| Positioning | -0.006 (-0.6) | -0.002 (-0.3) | -0.005 | -0.002 | -0.006 | -0.010 | 300 |
| Determination | +0.011 (+1.2) | -0.003 (-0.3) | -0.000 | +0.002 | +0.002 | -0.000 | 300 |
| Tackling | -0.009 (-0.9) | -0.003 (-0.3) | -0.000 | +0.002 | -0.013 | +0.001 | 300 |
| Bravery | -0.006 (-0.6) | -0.003 (-0.4) | -0.003 | -0.000 | -0.012 | -0.009 | 300 |
| Left Foot | -0.002 (-0.2) | -0.003 (-0.4) | -0.001 | +0.002 | -0.009 | -0.001 | 300 |
| Teamwork | -0.002 (-0.2) | -0.003 (-0.4) | -0.005 | -0.002 | -0.006 | -0.007 | 300 |
| Injury Proneness | -0.005 (-0.9) | -0.003 (-0.7) | -0.004 | -0.000 | -0.006 | -0.001 | 300 |
| Finishing | +0.021 (+2.3) | -0.003 (-0.4) | +0.002 | +0.005 | +0.004 | -0.009 | 300 |
| Long Shots | +0.001 (+0.1) | -0.004 (-0.5) | +0.002 | +0.006 | +0.015 | -0.008 | 300 |
| Reflexes | +0.002 (+0.2) | -0.004 (-0.5) | +0.002 | +0.006 | -0.001 | -0.010 | 300 |
| Heading | +0.003 (+0.3) | -0.005 (-0.6) | -0.001 | +0.004 | -0.006 | +0.007 | 300 |
| Flair | +0.011 (+1.1) | -0.005 (-0.6) | -0.002 | +0.003 | +0.022 | +0.003 | 300 |
| Aerial Reach | -0.003 (-0.3) | -0.005 (-0.7) | -0.004 | +0.002 | +0.013 | +0.012 | 300 |
| Consistency | +0.006 (+0.6) | -0.006 (-0.8) | -0.005 | +0.001 | -0.000 | -0.003 | 300 |
| Right Foot | +0.011 (+1.2) | -0.007 (-0.8) | -0.006 | +0.000 | +0.011 | -0.002 | 300 |
| Free Kick Taking | +0.005 (+0.6) | -0.007 (-1.2) | -0.005 | +0.002 | +0.000 | -0.006 | 300 |
| Crossing | -0.011 (-1.1) | -0.009 (-1.1) | -0.005 | +0.004 | -0.013 | -0.014 | 300 |
| Eccentricity | +0.009 (+0.9) | -0.012 (-1.4) | -0.010 | +0.002 | +0.004 | -0.004 | 300 |
| Off The Ball | +0.003 (+0.3) | -0.012 (-1.4) | -0.007 | +0.005 | -0.010 | -0.014 | 300 |
| Agility | +0.015 (+1.6) | -0.012 (-1.5) | -0.007 | +0.005 | +0.008 | +0.002 | 300 |
| Kicking | -0.001 (-0.1) | -0.023 (-3.2) | -0.018 | +0.005 | -0.011 | -0.022 | 300 |

## Real squads against everyone at 12

Many FM attribute tests level every player to the same value (often 12) so that only the tested attribute differs.
[Study 2](02-real-vs-levelled.md) repeats this study three ways to see what that does (65,400 matches):

| | **A** (this study): real squads, real matches | **B**: everyone 12, real matches | **C**: everyone 12, generic test match |
|---|---|---|---|
| **Fixtures** | 10 real fixtures from a real save (a newly promoted Premier League side's league, cup and European matches) | the same 10 real fixtures | one match between two unnamed teams, the same for every run (the sample match from the original tool) |
| **Players' attributes** | real | every attribute of every player at 12 | every attribute of every player at 12 |
| **Positions** | real position ratings | real position ratings kept | every player natural in every position |
| **Bodies** | real | real | everyone 180 cm / 70 kg |
| **Tactics** | the real ones (the tested side's saved tactic; each opponent's AI tactic) | the same real tactics | the sample's generic default tactics (4-3-3 against 4-2-3-1) |
| **Match state and in-match management** | as they really were | as they really were | generic; the assistant manages both sides |
| **The two sides** | different clubs, strengths and styles | different clubs and tactics, same attribute level | two near-identical teams |

B is "the real games, with every player replaced by a 12-rated version of himself who keeps his position, body and
role"; C is "a friendly between two identical teams of interchangeable 12-rated players". Why C differs is not yet
settled: the generic default tactics, everyone being natural everywhere and the two mirrored teams are the main
candidates ([Study 2](02-real-vs-levelled.md#why-c-gives-different-answers-not-settled-yet)).

**How closely the attribute values agree** (correlation over all 54 attributes):

| | xG difference | Points per game |
|---|---|---|
| A (real squads) against B (everyone 12, real matches) | **0.88** | 0.79 |
| A against C (everyone 12, generic test match) | 0.77 | 0.58 |

**The main attributes side by side** (xG difference for +5 in-game points across the whole squad; t in brackets):

| Attribute | A: real squads | B: everyone 12, real matches | C: everyone 12, test match |
|---|---|---|---|
| Pace | +0.51 (11.1) | +0.69 (15.3) | +0.15 (7.4) |
| Acceleration | +0.47 (10.8) | +0.44 (10.5) | +0.26 (13.2) |
| Jumping Reach | +0.34 (8.2) | +0.28 (6.9) | +0.32 (14.4) |
| Stamina | +0.30 (7.3) | +0.42 (9.4) | +0.05 (2.4) |
| Anticipation | +0.24 (6.1) | +0.24 (5.9) | +0.05 (2.6) |
| Dribbling | +0.24 (5.7) | +0.22 (5.0) | +0.09 (4.9) |
| Concentration | +0.22 (4.9) | +0.22 (5.5) | +0.02 (1.0) |
| Balance | +0.16 (4.0) | +0.19 (4.7) | +0.05 (2.6) |
| Composure | +0.14 (3.0) | −0.03 (−0.8) | +0.01 (0.3) |
| Work Rate | +0.10 (2.6) | +0.02 (0.5) | +0.01 (0.7) |
| Strength | +0.03 (0.7) | +0.13 (3.0) | +0.03 (1.3) |
| Agility | −0.06 (−1.5) | +0.09 (2.3) | +0.01 (0.7) |
| Kicking (goalkeeper) | −0.12 (−3.2) | 0.00 (0.1) | 0.00 (0.1) |

All 54 attributes, with points per game too, are in [Study 2](02-real-vs-levelled.md#results).

What it shows:

1. **Levelling the squads changes little, as long as the matches are real.** With every player at 12 in the real
   matches (B), the same attributes lead and the sizes are similar: Pace, Acceleration, Stamina, Jumping Reach, then
   Anticipation, Dribbling and Concentration.
2. **The generic test match is what distorts the result.** On it (C), most effects shrink to about 40% and several
   vanish: Stamina, Anticipation and Concentration look almost worthless there, though they clearly count in real
   matches. Only Jumping Reach keeps its size. The common conclusion that "mental attributes barely matter" comes
   from tests like C.
3. **A few effects depend on the squad.** Composure, Work Rate and goalkeeper Kicking (negative) count only with real
   players; Strength and Agility count only when everyone is equal, perhaps because they decide duels between
   otherwise identical players.

**For your own tests:** use real matches. Levelled squads are acceptable if the matches are real (B gives nearly
the same answers as A); a single generic test match understates most attributes and misses some entirely.

## 27.0 against 27.0.1

Same matches, seeds and design on both engines. The ranking is essentially unchanged (r = 0.98 for xGD effects).
The largest differences are small and within noise: Strength (+0.022 → +0.008 ppg per point), Flair (+0.022 →
+0.011), Rushing Out (−0.019 → −0.005), Long Shots (+0.015 → +0.001) and Finishing (+0.004 → +0.021 ppg, while its
xGD stays near zero on both). The baseline was 1.79 ppg on both.

## Caveats

- **One club, one situation.** The team is a newly promoted, lower-table side playing mostly stronger Premier
  League opponents. Values could differ for a dominant team, where attacking attributes may matter more.
- **Whole-squad changes.** The effect of improving one player is roughly the per-point value spread over the eleven
  on the pitch, but positions matter: Dribbling on a centre-back is not worth what it is on a winger. This study does
  not split by position.
- **Linear only.** Effects are averaged over −5 to +5 around each player's real value. They say nothing about
  diminishing returns at the top of the scale.
- **Many comparisons.** 54 attributes × 10 measures produce a few |t| ≈ 2–3 results by chance. The headline effects
  have t from 5 to 11 and agree across both engines.
- **Resolution.** ±0.015 xGD per point is about the smallest effect this design can see. "No clear effect" is not
  "no effect".

## Reproduce

```sh
.venv/bin/python port/validation/attr_real.py build port/mac_host/runs/attr_real_2701 "<team>" 30   # jobs, 30 seeds
FM27_STUDY_HOST=<frozen host> .venv/bin/python port/validation/overnight.py run port/mac_host/runs/attr_real_2701 6
.venv/bin/python port/validation/attr_real.py analyse port/mac_host/runs/attr_real_2701 "<team>"  # all measures
.venv/bin/python port/validation/study1_compare.py port/mac_host/runs/attr_real_2701 port/mac_host/runs/attr_real
```

The saved matches are the user's own; results and job files stay in the git-ignored `port/mac_host/runs/`.
