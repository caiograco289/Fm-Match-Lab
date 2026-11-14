# Study 15b: home advantage on every ground

**Status:** done (13 November, 6,020 matches). Study 15 found home advantage differs between grounds more than chance
allows, on twelve grounds. Is it the size of the stadium, the pitch, or the match itself? A player on FM Arena argues
that home advantage comes from the crowd: more spectators, more advantage.

**In short:**
- **Overall, home advantage is +0.22 xG and +0.37 points per match** (home side minus away side), as in Study 15.
- **Big stadiums give more than twice as much.** Grounds of 40,000 or more give +0.39 xG; smaller grounds +0.15 to
  +0.18, with no trend from 4,000 to 40,000.
- **Pitch size makes no difference.**
- **The same stadium differs from match to match** more than chance allows. Something about the match matters, not
  only the ground: the crowd on the day is a candidate, but so are weather and the competition.
- **Crowd, stadium and club can't be separated here:** big stadiums belong to big clubs, and the match input has no
  attendance field we can change.

## Design

- **Study 15's set-up on many grounds:** both sides the same synthetic squad (Premier League middle eight), both
  playing Gegenpress, tactical familiarity held at 80. The only difference between the sides is which is at home.
- **86 matches between other clubs** imported from the game, on 65 stadiums from non-league to the Champions League,
  used only for their ground and conditions. Several stadiums appear in two to four matches.
- **70 seeds per match,** 6,020 matches.
- **Each ground's capacity and pitch size** come from the save the matches were imported from.

## By stadium size

| Capacity | Grounds | Home advantage, xG | Goals | Expected points, home minus away | Points, home minus away |
|---|---|---|---|---|---|
| Under 8,000 | 13 | +0.15 (±0.03) | +0.26 | +0.17 | +0.40 |
| 8,000-20,000 | 25 | +0.16 (±0.02) | +0.17 | +0.17 | +0.20 |
| 20,000-40,000 | 26 | +0.18 (±0.02) | +0.25 | +0.21 | +0.30 |
| 40,000 and over | 22 | **+0.39** (±0.02) | **+0.47** | **+0.44** | **+0.63** |

- **A step, not a slope.** Up to 40,000 home advantage is flat; above it, it more than doubles. Across all grounds,
  xG home advantage rises by 0.31 per tenfold capacity (t 4.0), but that is the step averaged out.
- **Pitch length and width:** −0.017 xG per metre of length (t −1.5), −0.004 per metre of width (t −0.3). Nothing.
- **Grounds differ a lot:** the spread between grounds is far larger than chance (Q 301 on 85 degrees of freedom); the
  true spread is about ±0.18 xG.
- **The largest:** Liverpool's ground (+0.75 xG in two different matches), Arsenal's (+0.36 to +0.67), Inter's (Blu-neri Milano in the game, +0.66),
  Manchester United's (+0.59), Everton's (+0.61 in one match). The smallest are non-league and mid-sized grounds, down
  to about zero.

## The same stadium, different matches

Seventeen stadiums appear in two or more matches. Their matches differ more than chance allows (Q 52 on 21 degrees of
freedom, p < 0.001). For example:

| Stadium of | Matches (xG home advantage) |
|---|---|
| Everton | v Fulham +0.61, v Newcastle United +0.24, v West Ham United −0.03 |
| Manchester City | v Inter −0.02, v Paris Saint-Germain +0.48 and +0.26, v Benfica +0.58 |
| West Bromwich Albion | v Exeter City +0.19, v Sheffield Wednesday +0.57 |
| Carlisle United | v Harrogate Town +0.31, v MK Dons +0.02 |
| Liverpool | v Coventry City +0.75, v Juventus +0.75 |

So home advantage depends on the match as well as the ground. Each imported match carries its own crowd, weather,
pitch condition and competition; this study can't say which of these matters.

## The crowd question

FM Arena's claim: more spectators give more home advantage, so maximise stadium seats.
- **Partly supported:** home advantage is much larger in big stadiums, and varies from match to match at the same
  stadium, as a crowd effect would.
- **Not as a steady gain from seats:** between 4,000 and 40,000 more capacity changes nothing measurable.
- **Not separated:** stadium size, crowd and the size of the home club go together. The game's code has crowd fields
  (attendance, home and away crowd shares, crowd mood), but they aren't part of the match input we can edit, and it
  isn't known which the match engine reads. A direct test would set the attendance of one match and change nothing
  else.

## What this means for other studies

- **Paired studies are unaffected:** every condition plays the same ground as its comparison.
- **Absolute levels depend on the grounds.** The season tool (Study 19) first played on grounds with twice the usual
  home advantage; it now picks grounds whose home advantage matches the league's own stadiums.

## Caveats

- **One squad and one tactic** (a Gegenpress mirror); 70 seeds per match, so a single match's figure is ±0.24 xG.
- **Capacity from a later save** of the same career than some of the matches; a stadium may have been expanded since.
- **21 imported matches without team names** and the user's own club's matches were left out.

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 15b runs/study15b
.venv/bin/python port/validation/neutral_study.py run runs/study15b --workers 7     # about 1 hour with 7 workers
```

The specification is `s15b` in `port/validation/roadmap_studies.py`: every imported match between other clubs with
known names. Home advantage per match is home minus away xG, goals and points over its seeds; capacities and pitch
sizes come from the save's stadium records (fmsave).
