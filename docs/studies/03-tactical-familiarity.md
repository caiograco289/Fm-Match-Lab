# Study 3: tactical familiarity

**Status:** done. Step 0 found what familiarity is inside the engine; step 1 measured how much each part matters
(10 November, 6,900 matches).

## Step 0: what "familiarity" is in FM27

FM27 no longer shows a familiarity bar per tactical area. It shows **Tactical Effectiveness** (Training > Tactical
Effectiveness), in four parts: Tactical Understanding (Tactical Areas and Tactical Comprehension), Player Ability,
Player Buy-In and Next Match Info. Inside the match engine, each player carries a 33-byte record that the engine
builds before kick-off and reads during play. The engine function that reads it was decoded earlier
(`port/map/exec_record.py`, exact on 20,000 test records).

To find out which record bytes the panel shows, we used screenshots of the panel before two matches
(Team v Chelsea, 13 Oct; Man City v Team, 16 Oct; same tactic). Both matches were replayed and the
records dumped. The panel shows each value only as a segmented pie, so the check measures each pie's filled share and
compares the order of players with the record.

| Panel item | Record bytes | Agreement with the pies |
|---|---|---|
| Tactical Areas (8: In Possession Shape, Passing Style, Build Up, Chance Creation, Out Of Possession Shape, Line Of Engagement, Pressing Intensity, Pressing Trap) | the 8 triples at +0x01 to +0x18, one per area, in that order | the pie follows the player's average engine value over the action categories: 21 of 22 player-matches in order (one at a bucket edge) |
| Tactical Comprehension: Player Tactical Ability and Tactical Complexity | byte +0x00 (player tactical ability); +0x19 (team complexity: the team 78, Chelsea 4); +0x1a (per-role complexity) | ¼·(100 − complexity score) + ¼·tactical ability, the engine's own player-level term, splits the pies exactly at 25: 22 of 22 |
| Player Tactical Ability (inside Comprehension) | +0x00 = (median of Anticipation, Decisions, Composure, Concentration and Versatility on the 1–20 scale − 1) × 100/19 | exact for all 44 players of both teams in both matches |
| Player Ability: Capability and Role Suitability | +0x1c and +0x1d | follows capability × suitability |
| Player Buy-In | +0x1f | exact order: 48 → lowest pie (the one player with an orange icon), 87 → highest; 22 of 22 |
| Next Match Info | +0x20 | exact: 54 and 58 → lower pie (three players), 62+ → higher; 22 of 22 |

Two more findings:

- **Each area has two values: match exposure and training.** A forum post on FM27's Tactical Effectiveness describes
  each area score as tactical ability + tactic simplicity + match exposure + training contribution for that area.
  The record fits that:
  - Byte 2 of each triple rose by about 2 for every starter in every area after the Chelsea match, and stopped at
    100 where it was already 99. That is **match exposure**.
  - Byte 1 (copied in byte 0) moved only in some areas: it fell for most players in Chance Creation and Pressing
    Trap. That is the **training contribution**, which presumably fades for areas that are not trained.
  - The engine weights training twice as much as exposure (0.6 against 0.3 in this record mode). Tactical ability
    and simplicity each count 0.25.
  - The team's tactic is complex: team complexity 78, against 4 for Chelsea's. That costs every player about 20 points
    of effectiveness in every area before training and exposure are added.
  - The same post's tactical-ability formula is confirmed exactly (table above).
  - Its weights for the headline number (Understanding 50%, Ability 10%, Buy-In 25%, Next Match 15%) describe the
    panel. The match itself does not read that headline number.
- **The AI side has no per-area detail.** For Chelsea, all four in-possession areas share one value and all four
  out-of-possession areas share another.

### What the engine reads, and what it ignores

The earlier experiments (`port/REPORT.md`) already showed which parts matter, without knowing their names:

- **Read during play:** the area values, tactical ability and complexity. Raising all of them together to 90 was
  worth +0.23 points per game and +0.37 xG difference on these matches. Setting them to 30 changed nothing.
- **Ignored by the match:** Player Ability (capability, role suitability) and the overall value. Setting them to 10,
  50 or 90 gives exactly the natural match.
- **No measurable effect alone:** Buy-In and Next Match Info, held at 30 or 90 (|t| < 1.7). They may feed the panel's
  headline number, or matter only through other bytes when the game rebuilds the record day by day.

So "familiarity" in FM27 is the **Tactical Understanding** half of the panel: for each of the eight areas, training
plus match exposure, plus the player's tactical ability, minus how complex the tactic is for his role.

**For the attribute studies:** Anticipation, Decisions, Composure, Concentration and Versatility also act through
tactical ability, but only through their median. Raising one of them changes effectiveness only if it moves the
median. Study 4 can test this directly.

## Step 1: dose-response (done, 10 November; 6,900 matches)

### Design

On the 10 real matches × seeds 1-30 (300 pairs per condition, the Study 1 design), every team player's record
is held at one value, written between engine steps (data writes only). Each condition is compared with the unchanged
match on the same seeds.

| Condition | Bytes | Levels | Natural range (the squad) |
|---|---|---|---|
| exposure (matches played) | byte 2 of the 8 areas | 0, 25, 50, 75, 100 | 13-99 |
| training | bytes 0-1 of the 8 areas | 0, 25, 50, 75, 100 | 17-67 |
| both (whole area) | all 24 area bytes | 0, 50, 100 | |
| team complexity | +0x19 | 0, 50, 100 | 78 |
| role complexity | +0x1a | 0, 100 | 22-100 |
| player tactical ability | +0x00 | 25, 50, 75, 100 | 58-74 |

"0" is the floor of the scale, not a realistic brand-new tactic.

**Determinism check:** the 300 unchanged matches are identical to Study 1's, score and xG, match for match. (FM27 was
briefly open during Study 1; it made no difference.)

### Results

Difference from the unchanged match, per game, for the team (t in brackets):

| Condition | Points | xG difference | xG for | xG against | Goals for | Goals against |
|---|---|---|---|---|---|---|
| training 0 | **−0.40 (−4.1)** | **−0.46 (−5.4)** | −0.24 | +0.23 | −0.32 | +0.24 |
| training 25 | −0.02 | −0.07 (−0.8) | −0.02 | +0.06 | −0.08 | −0.01 |
| training 50 | +0.11 (1.2) | +0.21 (2.5) | +0.15 | −0.06 | +0.09 | −0.08 |
| training 75 | **+0.21 (2.3)** | **+0.38 (4.5)** | +0.22 | −0.16 | +0.21 | −0.12 |
| training 100 | **+0.22 (2.2)** | **+0.31 (3.5)** | +0.19 | −0.12 | +0.21 | −0.21 |
| exposure 0 | **−0.29 (−2.9)** | −0.22 (−2.7) | −0.09 | +0.13 | −0.26 | +0.17 |
| exposure 25 | +0.01 | +0.05 (0.5) | +0.03 | −0.02 | +0.01 | −0.09 |
| exposure 50 | +0.04 | +0.23 (2.8) | +0.12 | −0.11 | +0.11 | −0.16 |
| exposure 75 | −0.02 | +0.13 (1.5) | +0.09 | −0.04 | +0.03 | +0.01 |
| exposure 100 | 0.00 | **+0.31 (3.4)** | +0.21 | −0.09 | +0.15 | −0.10 |
| both 0 | **−0.33 (−3.3)** | **−0.47 (−5.5)** | −0.23 | +0.25 | −0.31 | +0.28 |
| both 50 | +0.19 (2.0) | **+0.28 (3.2)** | +0.19 | −0.09 | +0.14 | −0.11 |
| both 100 | +0.18 (1.9) | **+0.34 (3.9)** | +0.20 | −0.14 | +0.12 | −0.26 |
| tactical ability 25 | −0.01 | −0.17 (−2.1) | −0.14 | +0.02 | −0.16 | −0.14 |
| tactical ability 50 | −0.01 | −0.01 | −0.02 | −0.01 | −0.08 | 0.00 |
| tactical ability 75 | +0.21 (2.2) | +0.13 (1.6) | +0.11 | −0.02 | +0.18 | −0.14 |
| tactical ability 100 | +0.02 | **+0.24 (2.8)** | +0.14 | −0.10 | +0.09 | −0.09 |
| team complexity 0 | +0.08 | +0.15 (1.7) | +0.06 | −0.08 | −0.03 | −0.27 |
| team complexity 50 | −0.10 | +0.10 (1.1) | +0.11 | +0.01 | −0.02 | +0.04 |
| team complexity 100 | −0.03 | +0.10 (1.1) | +0.07 | −0.03 | −0.07 | −0.05 |
| role complexity 0 | +0.04 | +0.08 (1.0) | +0.05 | −0.04 | −0.03 | −0.12 |
| role complexity 100 | −0.08 | −0.02 | 0.00 | +0.01 | −0.10 | −0.05 |

### What it means

1. **Familiarity matters, and training matters most.** Taking the eight areas' training value from the squad's
   17-67 down to 0 costs about 0.4 points and 0.46 xG difference per game. Raising it to 75 gains about 0.2 points
   and 0.38 xG difference. Both ends move: more and better chances for, fewer against.
2. **Match exposure matters about half as much as training,** in line with the engine's weights (0.6 for training,
   0.3 for exposure). Zero exposure costs about 0.3 points; full exposure adds about 0.3 xG difference but no clear
   points. The middle levels are noisy.
3. **It saturates.** Training 75 and 100, and whole areas at 50 and 100, give the same result. That fits the
   engine's formula: each area value is capped at 100, and with a decent training value the cap is reached before
   training or exposure reach 100. Beyond that, extra familiarity buys nothing.
4. **The channels line up per point of area value.** Converted with the engine's weights (training 0.6, exposure 0.3,
   tactical ability 0.25), training, exposure and tactical ability are each worth roughly 0.02 xG difference per
   point of area value. That is consistent with the engine using one combined value per area.
5. **Player tactical ability counts, but less per step** (it has a 0.25 weight): 25 → 100 moves xG difference by
   about 0.4. One in-game point of the median of Anticipation, Decisions, Composure, Concentration and Versatility is
   about 5 points of this byte, so about 0.03 xG difference per point of median.
6. **Complexity has no clear effect when held alone**, which is surprising. The engine's formula gives it the same
   weight as tactical ability, but no level of team or role complexity moves results clearly (all |t| < 1.7, not in
   order). One possible explanation is that complexity is applied when the record is built, so holding the raw byte
   during the match does not change the derived area values. This is open; a save-based test (a simpler tactic
   learned the same way) would settle it.

### In practice

- A tactic your players have barely trained costs real points: up to about 0.4 per game against what the squad has
  now. Training the tactic matters more than playing matches with it.
- Once the areas are well trained (around 75), further training is wasted for the match. Time is better spent
  elsewhere.
- Do not count on a simpler tactic making up for a lack of training: this study cannot show a benefit from lower
  complexity (see point 6).

Study 4 (running) measures whether the top attributes are worth more at high familiarity than at low.

## Reproduce

```sh
# dump records for a saved match (research switch; output stays local)
FM27_MAC_RECORD_SUMMARY=1 fm27_mac_host --fixture <match.pkm> --seed <its seed> --output out.jsonl --dump-input in.json
python port/validation/study3_effectiveness.py build port/mac_host/runs/study3 port/mac_host/runs/attr_real_2701
FM27_STUDY_HOST=<frozen host> python port/validation/overnight.py run port/mac_host/runs/study3 6
python port/validation/study3_effectiveness.py analyse port/mac_host/runs/study3   # writes effects.json
```
