# Study 9: are attribute values tied to the tactic?

**Status:** done (12 November, 6,000 matches). Asked by a reader: attribute tests usually run "meta" tactics (high
press, high tempo, counter-attack), so physical attributes may come out on top only because they suit those tactics.
Would passing attributes matter more under a possession system?

**In short: no.** Physical attributes are worth three to four times as much as passing attributes under every style,
possession styles included. Passing attributes help most under the direct styles (Direct Counter-Attack and
Gegenpress) and least under the possession styles (Tiki-Taka and Control Possession), the opposite of what the
question expected. With a possession style, better passers keep the ball less, not more.

## Design

- **Five styles for the tested side:** the FM27 presets Gegenpress, Tiki-Taka, Control Possession and Direct
  Counter-Attack, and a "Neutral" style: Gegenpress's shape and roles with every team instruction on its standard
  option (Balanced mentality; on/off instructions off; time wasting never).
- **Two attribute groups, +5 for the whole squad** (every attribute in the group, in-game points, capped at 20):
  - **physical:** Pace, Acceleration, Stamina, Work Rate, Aggression;
  - **passing:** Passing, Technique, Vision, Decisions, First Touch, Composure.
- **Neutral ground, as in Study 7:** both sides have the same synthetic reference squad (Premier League middle eight),
  start alike, and have tactical familiarity held at 80 in all areas. No real team is involved; fixtures alternate
  between two template matches between other clubs (Leeds United v Tottenham Hotspur, Everton v West Ham United), of
  which only the stadium and conditions are used.
- **Opponents:** four presets of different styles (Gegenpress, Control Possession, Park the Bus, Route One), home and
  away.
- **Paired:** 50 seeds for each style, group, opponent and venue. Every boosted match is compared with the same match
  and seed without the boost: 400 pairs per style and group.

## The styles, unchanged

| Style | Points per game | xG for | xG against | Possession | Passes | Pass completion |
|---|---|---|---|---|---|---|
| Gegenpress | 1.48 | 1.50 | 1.21 | 56% | 606 | 88% |
| Tiki-Taka | 1.24 | 1.20 | 1.13 | 63% | 802 | 92% |
| Control Possession | 1.48 | 1.52 | 1.20 | 60% | 684 | 90% |
| Direct Counter-Attack | 1.27 | 1.21 | 1.22 | 45% | 428 | 82% |
| Neutral | 1.48 | 1.40 | 1.15 | 53% | 583 | 88% |

The styles play as intended: Tiki-Taka keeps the ball most and passes most; Direct Counter-Attack gives the ball away
and plays fewer, riskier passes.

## What +5 is worth under each style

Per game, against the same matches unchanged; t in brackets (|t| ≥ 2 is about 95% confidence, ≥ 3 solid). xPts:
expected points from both sides' xG, steadier than points. Per season: multiply by 38.

| Style | Group | Points | xPts | xG difference | xG for | xG against |
|---|---|---|---|---|---|---|
| Gegenpress | physical | +0.75 (+8.4) | +0.48 (+13.4) | +0.85 (+13.5) | +0.52 | −0.33 |
| Tiki-Taka | physical | +0.62 (+7.3) | +0.44 (+12.1) | +0.69 (+11.8) | +0.38 | −0.31 |
| Control Possession | physical | +0.64 (+7.1) | +0.43 (+11.4) | +0.73 (+11.2) | +0.44 | −0.30 |
| Direct Counter-Attack | physical | +0.59 (+6.4) | +0.48 (+12.4) | +0.77 (+12.2) | +0.48 | −0.29 |
| Neutral | physical | +0.45 (+4.7) | +0.38 (+9.8) | +0.64 (+9.9) | +0.38 | −0.25 |
| Gegenpress | passing | +0.20 (+2.2) | +0.11 (+2.7) | +0.19 (+3.0) | +0.12 | −0.07 |
| Tiki-Taka | passing | +0.08 (+0.9) | +0.01 (+0.2) | +0.02 (+0.3) | +0.06 | +0.04 |
| Control Possession | passing | +0.08 (+0.9) | +0.01 (+0.3) | +0.03 (+0.5) | +0.06 | +0.02 |
| Direct Counter-Attack | passing | +0.38 (+4.4) | +0.15 (+4.2) | +0.25 (+4.4) | +0.19 | −0.06 |
| Neutral | passing | −0.14 (−1.6) | −0.02 (−0.7) | −0.05 (−0.8) | −0.01 | +0.04 |

- **Physical:** +0.38 to +0.48 xPts per game under every style, about 14 to 18 points a season. It works at both
  ends: more chances made (+2.6 shots per game) and fewer conceded (−2.0 shots against). Gegenpress gains most, as the
  question suspected, but the possession styles gain almost as much (0.69 to 0.73 xGD against 0.85).
- **Passing:** clear under Direct Counter-Attack (+0.15 xPts, about 6 points a season) and Gegenpress (+0.11, about 4);
  nothing measurable under Tiki-Taka, Control Possession and Neutral.

## Does the style change what a group is worth?

The passing effect (xG difference per game) compared between styles; t from both standard errors:

| | Gegenpress | Tiki-Taka | Control Possession | Direct Counter-Attack | Neutral |
|---|---|---|---|---|---|
| **Passing effect** | +0.19 | +0.02 | +0.03 | +0.25 | −0.05 |
| Direct Counter-Attack minus this style | +0.06 (+0.7) | +0.23 (+2.7) | +0.21 (+2.5) | · | +0.29 (+3.7) |
| Gegenpress minus this style | · | +0.17 (+1.9) | +0.16 (+1.8) | −0.06 (−0.7) | +0.24 (+2.8) |

Taken together, the two direct styles gain +0.22 xGD from passing and the two possession styles +0.03: a difference of
0.19 (t about 3). The physical effect varies less between styles (+0.64 to +0.85); only Neutral is clearly below
Gegenpress (−0.22, t −2.4).

**The hypothesis in one number.** If passing attributes paid more in a possession system, the passing gain under
Tiki-Taka minus the passing gain under Gegenpress would be clearly positive. It is −0.17 xGD per game (t −1.9): if
anything the wrong sign, and certainly not the positive effect the hypothesis needs.

## Stamina and intensity (Study 9b)

A tester on FM Arena found that Stamina matters even more with intense tactics. Study 9b (12 November, 2,400
matches) holds the shape fixed and changes only the intensity: the Gegenpress preset, which is already at the top
of all three settings (pressing Much more often, tempo Much Higher, High press); the same shape with all three on
Standard and Mid block; and all three at the bottom (Much less often, Much Lower, Low block). The whole squad gets
+5 Stamina; otherwise the design is the one above (400 pairs per intensity).

| Intensity | Points per game, unchanged | Stamina +5: xPts | xG difference | xG for | xG against | Shots | Shots against |
|---|---|---|---|---|---|---|---|
| High (Gegenpress preset) | 1.48 | +0.13 (+3.5) | +0.24 (+3.8) | +0.12 | −0.11 | +0.5 | −0.2 |
| Standard | 1.52 | +0.05 (+1.2) | +0.08 (+1.4) | +0.08 | −0.00 | +0.1 | −0.1 |
| Low | 1.41 | +0.09 (+2.5) | +0.14 (+2.4) | +0.07 | −0.07 | +0.7 | −0.6 |

- **Stamina pays at every intensity:** +0.09 xPts per game pooled over the three (t 4.2), about 3.5 points a season.
- **It pays most at high intensity** (+0.13 xPts, about 5 points a season), but the differences between intensities
  are not significant: high minus standard +0.09 xPts (t 1.6), high minus low +0.04 (t 0.7). The data lean the
  tester's way without confirming it; it would take about four times as many matches to settle.
- The unchanged Gegenpress matches reproduce Study 9's exactly (1.48 points per game, xG 1.50 for and 1.21 against).

## Why passing helps the direct styles and not the possession styles

What +5 passing changes in each style's own play, per game (t in brackets):

| Style | Possession | Passes | Pass completion | Shots | Shots against |
|---|---|---|---|---|---|
| Gegenpress | −0.8 pts (−3.8) | −9 (−2.6) | −0.6 pts (−6.5) | +0.8 (+2.8) | −0.2 (−1.1) |
| Tiki-Taka | −0.9 pts (−4.7) | −26 (−6.0) | −0.6 pts (−9.1) | +0.4 (+1.5) | +0.1 (+0.5) |
| Control Possession | −1.2 pts (−6.1) | −23 (−6.7) | −0.9 pts (−10.6) | +0.6 (+2.2) | +0.0 (+0.0) |
| Direct Counter-Attack | +1.3 pts (+6.7) | +17 (+6.3) | +1.1 pts (+7.5) | +0.8 (+3.0) | −0.9 (−3.9) |
| Neutral | −0.7 pts (−3.7) | −11 (−3.2) | −0.7 pts (−6.7) | +0.3 (+1.2) | −0.1 (−0.4) |

- **Possession styles already complete 90-92% of their passes.** Better passers don't keep the ball better; they
  keep it slightly *less* and complete fewer passes. The group includes Vision and Decisions, so the likeliest reading
  is that players see and try more ambitious passes, which fail more often, without making many more chances.
- **Direct Counter-Attack completes only 82%** of its passes, most of them long and forward. There better technique
  pays: more passes completed (+1.1 points of completion), more possession, more shots and fewer shots against (the
  ball is lost less, so the opponent counters less).
- **Physical attributes don't change how a side passes** (possession and completion move by less than 1 point) under
  any style; they win chances at both ends directly.

## Caveats

- **Groups, not single attributes.** The passing group mixes execution (Passing, Technique, First Touch) with decisions
  (Vision, Decisions, Composure), and the physical group has five attributes against six. Study 1 measures attributes
  one at a time; a follow-up could split the passing group into execution and decisions.
- **One squad and +5 for everyone.** A mid-table Premier League squad, every player improved. Improving only the
  players a style relies on most (for example the midfield in Tiki-Taka) is not tested.
- **The installed presets.** Community possession tactics may use passing players differently; the opponents are a
  panel of four presets, not a league.
- **Tactical familiarity is held at 80** for both sides, and tactical complexity is not recomputed by the match engine
  (see the main README), so complex instructions don't pay their in-game cost.
- In the unchanged Gegenpress v Gegenpress matches both sides are identical, so home and away replay the same match;
  this affects only one cell of the baseline table, not the paired effects.

## Reproduce

```sh
.venv/bin/python port/validation/study9_attributes_by_style.py build runs/study9 TEMPLATE1_fm.pkm TEMPLATE2_fm.pkm --seeds 50
.venv/bin/python port/validation/study9_attributes_by_style.py run runs/study9 --workers 6     # resumable, about 1 hour with 6 workers
.venv/bin/python port/validation/study9_attributes_by_style.py report runs/study9
```

The templates are any two saved matches between other clubs (for example from `scripts/import_other_matches.py`);
only their stadium and conditions are used.
