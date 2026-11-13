# Study 17: positions in and out of possession

**Status:** done (13 November, 3,200 matches, plus 1,600 in the follow-up 17b). Asked on FM Arena, untested so far:
FM26 and FM27 give each player a position in possession and one out of possession. Is a player penalised for being
unfamiliar with his out-of-possession position, or only with his in-possession one?

**In short: neither, measurably.** For players whose two positions differ, capping the in-possession rating, the
out-of-possession rating or both at 10 changes nothing measurable.

A follow-up (17b) found why, and corrected what Study 5 implied:
- **The ratings of a player's own positions matter little:** −0.10 xPts per game with all ten outfield starters at 10
  in theirs (t −2.4).
- **The ratings of the positions he does *not* play matter more:** capping every position rating at 10 costs −0.30
  (t −7.0), with less possession and fewer passes completed.
- **For the goalkeeper, the position rating is shot-stopping:** a keeper at 10 makes 0.7 fewer saves per game and
  concedes 0.7 more goals, at the same xG.

## Design

- **Neutral ground,** as in the other roadmap studies:
  - The synthetic Premier League middle-eight squad on both sides.
  - Tactical familiarity held at 80.
  - Four preset opponents, home and away.
  - Two template matches between other clubs.
- **Study 17: two presets whose shapes differ in and out of possession.**
  - **Fluid Counter-Attack:** four starters move: MC to DM, MC to ST, AMR to MR, AML to ML.
  - **Vertical Tiki-Taka:** three move: MC to ML, MC to MR, AMC to DM.
  - **Starting point:** those players start natural (20) in both their positions, in every condition including the
    unchanged one.
  - **Conditions:** the in-possession rating, the out-of-possession rating, or both capped at 10.
  - **Paired:** 50 seeds, giving 400 pairs per condition.
- **Study 17b: where the cost of playing out of position comes from.**
  - **Conditions,** with Gegenpress and the squad's own ratings, each capped at 10:
    - the outfield starters' own positions (in and out of possession);
    - every position rating of the outfield starters;
    - every position rating of the goalkeeper;
    - every position rating of every starter, as in Study 5.
  - **Paired:** 40 seeds, giving 320 pairs per condition.

## Study 17: in, out or both

Per game against the same matches unchanged; t in brackets (|t| ≥ 4 established, 3-4 likely, below that unconfirmed).

| Style | Rating capped at 10 | xPts | xG difference | Points | Shots | Shots against |
|---|---|---|---|---|---|---|
| Fluid Counter-Attack | in possession | +0.00 (+0.0) | −0.01 (−0.1) | −0.02 (−0.2) | +0.2 | −0.0 |
| | out of possession | +0.04 (+1.0) | +0.05 (+1.0) | +0.03 (+0.3) | +0.3 | −0.4 |
| | both | −0.02 (−0.5) | −0.04 (−0.6) | −0.07 (−0.8) | −0.2 | −0.1 |
| Vertical Tiki-Taka | in possession | +0.02 (+0.6) | +0.03 (+0.4) | +0.02 (+0.2) | +0.5 | +0.0 |
| | out of possession | +0.02 (+0.4) | +0.02 (+0.3) | +0.03 (+0.4) | −0.1 | +0.0 |
| | both | −0.01 (−0.3) | −0.03 (−0.5) | −0.07 (−0.8) | +0.1 | +0.2 |

For three or four players, being unfamiliar with either of their positions costs nothing measurable. The standard
errors are about 0.04 xPts, so a cost of 0.1 per game would have shown.

The ratings are read: every capped match plays out differently from the unchanged one. Their effect is just too
small to measure here. The effectiveness records, the per-player values tactical familiarity feeds, are
byte-identical with and without the caps, so the familiarity hold does not hide anything.

## Study 17b: where the cost comes from

| Position ratings capped at 10 | xPts | xG difference | Points | Goals against | Saves | Possession | Pass completion |
|---|---|---|---|---|---|---|---|
| Outfield starters, own positions | −0.10 (−2.4) | −0.16 (−2.3) | −0.07 (−0.8) | +0.05 | +0.2 | −0.4 pts | −0.2 pts |
| Outfield starters, every position | **−0.30 (−7.0)** | −0.47 (−6.5) | −0.35 (−3.6) | +0.13 | +0.2 | **−1.9 pts** | **−1.0 pts** |
| Goalkeeper, every position | −0.12 (−2.8) | −0.18 (−2.6) | **−0.54 (−5.3)** | **+0.70 (+7.6)** | **−0.73 (−5.1)** | −0.8 pts | +0.0 pts |
| Every starter, every position (Study 5) | **−0.37 (−8.8)** | −0.59 (−8.4) | **−0.65 (−6.8)** | +0.48 | −0.1 | −2.4 pts | −1.1 pts |

- **Own positions: a small cost.** Ten outfield players at 10 in the positions they actually take lose about 0.10
  xPts per game (t −2.4, unconfirmed). That is consistent with Study 17's nil for three or four players.
- **Other positions: the bigger cost.** Capping all fifteen ratings of the outfield starters costs three times as
  much (−0.30 xPts, t −7.0). The side keeps the ball less (−1.9 points of possession), completes fewer passes and
  takes two fewer shots per game.
  - **The likeliest reading:** players move through other zones during play (a winger cutting inside, a midfielder
    arriving in the box), and the engine uses the rating for the zone a player is in, not only for his slot.
  - **Why it's hard to see in the game:** ratings for other positions are rarely all low, so it shows only when they
    are capped together.
- **Goalkeeper: the position rating is shot-stopping.** With the keeper's goalkeeping rating at 10:
  - shots on target against don't change;
  - he makes 0.73 fewer saves per game and concedes 0.70 more goals;
  - xG against barely moves.

  So xPts hardly sees it (−0.12), while points fall by 0.54 per game, about 20 points a season.
- **Study 5's "capping positions at 10 costs 0.85 points per game"** combined these: the goalkeeper's rating and
  the outfield players' other-position ratings. Here the same condition costs 0.65 points per game (Study 5 used the
  team's real matches; this uses neutral ground). The outfield players' own positions are the smallest part.

## So: in, out or both?

- **Within a match,** an unfamiliar in-possession or out-of-possession position costs little for one player or a few,
  and there's no sign that one costs more than the other.
- **What costs more is a player who is poor in every position** around his own. A player who is natural in his slot
  but has very low ratings for neighbouring positions is worth less than his slot rating suggests.
- **The goalkeeper's rating is part of his shot-stopping:** a natural keeper matters, not only his goalkeeping
  attributes. Study 21 measures those attributes one at a time.

## Caveats

- **Familiarity is held at 80** for both sides. Position familiarity can also feed the tactical-familiarity build-up
  over weeks in the game, which a single match does not show.
- **Three or four players in Study 17,** two presets, one squad. A tactic where most players change position between
  phases could show more.
- **The "other positions" reading is a hypothesis.** The study shows that the ratings of unplayed positions matter,
  not exactly how the engine uses them.
- **The assistant manages both sides.** If it uses position ratings for substitutions or positional changes, part of
  the cost could come from those decisions.

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 17 runs/study17      # and 17b for the follow-up
.venv/bin/python port/validation/neutral_study.py pilot runs/study17 --workers 7
.venv/bin/python port/validation/neutral_study.py run runs/study17 --workers 7   # about 25 minutes with 7 workers
.venv/bin/python port/validation/neutral_study.py report runs/study17
```

The specifications (`s17`, `s17b`) are in `port/validation/roadmap_studies.py`. The record comparison uses the host's
research switch `FM27_MAC_RECORD_SUMMARY=1` (see docs/RESEARCH.md).
