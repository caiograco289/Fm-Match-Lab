# Study 15: home advantage and morale

**Status:** done (13 November, 2,480 matches). Two things often asserted and rarely measured cleanly:
- How big is home advantage in FM27, and does it depend on the ground?
- How much does morale matter within a match? Study 5 had found morale small.

**In short:**
- **Home advantage is real and about the size of real football's.** With identical squads and tactics, the home
  side takes 1.54 points per game and the away side 1.18:
  - +0.21 xG and +0.28 goals per game for the home side;
  - +1.3 shots per game.
- **It differs between grounds** more than chance allows. Two of the twelve give about +0.5 xG; one gives none.
  The size does not follow the level of the club, from the Premier League to non-league.
- **Morale makes no measurable difference:** morale 5, 10 and 20 against the usual 15 all within ±0.04 xPts (|t| < 1).

## Design

### Home advantage

- **Identical sides:**
  - Both teams are the same synthetic squad (Premier League middle eight), both play the Gegenpress preset, and both
    start alike with tactical familiarity held at 80.
  - The only difference between the two sides is which one is at home.
- **Twelve grounds:** saved matches between other clubs, used only for their stadium and conditions. They run from
  the Premier League to non-league:
  - Arsenal v Fulham, Everton v Newcastle United, Leeds United v Tottenham Hotspur, Burnley v West Ham United,
    Brentford v Southampton;
  - Birmingham City v Bolton Wanderers, Bristol Rovers v Oldham Athletic, Barnet v Colchester United;
  - Boreham Wood v Woking, Chester v Yeovil Town, Dartford v Ebbsfleet United, AFC Fylde v Boreham Wood.
- **Seeds:** 100 per ground, 1,200 matches.
- **What it measures:** with identical sides, any difference between home and away is home advantage. That includes
  everything the engine attaches to playing at home: crowd, familiarity with the ground, and any home-side rule.

### Morale

- **The usual neutral-ground set-up:** four preset opponents, home and away, two templates.
- **Levels:** the tested side's morale set to 5, 10 or 20, against the equal start of 15.
- **Paired:** 40 seeds, giving 320 pairs per level.

## Home advantage

| | Home | Away | Difference (t) |
|---|---|---|---|
| Points per game | 1.54 | 1.18 | +0.36 |
| xG | 1.65 | 1.45 | +0.21 (+7.4) |
| Goals | | | +0.28 (+5.7) |
| xPts | | | +0.23 (+7.4) |
| Shots | | | +1.3 (+7.9) |
| Possession | 50% | 50% | −0.3 points (−1.9) |
| Cards | | | +0.02 (+0.4) |

- **Comparable to real football.** In recent Premier League seasons home sides have taken about 1.5-1.6 points per
  game and away sides about 1.1-1.2, scoring about 0.3 goals more.
- **It comes from chances, not possession:** the home side has the same share of the ball but 1.3 more shots.
- **Referees don't take sides.** Cards are equal, so the engine does not give the home side a refereeing edge.

## By ground

Home minus away, per game; t in brackets:

| Ground (template) | xG difference | Goal difference | Home points | Home W / D / L |
|---|---|---|---|---|
| Arsenal v Fulham | **+0.57 (+5.7)** | +0.72 (+3.9) | 1.69 | 48 / 25 / 27 |
| Leeds United v Tottenham Hotspur | **+0.47 (+5.2)** | +0.79 (+4.2) | 1.87 | 56 / 19 / 25 |
| AFC Fylde v Boreham Wood | +0.27 (+2.4) | +0.45 (+2.6) | 1.66 | 47 / 25 / 28 |
| Bristol Rovers v Oldham Athletic | +0.23 (+2.3) | +0.15 (+1.1) | 1.42 | 37 / 31 / 32 |
| Chester v Yeovil Town | +0.21 (+2.0) | +0.10 (+0.6) | 1.52 | 41 / 29 / 30 |
| Burnley v West Ham United | +0.18 (+2.1) | +0.00 (+0.0) | 1.33 | 31 / 40 / 29 |
| Birmingham City v Bolton Wanderers | +0.15 (+1.7) | +0.01 (+0.1) | 1.37 | 36 / 29 / 35 |
| Dartford v Ebbsfleet United | +0.13 (+1.3) | +0.44 (+2.6) | 1.68 | 49 / 21 / 30 |
| Brentford v Southampton | +0.12 (+1.2) | +0.35 (+2.0) | 1.54 | 43 / 25 / 32 |
| Barnet v Colchester United | +0.08 (+1.0) | −0.01 (−0.1) | 1.44 | 40 / 24 / 36 |
| Boreham Wood v Woking | +0.06 (+0.7) | +0.19 (+1.3) | 1.55 | 41 / 32 / 27 |
| Everton v Newcastle United | +0.02 (+0.2) | +0.11 (+0.7) | 1.40 | 36 / 32 / 32 |

- **Grounds differ:** the spread in xG difference is larger than chance (heterogeneity Q = 32.8 on 11 degrees of
  freedom, p about 0.001).
- **Not by level:** the five top-flight grounds average +0.27 xG and the seven lower and non-league grounds +0.16. That
  gap comes entirely from Arsenal and Leeds United; the Everton and Brentford grounds give less than most non-league
  ones.
- **What makes a ground strong is not known.** Each template brings its own stadium, pitch, weather and recorded
  crowd, and the match input has no attendance or crowd field that can be changed. So crowd and stadium can't be
  separated here.
- **Why this matters for other studies:**
  - Every neutral-ground study pairs each condition with the same template and venue, so ground effects cancel.
  - They do mean single-template results carry a little ground-specific colour; the studies use two to four
    templates for this reason.

## Morale

| Morale (tested side) | xPts | xG difference | Points | Shots | Shots against |
|---|---|---|---|---|---|
| 5 | −0.03 (−0.7) | −0.04 (−0.5) | +0.06 (+0.5) | −0.1 | +0.4 |
| 10 | −0.04 (−0.9) | −0.05 (−0.7) | +0.03 (+0.3) | −0.1 | +0.3 |
| 20 | +0.03 (+0.8) | +0.07 (+0.9) | +0.10 (+1.0) | +0.6 | −0.1 |

Against the equal start of 15, very low or very high morale changes nothing measurable within a match. The direction
is the expected one (low worse, high better), but the whole range is under 0.1 xPts per game, as Study 5 found.

## Caveats

- **Home advantage with one squad and one tactic** (a Gegenpress mirror). A stronger or weaker side, or other styles,
  could gain more or less at home.
- **Ground, not crowd:** the twelve grounds differ in everything at once. The study can say grounds differ, not why.
- **Morale at kick-off only.** In the game morale also moves during the match and over a season, through results,
  team talks and the dressing room; only the starting value was set here.
- **Within a match.** Morale's effects over a season (training, form, transfer requests) are not measured.

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 15 runs/study15
.venv/bin/python port/validation/neutral_study.py pilot runs/study15 --workers 7
.venv/bin/python port/validation/neutral_study.py run runs/study15 --workers 7     # about 20 minutes with 7 workers
.venv/bin/python port/validation/neutral_study.py report runs/study15
```

The by-ground table comes from `results.jsonl` (the "Home advantage" rows, template index in the condition string):
home minus away xG, goals and points per template.
