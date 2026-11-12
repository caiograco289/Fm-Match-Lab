# How our results compare with other FM27 tests

Two other testers have published FM27 results on the same questions, using different methods. This page lines them
up with ours. Where we agree, the result is more likely to hold; where we differ, the method usually explains why.

| | harvestgreen22 (forum post, early November) | Another engine tester (forum post) | This project |
|---|---|---|---|
| Method | In-game seasons with locked conditions (FMRTE), win rate | FM27's engine outside the game, paired seeds, xPts | FM27's engine outside the game, paired seeds, points and xG |
| Squads | Every attribute 12, one formation (Gegenpress), 5 opponent formations | One squad against one opponent | One club's ten real saved matches; levelled squads in Study 2 |
| Scale | 1 → 18 per attribute; whole seasons | Familiarity levels 50, 65, 100 | ±5 points around real or levelled values; single matches |

## Attributes

Their table (win rate from 1 to 18) and our Studies 1 and 2 agree on the main points.

| | harvestgreen22 | This project |
|---|---|---|
| Top four | Pace 59%, Acceleration 48%, Stamina 43%, Jumping Reach 33% | the same four in every arm (Study 1 and 2) |
| Second group | Work Rate, Pressure, Strength, Anticipation, Concentration, Natural Fitness, Balance | Anticipation, Concentration, Balance (real matches); Strength and Agility only with levelled squads; Work Rate with real squads |
| Third group | Dribbling, Finishing, Long Shots, Determination, Agility, Consistency, Important Matches, Heading | Dribbling; Finishing converts chances rather than creating them; Long Shots raises goals for and against |
| Little or negative | Technique, Tackling, Vision, Off the Ball negative above 12 | Technique, Tackling, Off the Ball: no clear effect; Vision small |

Where we differ, and why it probably happens:

- **Natural Fitness:** 15% in their test, exactly zero in ours. They play whole seasons, where it governs recovery
  between matches; we play single matches.
- **Pressure** (personality): 21% in their test; ours looked positive in a first screen but didn't hold up on 900
  more pairs. Like Natural Fitness, it may act across a season (pressure situations, form) rather than within one
  match.
- **Work Rate above 12:** useless in their test, consistent with our levelled arm (12±5), where it showed nothing
  clear; with real squads, where many players are lower, it counts.
- **Agility:** useless above 12 in their test, clearly positive in our levelled arm (7-17).
- **Determination, Consistency, Important Matches:** small in theirs, nothing in ours. Again, likely season effects.

## Tactical familiarity

| | Other tests | This project (Study 3, win rate on the team's real matches) |
|---|---|---|
| Maxing it from a normal level | +6% win rate (harvestgreen22) | natural 53% → training 75-100: 62% (+9 points) |
| Moderate training increase | +30% understanding → +3.5% win rate (harvestgreen22) | training 25 → 50: +6 points; 50 → 75: +5 points |
| Untrained vs trained | +0.26 real points per match at 50 and +0.40 at 100, against near zero (other tester) | training 0 → 50: +0.51 points per game; 0 → 100: +0.62 |
| Only one area raised | almost nothing (other tester) | almost nothing: no single area at 100 gives a clear gain; the effect is spread across all eight (Study 3, step 2) |
| Shape of the curve | rises to 100 (+0.26 at 50, +0.30 at 65, +0.40 at 100, other tester) | rises to about 50, then flat; 90 and 100 identical (engine cap) |
| How it builds and fades | sessions add records that fade (half after about three weeks); matches add to it (other tester, from game data) | saved matches: match exposure +2 per match; the training part falls between matches |

All three agree on the direction: familiarity is worth real points, mostly through training. The difference is in
framing. Topping up a tactic that is already learned is worth a few percent of win rate (all three tests). An
untrained tactic costs much more: about 14 points of win rate against the team's normal level in our test. That's
the case the "not worth the training time" view leaves out.

The cost side (more sessions, more injury risk, other training lost) happens in the game's training system, which
none of the engine tests can measure.

## Preset tactics

| | harvestgreen22 | This project (Study 6, one club, fixed and picked XIs) |
|---|---|---|
| Strongest presets | Wing Play 4-2-4 (4-4-2), Gegenpress 4-2-3-1, Fluid Counter-Attack | Control Possession, Gegenpress, Fluid Counter-Attack |
| Weakest | Tiki-Taka, Catenaccio | Park the Bus, Catenaccio, Route One, Tiki-Taka |

Agreement on the bottom (Catenaccio, Tiki-Taka) and on Gegenpress and Fluid Counter-Attack doing well. Wing Play is
their winner but middling in ours: they tested several formations per preset and found its 4-2-4 shape strongest,
while we used one formation per style, played by one weaker club's squad. The league (running) plays the presets
against each other directly.

## What none of us can test yet

- How training schedules, intensity and injuries trade off against familiarity (game training system).
- Whether these values hold for a dominant team, a different league or another formation family. `scripts/study.py`
  makes it straightforward to repeat any of our studies on another save.
