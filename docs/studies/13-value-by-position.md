# Study 13: what is an attribute worth in each position?

**Status:** done (13 November, 15,680 matches). **Superseded in part by [Study 13b](13b-value-by-position-random.md),**
which measures every attribute in every position far more precisely: positions do differ, and the "first players
worth more" finding below is mostly the position of those first players (a centre-back and a striker). Three questions:
- **Weights by position.** These are widely used for recruitment, but they come from regressions on season data,
  not from controlled tests. Which positions benefit most from each attribute?
- **Jumping Reach** (from FM Arena): is high Jumping Reach valuable only for defenders, or for midfielders and
  attackers too?
- **One player against the whole team.** Attribute tables are built from changes to the whole squad, and readers
  assume one player is worth one-eleventh. Is that right?

**In short:**
- **No attribute has a clearly position-specific value at this resolution.** Two players +5 in one of the eight most
  valuable attributes are worth about 0.03-0.06 expected points per game, whichever pair it is.
  - Taken together, the differences between positions are no larger than chance (p 0.12).
  - Full-backs and attacking wide players gain a little more, central midfielders least, but not significantly.
- **Jumping Reach pays in every position,** and more through chances created than through chances prevented.
  Strikers and wide attackers gain at least as much as centre-backs.
- **Not one-eleventh each.** Jumping Reach +5 for three players (a defensive midfielder, a centre-back, a striker)
  is already worth +0.14 xPts per game, two-thirds of the whole team's +0.22. The first players improved are worth
  more than the last.

## Design

- **Neutral ground,** as in the other roadmap studies:
  - The synthetic Premier League middle-eight squad on both sides, Gegenpress.
  - Tactical familiarity held at 80.
  - Four preset opponents, home and away.
  - Two template matches between other clubs.
- **By position:** the eight largest attributes in Study 1, +5 for one position group of the starting XI at a time.
  - **Attributes:** Pace, Acceleration, Jumping Reach, Stamina, Anticipation, Dribbling, Concentration, Balance.
  - **Groups, two players each:**
    - centre-backs (DCL, DCR);
    - full-backs (DL, DR);
    - defensive midfielders (DML, DMR);
    - wide attacking midfielders (AML, AMR);
    - strikers (STL, STR).
  - The goalkeeper is Study 21's subject.
- **By number of players:** Pace +5 and Jumping Reach +5 for 1, 3, 6 and 11 starters, added in this order:
  - DMR (1 player);
  - DCR, STR (3);
  - AMR, DR, DML (6);
  - DCL, STL, AML, DL, GK (11).
- **Paired:** 40 seeds, giving 320 pairs per condition, against the same matches unchanged.

## By position

Expected points (xPts) per game from +5 for the two players of each group; t in brackets (|t| ≥ 4 established, 3-4
likely, below that unconfirmed). The last column tests whether the five groups differ (chi-square on 4 degrees of
freedom; about 9.5 is the 5% line).

| Attribute | Centre-backs | Full-backs | Defensive midfield | Wide attackers | Strikers | Differ? |
|---|---|---|---|---|---|---|
| Pace | +0.03 (+0.8) | +0.08 (+1.9) | +0.01 (+0.2) | +0.01 (+0.1) | +0.09 (+2.0) | 7.7 |
| Acceleration | +0.08 (+2.0) | +0.11 (+2.7) | +0.04 (+0.9) | +0.02 (+0.5) | +0.08 (+1.9) | 6.1 |
| Jumping Reach | +0.06 (+1.5) | +0.06 (+1.5) | +0.06 (+1.4) | +0.09 (+2.1) | +0.12 (+2.7) | 2.8 |
| Stamina | +0.02 (+0.5) | +0.07 (+1.6) | −0.01 (−0.3) | +0.10 (+2.5) | +0.04 (+1.0) | 7.8 |
| Anticipation | +0.02 (+0.5) | +0.04 (+0.9) | −0.01 (−0.2) | +0.11 (+2.5) | +0.03 (+0.7) | 7.0 |
| Dribbling | −0.01 (−0.1) | +0.03 (+0.8) | −0.01 (−0.3) | +0.05 (+1.1) | +0.06 (+1.3) | 4.0 |
| Concentration | +0.07 (+1.6) | +0.08 (+1.9) | +0.04 (+1.0) | +0.04 (+0.9) | −0.00 (−0.1) | 4.5 |
| Balance | −0.01 (−0.3) | +0.01 (+0.2) | +0.03 (+0.6) | +0.01 (+0.2) | −0.02 (−0.5) | 1.5 |
| **Mean of the eight** | +0.03 (+1.1) | **+0.06 (+1.9)** | +0.02 (+0.6) | +0.05 (+1.7) | +0.05 (+1.5) | 10.3 |

- **No single attribute differs clearly between positions.** Every chi-square is below the 5% line, and over all
  eight attributes together the differences are what chance gives (41.5 on 32 degrees of freedom, p 0.12).
- **Each cell is small.** Two players +5 is about a fifth of a team, so effects of 0.03-0.10 per game are expected,
  and 320 pairs measure them to about ±0.08. This study can find large position effects, not fine weights.
- **Leads worth a rerun** (|t| 2.5-2.7, unconfirmed with 40 conditions):
  - Acceleration for full-backs;
  - Jumping Reach for strikers;
  - Stamina and Anticipation for wide attackers.
- **Averaged over the eight attributes,** full-backs and wide attackers gain most and defensive midfielders least
  (p about 0.04). That fits a Gegenpress shape where the wide players cover the most ground. It is not established.

## Jumping Reach: not only for defenders

| Jumping Reach +5 for | xG for | xG against | Goals for | Points |
|---|---|---|---|---|
| Centre-backs | +0.11 | −0.03 | +0.20 | +0.17 |
| Full-backs | +0.07 | −0.03 | +0.08 | +0.14 |
| Defensive midfield | +0.07 | −0.04 | +0.10 | +0.06 |
| Wide attackers | +0.13 | −0.05 | +0.08 | +0.18 |
| Strikers | +0.15 | −0.06 | +0.10 | +0.11 |

- **Every group gains,** and by similar amounts. There's no sign that the attribute is worth more in defence.
- **The gain comes mostly from chances created** (xG for +0.07 to +0.15), not from chances prevented (−0.03 to
  −0.06), even for centre-backs. That points to set pieces and long balls won in the opponent's half.
- **This differs from Study 1,** which found Jumping Reach's effect mostly defensive (−0.21 goals against per game).
  Study 1 used the team's real squad and matches, this a neutral squad and Gegenpress. The difference may be the
  squad's starting values (Jumping Reach 6-18 here) or the style.

## One player, three, six, eleven

| +5 for | Pace: xPts | Jumping Reach: xPts | One-eleventh each would give |
|---|---|---|---|
| 1 player (DMR) | −0.03 (−0.7) | +0.01 (+0.2) | +0.01 / +0.02 |
| 3 players (+ DCR, STR) | +0.00 (+0.0) | **+0.14 (+3.1)** | +0.04 / +0.06 |
| 6 players (+ AMR, DR, DML) | +0.12 (+2.9) | **+0.19 (+4.5)** | +0.08 / +0.12 |
| 11 players (all) | +0.14 (+3.3) | **+0.22 (+5.3)** | |

- **Jumping Reach: diminishing returns.** Three players give two-thirds of the whole team's gain, and six give most
  of it. Each departs from the one-eleventh line by +0.08 (t about 2).
  - The same shows in the position groups: their five Jumping Reach effects add up to +0.39, more than the +0.22 for
    the whole team (difference not significant, t 1.3).
  - **The reading:** in the air it matters most that *someone* wins the ball, so the second and third good jumper
    add less than the first.
- **Pace: unclear.** Nothing measurable for one or three players, then +0.12 at six and +0.14 at eleven. That is
  consistent with one-eleventh each, within the noise.
- **For readers of attribute tables:** whole-squad effects understate what the first few players are worth for
  Jumping Reach. For Pace, one-eleventh each is a fair rule of thumb on this evidence.

## One line per position (Gegenpress, leads rather than findings)

- **Centre-backs:** Acceleration, Concentration and Jumping Reach; Pace less than expected.
- **Full-backs:** Acceleration and Pace first, then Concentration and Stamina; the group that gains most overall.
- **Defensive midfielders:** nothing stands out; the group gains least from these eight attributes.
- **Wide attackers:** Anticipation, Stamina and Jumping Reach; Pace and Acceleration hardly.
- **Strikers:** Jumping Reach, then Pace and Acceleration.

## Caveats

- **Two players per group, 320 pairs.** Good enough to rule out large position-specific effects, not to give fine
  weights. A rerun of the leads above with 160 seeds would settle them.
- **One style.** Gegenpress uses no central attacking midfielder and two strikers; the wide attackers in this shape
  are AML/AMR. Other shapes could weight positions differently.
- **Expected points.** Attributes that act on finishing (Strength, as Study 12 found) are not among the eight; xPts
  would undervalue them by position as well.
- **Familiarity held at 80, starters only.** Substitutes are unchanged.

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 13 runs/study13
.venv/bin/python port/validation/neutral_study.py pilot runs/study13 --workers 7
.venv/bin/python port/validation/neutral_study.py run runs/study13 --workers 7     # about 2 hours with 7 workers
.venv/bin/python port/validation/neutral_study.py report runs/study13
```

The chi-square tests use the covariance of the condition means estimated from the paired data (all conditions share
the unchanged matches), as in `port/validation/dose_response.py`.
