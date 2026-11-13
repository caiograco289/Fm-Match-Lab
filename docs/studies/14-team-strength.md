# Study 14: does team strength change what attributes are worth?

**Status:** done (13 November, 8,800 matches). FM Arena's attribute tests use equal-strength sides, and FM Arena
itself warns that its results need translating to real saves. Do attribute values and their ranking hold for a
dominant side as for an underdog, and for strong leagues as for weak ones?

**In short: yes, they hold.**
- **The ranking of the ten attributes is the same at every strength.** Acceleration and Jumping Reach are the top two
  in all five pairings. The average rank correlation between pairings is 0.84.
- **No attribute's value depends on strength** beyond chance. Over all ten attributes and five pairings, the
  differences are what chance gives (p 0.81).
- **A lead, not a finding:** an underdog gains a little less overall from +5 (+0.07 xPts per game against
  +0.11-0.17), and what it gains comes from conceding less rather than scoring more.

## Design

- **Neutral ground,** as in the other roadmap studies:
  - Gegenpress for the tested side.
  - Tactical familiarity held at 80.
  - Four preset opponents (Gegenpress, Control Possession, Park the Bus, Route One), home and away.
  - Two template matches between other clubs.
- **Five strength pairings,** with the synthetic Premier League reference squads:

  | Pairing | Tested side | Opponent |
  |---|---|---|
  | top v top | top eight | top eight |
  | middle v middle | middle eight | middle eight |
  | bottom v bottom | bottom eight | bottom eight |
  | favourite | top eight | bottom eight |
  | underdog | bottom eight | top eight |

  The squads differ moderately: median Current Ability 148, 138 and 131. On attributes, the top squad is about one
  point higher than the bottom squad in most of the ten tested here.
- **Conditions:** the ten most valuable attributes in Study 1, each +5 for the whole tested squad.
  - **Attributes:** Pace, Acceleration, Jumping Reach, Stamina, Anticipation, Dribbling, Concentration, Balance,
    Composure, Work Rate.
- **Paired:** 160 pairs per condition, each against the same matches with the squad unchanged.
- **Not run here:** the roadmap's preset league by strength. Tactic rankings by squad tier are Study 19's question.

## How strong is "favourite"?

| Pairing | Points per game (unchanged) | xG for | xG against | Shots for / against |
|---|---|---|---|---|
| top v top | 1.36 | 1.56 | 1.35 | 15.3 / 10.8 |
| middle v middle | 1.47 | 1.43 | 1.18 | 14.4 / 9.8 |
| bottom v bottom | 1.51 | 1.54 | 1.21 | 14.6 / 9.9 |
| favourite | **1.82** | 1.80 | 1.05 | 16.7 / 9.2 |
| underdog | **1.11** | 1.46 | 1.51 | 13.8 / 11.9 |

The gap between the top and bottom squads is worth about 0.7 points per game. The tested side does a little better
than its opponent even with equal squads; that comes from the presets it meets, not from the squads.

## The attributes at each strength

Expected points (xPts) per game from +5 for the whole squad; t in brackets (|t| ≥ 4 established, 3-4 likely, below
that unconfirmed). The last column tests whether the five pairings differ (chi-square on 4 degrees of freedom; about
9.5 is the 5% line).

| Attribute | top v top | middle v middle | bottom v bottom | favourite | underdog | Differ? |
|---|---|---|---|---|---|---|
| Acceleration | +0.26 (+4.2) | +0.37 (+6.5) | +0.25 (+4.1) | +0.23 (+4.3) | +0.22 (+3.7) | 4.1 |
| Jumping Reach | +0.35 (+6.0) | +0.31 (+5.4) | +0.27 (+4.5) | +0.23 (+3.9) | +0.21 (+3.4) | 3.8 |
| Pace | +0.19 (+3.2) | +0.22 (+3.8) | +0.23 (+3.8) | +0.15 (+2.7) | +0.14 (+2.6) | 2.1 |
| Stamina | +0.20 (+3.2) | +0.16 (+2.4) | +0.08 (+1.2) | +0.11 (+1.9) | +0.01 (+0.2) | 6.0 |
| Anticipation | +0.13 (+2.4) | +0.19 (+3.2) | +0.15 (+2.6) | +0.16 (+2.7) | +0.03 (+0.5) | 4.1 |
| Dribbling | +0.11 (+2.0) | +0.14 (+2.4) | +0.16 (+2.8) | +0.13 (+2.4) | +0.02 (+0.4) | 3.2 |
| Balance | +0.13 (+2.2) | +0.13 (+2.1) | +0.06 (+0.9) | +0.11 (+2.0) | +0.03 (+0.6) | 2.0 |
| Concentration | +0.05 (+1.0) | +0.08 (+1.3) | +0.06 (+1.0) | +0.03 (+0.5) | +0.09 (+1.7) | 0.7 |
| Composure | +0.06 (+1.0) | +0.05 (+0.8) | +0.04 (+0.6) | −0.03 (−0.5) | −0.05 (−0.8) | 2.6 |
| Work Rate | −0.05 (−0.8) | +0.07 (+1.1) | +0.03 (+0.5) | −0.06 (−1.1) | −0.01 (−0.2) | 3.4 |
| **Mean of the ten** | +0.14 | +0.17 | +0.13 | +0.11 | +0.07 | |

- **No attribute differs between pairings:** every chi-square is below the 5% line, and all ten together give 32.0 on
  40 degrees of freedom (p 0.81). Points instead of xPts give the same answer (p 0.94).
- **The same attributes lead everywhere:** Acceleration and Jumping Reach are the top two in every pairing, with Pace
  third or fourth. Concentration, Composure and Work Rate are the bottom three in every pairing.
- **Rankings agree closely.** Rank correlation with middle v middle: 0.90 (top v top), 0.94 (bottom v bottom), 0.94
  (favourite), 0.79 (underdog).
- **Three comparisons, all nil.** Taking the four pairings of top and bottom squads as a two-by-two:
  - **The tested squad's own strength** (top against bottom, whoever the opponent): no attribute differs (all
    |t| ≤ 1.8).
  - **The opponent's strength:** no attribute differs (all |t| ≤ 1.4).
  - **The gap** (favourite against underdog): no attribute differs (all |t| ≤ 1.6).

## The underdog: a lead

| Mean of the ten, per game | top v top | middle v middle | bottom v bottom | favourite | underdog |
|---|---|---|---|---|---|
| xPts | +0.14 | +0.17 | +0.13 | +0.11 | +0.07 |
| xG for | +0.13 | +0.22 | +0.07 | +0.07 | −0.03 |
| xG against | −0.13 | −0.06 | −0.15 | −0.09 | −0.16 |
| Goals for | +0.20 | +0.29 | +0.07 | +0.20 | −0.05 |
| Goals against | −0.03 | +0.01 | −0.17 | −0.13 | −0.26 |

- **Better players help an underdog defend,** not attack: the average +5 does not raise its xG or goals, but lowers
  what it concedes by about as much as in any other pairing.
- **The favourite gains at both ends.**
- **Not established:** favourite against underdog differs by +0.25 goals for (t 1.9) and +0.10 xG for (t 1.3). It is
  plausible (an underdog has less of the ball in dangerous areas to use its attacking attributes), but it needs more
  seeds before anyone relies on it.

## So: does strength change the rankings?

**No, neither the strength of both sides nor the gap between them.** Within the Premier League range of squads
tested here, an attribute table measured with equal sides applies to a dominant side and to an underdog. The sizes
may shrink slightly for an underdog, especially for attacking attributes, but the order does not change.

## Caveats

- **A moderate range of strength.** The reference squads span the Premier League's top, middle and bottom eight;
  CA medians differ by 17. A Champions League side against a League Two side is outside this range.
- **One style for the tested side** (Gegenpress), against four presets.
- **160 pairs per condition.** Enough to rule out large differences between pairings (about ±0.15 xPts at 95%), not
  small ones.
- **Expected points.** Attributes that act on finishing (Strength, Study 12) are not among the ten.
- **Tactic rankings by strength** are not tested here; see Study 19.

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 14 runs/study14
.venv/bin/python port/validation/neutral_study.py pilot runs/study14 --workers 7
.venv/bin/python port/validation/neutral_study.py run runs/study14 --workers 7      # about 1.3 hours with 7 workers
.venv/bin/python port/validation/neutral_study.py report runs/study14
```

The heterogeneity tests are inverse-variance chi-squares across the five pairings, which use different squads and so
are independent. The mean of the ten is computed match by match.
