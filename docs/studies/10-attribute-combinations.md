# Study 10: are attributes worth more together?

**Status:** done (12 November, 21,600 matches). Asked by two Reddit readers. One asked whether Passing would still
make a negligible difference "if you also increased vision, technique and decisions". The other suggested that
"maybe dribbling, concentration, long shots and balance become far more powerful together".

**In short: no.** Attributes add up. Each group of four, raised together, is worth what its four members are worth
one at a time, give or take a few hundredths of a point. No group shows a synergy that can be told apart from zero
(every |t| is 1 or below). What makes a group strong is one or two strong members:
- **Ball carrying:** Dribbling, Balance and Concentration.
- **Aerial:** Jumping Reach alone.
- **Defending:** Anticipation alone.
- **Playmaking:** worth nothing measurable, alone or together.

## Design

- **Four groups of four attributes:**
  - **Playmaking:** Passing, Vision, Technique, Decisions.
  - **Ball carrying:** Dribbling, Balance, Concentration, Long Shots.
  - **Defending:** Tackling, Marking, Positioning, Anticipation.
  - **Aerial:** Jumping Reach, Heading, Strength, Bravery.
- **Conditions:** each attribute +5 alone, and the whole group +5 together, for the whole squad (in-game points,
  capped at 20).
  - **Gegenpress:** all four groups.
  - **Tiki-Taka:** the playmaking group again, where it should matter most if anywhere.
- **Neutral ground,** as in Studies 7 and 9:
  - Both sides use the same synthetic reference squad (Premier League middle eight) and start alike.
  - Tactical familiarity is held at 80.
  - Two template matches between other clubs supply only the stadium and conditions.
- **Opponents:** four presets (Gegenpress, Control Possession, Park the Bus, Route One), home and away.
- **Paired:** 100 seeds for each condition, opponent and venue, giving 800 pairs per condition.
- **Synergy:** (group effect) − (sum of the four single effects), computed match by match.
  - Every condition replays the same unchanged matches, so the standard error comes straight from the paired data.
  - A sum of four noisy effects has a wide standard error, which is why this study used 100 seeds, twice Study 9's.

## Is a group worth more than the sum of its parts?

Per game; t in brackets (|t| ≥ 4 established, 3-4 likely, below that unconfirmed). Per season: multiply by 38.

| Style | Group | Group +5: xPts | Sum of the four singles | Synergy: xPts | Synergy: xG difference |
|---|---|---|---|---|---|
| Gegenpress | Playmaking | +0.02 (+0.9) | −0.01 (−0.2) | +0.04 (+0.5) | +0.04 (+0.4) |
| Gegenpress | Ball carrying | **+0.23 (+8.9)** | +0.19 (+2.3) | +0.05 (+0.7) | +0.06 (+0.5) |
| Gegenpress | Defending | +0.08 (+3.2) | +0.07 (+0.8) | +0.02 (+0.2) | +0.02 (+0.1) |
| Gegenpress | Aerial | **+0.23 (+8.9)** | +0.24 (+3.0) | −0.01 (−0.1) | −0.02 (−0.2) |
| Tiki-Taka | Playmaking | −0.01 (−0.3) | −0.08 (−0.9) | +0.07 (+1.0) | +0.07 (+0.6) |

- **No synergy anywhere.** The largest is +0.07 xPts for playmaking under Tiki-Taka, with t 1.0.
- **The groups that pay, pay because of their members.** Ball carrying and aerial are each worth about +0.23 xPts
  per game (about 9 points a season), and so are their four members added up.
- **The test is sharp enough to matter.** A synergy as large as the second reader suggested ("far more powerful
  together") would have to be several tenths of a point. The standard errors here are about 0.08 xPts, so a synergy
  of 0.15 or more would have shown.

## Which members carry each group

Gegenpress, each attribute +5 alone (xPts per game, t in brackets):

| Group | Attribute | xPts | xG difference | Shots | Shots against |
|---|---|---|---|---|---|
| Playmaking | Passing | −0.03 (−0.9) | −0.04 | −0.1 | −0.1 |
| | Vision | +0.02 (+1.0) | +0.04 | +0.2 | −0.2 |
| | Technique | −0.03 (−1.1) | −0.03 | +0.1 | +0.1 |
| | Decisions | +0.02 (+0.6) | +0.03 | +0.2 | +0.0 |
| Ball carrying | Dribbling | +0.07 (+2.7) | +0.13 | +1.1 | −0.1 |
| | Balance | +0.08 (+3.0) | +0.14 | +0.4 | −0.5 |
| | Concentration | +0.05 (+1.8) | +0.09 | +0.5 | −0.4 |
| | Long Shots | −0.01 (−0.4) | −0.01 | +0.2 | −0.1 |
| Defending | Tackling | −0.01 (−0.3) | +0.00 | +0.0 | +0.0 |
| | Marking | −0.01 (−0.4) | −0.01 | +0.0 | −0.0 |
| | Positioning | −0.03 (−1.0) | −0.03 | +0.1 | +0.1 |
| | Anticipation | **+0.11 (+4.2)** | +0.19 | +1.0 | −0.5 |
| Aerial | Jumping Reach | **+0.22 (+8.3)** | +0.38 | +2.0 | −1.0 |
| | Heading | −0.00 (−0.0) | −0.00 | +0.3 | +0.2 |
| | Strength | −0.01 (−0.2) | +0.02 | +0.2 | +0.1 |
| | Bravery | +0.03 (+1.1) | +0.04 | +0.1 | −0.1 |

- **Jumping Reach is the whole aerial group:** +0.22 alone against +0.23 for all four. Heading, Strength and Bravery
  add nothing measurable.
- **Anticipation is the whole defending group,** and works at both ends: about one more shot per game, and half a
  shot fewer against.
- **Ball carrying is shared** between Dribbling (more shots), Balance (fewer shots against) and Concentration, with
  Long Shots contributing nothing.
- **Playmaking is worth nothing measurable** under either style, alone or together. With the group raised, the side
  keeps the ball slightly less (−0.8 points of possession under Gegenpress, −1.0 under Tiki-Taka) and completes
  fewer passes, as in Study 9.
- Several single attributes show +0.10 to +0.16 *points* per game with t about 2 (for example Tackling, Heading and
  Strength) but no change in xPts. With 20 conditions a few of these are expected by chance. Read them as finishing
  noise, not effects.

## Compared with Study 9

Study 9's passing group was worth +0.11 xPts under Gegenpress. It held six attributes: these four, plus First Touch
and Composure. Here the four-attribute playmaking group is worth +0.02. That suggests the passing value in Study 9
came mostly from First Touch and Composure. It is a comparison between two studies, not a test; Study 12 (each
attribute at eight levels) includes both and will check it.

## Caveats

- **+5 for the whole squad.** Synergy between a player's own attributes and synergy between players are not told
  apart. Raising a group for one position only is Study 13's question.
- **One squad, two styles.** A mid-table Premier League squad; the Tiki-Taka run covers only the playmaking group.
- **Additive on this scale.** A step of +5 from a mid-table base. Combinations could behave differently near the
  extremes (for example from very low values), which Study 12 looks at one attribute at a time.
- **Tactical familiarity is held at 80** for both sides, and tactical complexity is not recomputed by the match
  engine (see the main README).

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 10 runs/study10        # checks every condition
.venv/bin/python port/validation/neutral_study.py pilot runs/study10 --workers 7
.venv/bin/python port/validation/neutral_study.py run runs/study10 --workers 7   # resumable; about 3 hours with 7 workers
.venv/bin/python port/validation/neutral_study.py report runs/study10
.venv/bin/python port/validation/synergy.py runs/study10
```

The study's specification is in `port/validation/roadmap_studies.py`. The template matches are any saved matches
between other clubs (for example from `scripts/import_other_matches.py`); only their stadium and conditions are used.
