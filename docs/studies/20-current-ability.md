# Study 20: does Current Ability play a role in the match?

**Status:** done (12 November, 5,760 matches). Asked because a long-time FM Arena researcher reported that new
reverse engineering, shared on another forum, found that "CA plays a big role in the match engine for technical and
mental attributes". Study 5 had found nothing clear for CA ±20 with every attribute fixed (t ≤ 1.5); this study
covers the whole range.

**In short: no.**
- **No effect on results:** with every attribute fixed, setting the whole squad's Current Ability anywhere from 40 to
  200 changes nothing measurable, for one side or both.
- **No effect on attribute values:** CA does not change what an attribute is worth. Passing +5 and Decisions +5 are
  worth the same at CA 60 as at CA 180.
- **CA is still read during the match.** Changing it changes how individual matches unfold, but not their average
  outcome.

## Where the engine reads Current Ability (first step)

Before running anything, one match was replayed at CA 40, natural and 200 (seed 1, familiarity not held), with the
host's record dump switched on:
- **Not through familiarity:** every player's effectiveness record, the per-player values that tactical familiarity
  and positions feed into, is byte-identical at all three CA values.
- **Read during play:** the matches diverge before about minute 9, with no substitutions, so the value is read during
  the match itself and not only before kick-off.

The full study measures whether that reading matters.

## Design

- **Neutral ground,** as in Studies 7, 9 and 10:
  - The synthetic Premier League middle-eight squad on both sides.
  - Tactical familiarity held at 80.
  - Four preset opponents, home and away.
  - Two template matches between other clubs, used only for the stadium and conditions.
- **Only Current Ability changes.** Every attribute stays as it is.
  - The squad's own CA runs from 124 to 154 (median 138).
- **One side:** the whole squad's CA set to 40, 60, 80, 120, 160, 180 or 200, against the unchanged opponent.
- **Both sides:** CA 40, 80, 120, 160 or 200 for both squads.
- **CA with attributes:** Passing +5 or Decisions +5 at CA 60 and at CA 180.
- **Paired:** 40 seeds, giving 320 pairs per condition, each against the same match with the squad unchanged.

## CA alone

Per game against the same matches unchanged; t in brackets (|t| ≥ 4 established, 3-4 likely, below that unconfirmed).

| CA (whole squad) | One side: xPts | One side: xG difference | Both sides: xPts | Both sides: xG difference |
|---|---|---|---|---|
| 40 | −0.01 (−0.2) | −0.02 (−0.3) | −0.00 (−0.1) | +0.01 (+0.1) |
| 60 | −0.02 (−0.4) | −0.01 (−0.2) | · | · |
| 80 | −0.03 (−0.8) | −0.03 (−0.5) | −0.01 (−0.3) | −0.01 (−0.1) |
| 120 | +0.00 (+0.0) | +0.03 (+0.6) | +0.04 (+1.2) | +0.09 (+1.5) |
| 160 | −0.01 (−0.3) | −0.01 (−0.2) | +0.03 (+1.0) | +0.08 (+1.4) |
| 180 | −0.01 (−0.2) | −0.00 (−0.1) | · | · |
| 200 | −0.01 (−0.2) | −0.00 (−0.1) | −0.01 (−0.2) | +0.01 (+0.1) |

- **Flat across the range.** A side with CA 40 does as well as one with CA 200 when the attributes are the same.
- **No trend:** the slope of xG difference over CA is +0.015 per 100 CA (t 0.3) for one side.
- **Small enough to rule out "a big role":** the standard errors are about 0.04 xPts, so an effect of 0.1 xPts per
  game (about 4 points a season) would have shown at any level.
- Shots, possession and pass completion don't move either (all within ±0.5 shots and ±0.3 points of possession).

## Does CA change what attributes are worth?

The claim was specifically about technical and mental attributes, so Passing (technical) and Decisions (mental) +5
were tested at a low and a high CA:

| Attribute +5 | at CA 60: xG difference | at CA 180: xG difference | Difference (180 − 60) |
|---|---|---|---|
| Passing | −0.00 (−0.0) | +0.00 (+0.0) | +0.01 (t 0.1) |
| Decisions | +0.08 (+1.1) | +0.11 (+1.6) | +0.04 (t 0.4) |

Each attribute is worth the same at either CA. Passing +5 alone is worth nothing measurable here, as in Study 10.

## So what does CA do in the match?

It changes the course of matches without changing the results. The table counts, out of 320 pairs, the matches whose
xG for and against are exactly as in the unchanged match:

| CA | 40 | 60 | 80 | 120 | 160 | 180 | 200 |
|---|---|---|---|---|---|---|---|
| One side: identical matches | 0 | 0 | 0 | 63 | 173 | 135 | 105 |
| Both sides: identical matches | 0 | · | 0 | 1 | 36 | · | 28 |

- **Below the squad's own range (124-154):** every match plays out differently.
- **Above it:** a third to a half of matches are unchanged.

So the engine compares CA with something, probably a threshold or a value derived from the attributes, and acts when
it falls below. What it acts on is not known. Possible readings:
- AI decisions that rank players (who takes a set piece, who gets the ball in a choice between two players);
- an in-match check such as a mistake or morale roll.

Whatever it is, it has no measurable effect on chances or results.

## Caveats

- **Attributes fixed.** In the game CA and attributes move together, because CA is largely computed from
  attributes. This study separates them; it says the *field* CA does nothing measurable, not that better players
  (higher attributes) don't matter.
- **One squad, one style.** Mid-table Premier League, Gegenpress; whole squad changed at once.
- **The AI manages both sides.** If CA affects the human manager's information (for example star ratings), that is
  outside the match engine and not tested.
- **Outside a single match:** a CA effect on injuries, condition over a season, development or
  reputation is not part of a single match and not tested.

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 20 runs/study20
.venv/bin/python port/validation/neutral_study.py pilot runs/study20 --workers 7
.venv/bin/python port/validation/neutral_study.py run runs/study20 --workers 7    # about 45 minutes with 7 workers
.venv/bin/python port/validation/neutral_study.py report runs/study20
```

The record comparison uses the host's research switch `FM27_MAC_RECORD_SUMMARY=1` (see docs/RESEARCH.md).
