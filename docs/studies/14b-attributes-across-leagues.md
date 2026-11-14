# Study 14b: are attributes worth the same in every league?

**Status:** done (13 November, 9,600 matches). Study 14 found that attribute values hold for strong and weak sides
within the Premier League. Do they also hold lower down the English pyramid, for a mid-table side in the
Championship, League One, League Two or the National League?

**In short: yes.**
- **The same three attributes lead in every league:** Pace, Acceleration and Jumping Reach are the top three in all
  five, each worth about +0.22 to +0.37 expected points per game for +5 across the squad.
- **No attribute's value differs between leagues** beyond chance (p 0.86 over all eleven attributes), and none has a
  clear trend from the Premier League down.
- **A lead:** Pace may be worth a little more lower down (+0.22 in the Premier League, +0.32 to +0.36 in League Two and
  the National League; trend t 1.7). Not established.

## Design

- **Neutral ground,** as in Study 14:
  - Gegenpress for the tested side.
  - Tactical familiarity held at 80.
  - Four preset opponents (Gegenpress, Control Possession, Park the Bus, Route One), home and away.
  - Two template matches between other clubs.
- **Five leagues, a mid-table side in each:** synthetic reference squads calibrated on each league's middle eight
  clubs at the start of the season, on both sides.

  | League | Tier | Median Current Ability of the squad |
  |---|---|---|
  | Premier League | 1 | 138 |
  | Championship | 2 | 119 |
  | League One | 3 | 102 |
  | League Two | 4 | 91 |
  | National League | 5 | 73 |

  The lower-league squads are new: invented players drawn from each league's real profile (see
  `scripts/reference_squads.py`), checked to be at least twice as far from any real player as real players are from
  each other.
- **Conditions:** each of Study 14's ten attributes +5 for the whole tested squad, plus Strength.
- **Paired:** 160 pairs per condition, against the same matches unchanged.

## The attributes in each league

Expected points (xPts) per game from +5 for the whole squad; t in brackets (|t| ≥ 4 established, 3-4 likely, below
that unconfirmed). "Differ?" tests whether the five leagues differ (chi-square on 4 degrees of freedom; about 9.5 is
the 5% line); "Trend" is the change per tier down the pyramid.

| Attribute | Premier League | Championship | League One | League Two | National League | Differ? | Trend per tier (t) |
|---|---|---|---|---|---|---|---|
| Pace | +0.22 (+3.8) | +0.24 (+4.6) | +0.27 (+4.6) | +0.36 (+6.0) | +0.32 (+5.8) | 3.6 | +0.030 (+1.7) |
| Acceleration | +0.37 (+6.5) | +0.26 (+4.6) | +0.34 (+6.2) | +0.25 (+4.1) | +0.29 (+5.1) | 2.8 | −0.015 (−0.8) |
| Jumping Reach | +0.31 (+5.4) | +0.32 (+5.7) | +0.26 (+4.3) | +0.27 (+4.1) | +0.27 (+4.6) | 0.9 | −0.013 (−0.7) |
| Stamina | +0.16 (+2.4) | +0.02 (+0.4) | +0.18 (+2.8) | +0.17 (+3.3) | +0.13 (+2.2) | 4.7 | +0.011 (+0.6) |
| Anticipation | +0.19 (+3.2) | +0.09 (+1.4) | +0.08 (+1.3) | +0.22 (+3.6) | +0.04 (+0.6) | 6.2 | −0.016 (−0.8) |
| Dribbling | +0.14 (+2.4) | +0.06 (+1.0) | +0.20 (+3.3) | +0.02 (+0.3) | +0.05 (+0.8) | 5.6 | −0.023 (−1.2) |
| Balance | +0.13 (+2.1) | +0.05 (+0.8) | +0.13 (+2.1) | +0.07 (+1.2) | +0.13 (+2.2) | 1.6 | +0.003 (+0.2) |
| Composure | +0.05 (+0.8) | −0.00 (−0.1) | +0.12 (+2.0) | +0.07 (+1.1) | +0.12 (+2.2) | 3.1 | +0.023 (+1.2) |
| Concentration | +0.08 (+1.3) | +0.03 (+0.5) | +0.02 (+0.4) | +0.08 (+1.3) | +0.01 (+0.2) | 1.1 | −0.008 (−0.4) |
| Work Rate | +0.07 (+1.1) | −0.01 (−0.2) | +0.07 (+1.2) | +0.05 (+0.8) | +0.07 (+1.2) | 1.5 | +0.007 (+0.4) |
| Strength | +0.03 (+0.5) | +0.04 (+0.7) | +0.08 (+1.4) | +0.03 (+0.5) | +0.14 (+2.5) | 2.9 | +0.023 (+1.2) |
| **Mean of the ten** | +0.16 | +0.10 | +0.16 | +0.15 | +0.14 | | |

- **No league differs:** every chi-square is below the 5% line, and all eleven attributes together give 34.0 on 44
  degrees of freedom (p 0.86). Points instead of xPts give the same answer (p 0.30).
- **The top three are the same everywhere:** Pace, Acceleration and Jumping Reach, in some order, are the top three in
  every league.
- **Below the top three, the order is noisier** (the rank correlation between two leagues averages 0.70, against
  0.84 between the strength pairings of Study 14). The middle attributes are worth 0.02-0.20 each, close enough together that 160 pairs can't order them
  reliably in any one league; no attribute is consistently higher or lower in the lower leagues.
- **The Championship's lower average** (+0.10) comes from Stamina and Anticipation being near zero there. It is not
  significant, and there's no trend through the other leagues.

## Strength and finishing

Study 12 found that Strength works through goals, not xG. Goals minus xG for the tested side, Strength +5:

| | Premier League | Championship | League One | League Two | National League | Pooled |
|---|---|---|---|---|---|---|
| Goals minus xG | +0.27 (+2.4) | +0.10 (+0.9) | +0.20 (+1.6) | −0.05 (−0.4) | +0.02 (+0.2) | +0.11 (+2.1) |

The effect points the same way overall, as in Study 12, but is too small at +5 to compare leagues.

## So: is an attribute worth the same in every league?

**Yes, as far as this resolution goes.** An attribute table measured with Premier League squads applies to a
mid-table side in the Championship, League One, League Two or the National League. Pace, Acceleration and Jumping
Reach lead everywhere. Together with Study 14, neither the level of the league nor a side's strength within it changes
which attributes matter.

## Caveats

- **Synthetic squads,** one per league, calibrated on the middle eight clubs. Each league's matches are played on two
  Premier League templates (the same as Study 14), so lower-league grounds and conditions are not part of the test.
- **One style for the tested side** (Gegenpress), against four presets.
- **160 pairs per condition.** Enough to rule out large differences between leagues (about ±0.15 xPts at 95%), not
  small ones.
- **Expected points** miss finishing effects (Strength, Finishing; Study 12).

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 14b runs/study14b
.venv/bin/python port/validation/neutral_study.py pilot runs/study14b --workers 7
.venv/bin/python port/validation/neutral_study.py run runs/study14b --workers 7     # about 1.5 hours with 7 workers
.venv/bin/python port/validation/neutral_study.py report runs/study14b
```

The lower-league squads are in `src/reference_squads.json` (tiers `championship`, `league-one`, `league-two`,
`national-league`). The tests are as in Study 14: inverse-variance chi-squares across the five independent leagues,
and a weighted linear trend over the tier.
