# Study 5: everything else you can change

**Status:** done (11 November). Screen: 35,400 matches. Confirmation of the uncertain effects and the goalkeeper
check: 18,300 more.

## Design

- **Conditions:** 125 single changes for the team only, each on the 10 real matches × seeds 1-30 (300 pairs),
  against the unchanged match.
- **How each change is made:** through the app's own editor and validator, exactly as you would make it in the UI.
  That covers start state, body, person, starters' position ratings, mentality, every option of every team
  instruction, opposition instructions and in-match management.
- **Skipped:** three Supporting Runs (secondary) options, which the validator rejects for this tactic.
- **The squad's natural values** (median of the starting XI over the 10 matches):
  - condition 94–99%;
  - match sharpness 90–100% (a few players near 57%);
  - morale 15–20;
  - team cohesion 62–84;
  - in-match management: the assistant (the saved matches were played on holiday).

**Reading the table:** with about 120 conditions, a handful of |t| ≈ 2–3 results appear by chance. Treat |t| ≥ 4 as
established, 3–4 as likely, and anything below as unconfirmed.

## Results: everything except team instructions

| Group | Change | Δ ppg (t) | Δ xGD (t) | xG for | xG against |
|---|---|---|---|---|---|
| Start state | condition=80% | -0.80 (-8.1) | -1.21 (-13.8) | -0.57 | +0.64 |
| Start state | condition=90% | -0.28 (-2.8) | -0.36 (-4.3) | -0.18 | +0.17 |
| Start state | condition=100% | +0.18 (+2.0) | +0.24 (+2.8) | +0.14 | -0.10 |
| Start state | sharpness=50% | -1.03 (-10.6) | -1.48 (-18.1) | -0.65 | +0.83 |
| Start state | sharpness=75% | -0.37 (-3.7) | -0.49 (-5.5) | -0.16 | +0.33 |
| Start state | sharpness=100% | +0.16 (+1.5) | +0.25 (+2.9) | +0.09 | -0.16 |
| Start state | morale=5 | -0.17 (-1.7) | -0.10 (-1.2) | -0.07 | +0.03 |
| Start state | morale=12 | -0.13 (-1.3) | -0.07 (-0.9) | -0.03 | +0.04 |
| Start state | morale=20 | +0.06 (+0.6) | +0.11 (+1.2) | +0.10 | -0.01 |
| Start state | club_cohesion=25 | +0.02 (+0.2) | -0.01 (-0.1) | -0.03 | -0.02 |
| Start state | club_cohesion=100 | -0.03 (-0.3) | +0.09 (+1.2) | +0.09 | -0.00 |
| Start state | team cohesion: match high vs match low (pooled) | +0.32 (+3.2) | +0.35 (+4.2) | | |
| Position familiarity (starters) | positions capped at 15 | -0.26 (-2.5) | -0.22 (-2.7) | -0.20 | +0.02 |
| Position familiarity (starters) | positions capped at 10 | -0.85 (-8.8) | -1.03 (-12.3) | -0.68 | +0.35 |
| Position familiarity (starters) | positions all natural | -1.10 (-12.0) | -1.50 (-18.1) | -1.05 | +0.44 |
| Mentality | mentality -2 | +0.02 (+0.2) | +0.07 (+0.9) | -0.08 | -0.15 |
| Mentality | mentality -1 | +0.08 (+0.8) | -0.11 (-1.4) | -0.12 | -0.00 |
| Mentality | mentality +1 | -0.01 (-0.1) | -0.26 (-3.1) | -0.15 | +0.11 |
| In-match management | in-match ai | -0.56 (-5.8) | -0.91 (-11.0) | -0.69 | +0.22 |
| In-match management | in-match assistant | +0.00 (+0.0) | +0.00 (+0.0) | +0.00 | +0.00 |
| Opposition instructions | OI none | +0.00 (+0.0) | +0.00 (+0.0) | +0.00 | +0.00 |
| Body | height-10cm | -0.04 (-0.4) | +0.08 (+0.9) | -0.01 | -0.08 |
| Body | height+10cm | -0.02 (-0.2) | +0.01 (+0.1) | +0.03 | +0.03 |
| Body | weight-10kg | +0.00 (+0.0) | +0.00 (+0.0) | +0.00 | +0.00 |
| Body | weight+10kg | +0.00 (+0.0) | +0.00 (+0.0) | +0.00 | +0.00 |
| Person | age-5 | -0.13 (-1.6) | -0.13 (-2.1) | -0.07 | +0.06 |
| Person | age+5 | -0.07 (-1.5) | +0.06 (+1.4) | +0.01 | -0.04 |
| Person | current_ability-20 | +0.07 (+0.8) | +0.03 (+0.4) | +0.02 | -0.02 |
| Person | current_ability+20 | +0.03 (+0.3) | +0.13 (+1.5) | +0.07 | -0.06 |
| Person | reputation x0.5 | -0.00 (-0.0) | +0.08 (+0.9) | +0.03 | -0.05 |
| Person | reputation x1.5 | +0.00 (+0.0) | +0.05 (+0.6) | -0.02 | -0.07 |
| Person | professionalism=5 | -0.06 (-0.6) | -0.09 (-1.1) | -0.05 | +0.04 |
| Person | professionalism=18 | +0.07 (+0.7) | +0.19 (+2.3) | +0.07 | -0.12 |
| Person | pressure=5 | +0.01 (+0.1) | +0.09 (+1.1) | +0.04 | -0.05 |
| Person | pressure=18 | +0.22 (+2.2) | +0.25 (+2.9) | +0.17 | -0.08 |
| Person | temperament=5 | -0.22 (-2.2) | -0.02 (-0.2) | -0.00 | +0.02 |
| Person | temperament=18 | +0.10 (+1.0) | +0.14 (+1.7) | +0.09 | -0.06 |
| Person | ambition=5 | +0.10 (+1.0) | -0.02 (-0.2) | +0.01 | +0.03 |
| Person | ambition=18 | -0.06 (-0.7) | +0.07 (+0.8) | +0.04 | -0.03 |
| Person | adaptability=5 | +0.05 (+0.5) | +0.06 (+0.7) | +0.00 | -0.06 |
| Person | adaptability=18 | -0.07 (-0.8) | +0.12 (+1.5) | +0.09 | -0.03 |
| Person | loyalty=5 | +0.13 (+1.2) | +0.14 (+1.7) | +0.05 | -0.09 |
| Person | loyalty=18 | +0.05 (+0.5) | +0.13 (+1.6) | +0.08 | -0.04 |
| Person | sportsmanship=5 | -0.05 (-0.5) | -0.04 (-0.5) | -0.04 | -0.00 |
| Person | sportsmanship=18 | -0.05 (-0.5) | -0.03 (-0.4) | -0.02 | +0.01 |

## Results: team instructions

Each row changes one instruction from the team's setting to the option named. Sorted by Δ xGD.

| Team instruction changed to | Δ ppg (t) | Δ xGD (t) | xG for | xG against |
|---|---|---|---|---|
| AttackingTransition: Standard | +0.19 (+1.8) | +0.20 (+2.3) | +0.12 | -0.08 |
| ProgressThrough: Left | +0.11 (+1.1) | +0.20 (+2.4) | +0.09 | -0.11 |
| Tempo: Higher | +0.09 (+0.9) | +0.19 (+2.5) | +0.12 | -0.07 |
| SupportingRuns: Standard | +0.21 (+2.2) | +0.18 (+2.1) | +0.12 | -0.06 |
| ProgressThrough: Right | +0.07 (+0.7) | +0.18 (+2.2) | +0.09 | -0.09 |
| ProgressThrough: Centre | +0.05 (+0.5) | +0.18 (+2.2) | +0.10 | -0.08 |
| GoalKicks: Mixed | +0.09 (+0.9) | +0.18 (+1.9) | +0.11 | -0.07 |
| GoalkeeperDistributionSpeed: Balanced | +0.15 (+1.6) | +0.18 (+2.0) | +0.09 | -0.09 |
| Crossing: Floated Crosses | +0.08 (+0.8) | +0.18 (+1.9) | +0.10 | -0.08 |
| DefensiveLine: Deeper | +0.10 (+1.1) | +0.16 (+1.8) | +0.12 | -0.04 |
| Crossing: Balanced | +0.02 (+0.2) | +0.15 (+1.7) | +0.10 | -0.05 |
| AttackingWidth: Much wider | +0.05 (+0.5) | +0.14 (+1.6) | +0.03 | -0.11 |
| TriggerPress: Standard | +0.06 (+0.6) | +0.12 (+1.5) | +0.01 | -0.12 |
| AttackingTransition: Regroup | +0.26 (+2.6) | +0.12 (+1.5) | +0.10 | -0.02 |
| SupportingRuns: Right underlap | +0.03 (+0.3) | +0.12 (+1.4) | +0.10 | -0.02 |
| Tempo: Standard | +0.03 (+0.3) | +0.12 (+1.5) | +0.12 | +0.00 |
| AttackingWidth: Narrower | +0.04 (+0.4) | +0.11 (+1.3) | +0.02 | -0.08 |
| DefensiveLine: Standard | -0.16 (-1.7) | +0.10 (+1.1) | +0.06 | -0.03 |
| DefensiveLineBehaviour: Balanced | +0.07 (+0.7) | +0.09 (+1.1) | +0.10 | +0.00 |
| TriggerPress: More often | -0.07 (-0.7) | +0.09 (+1.1) | +0.02 | -0.07 |
| SupportingRuns: Left underlap | +0.01 (+0.1) | +0.08 (+0.9) | +0.09 | +0.01 |
| ShotsFromDistance: More shots from distance | +0.12 (+1.1) | +0.07 (+0.9) | -0.02 | -0.09 |
| PassReception: Standard | +0.02 (+0.2) | +0.07 (+0.9) | +0.04 | -0.03 |
| Crossing: Whipped Crosses | +0.09 (+0.9) | +0.07 (+0.8) | +0.09 | +0.01 |
| DefensiveTransition: Regroup | -0.04 (-0.4) | +0.07 (+0.8) | +0.05 | -0.02 |
| DefensiveTransition: Standard | -0.05 (-0.5) | +0.06 (+0.6) | +0.02 | -0.04 |
| DefensiveLineBehaviour: Drop off more | +0.05 (+0.5) | +0.05 (+0.6) | +0.06 | +0.01 |
| CreativeFreedom: More disciplined | -0.02 (-0.2) | +0.05 (+0.6) | +0.06 | +0.00 |
| CrossEngagement: Standard | +0.05 (+0.4) | +0.05 (+0.5) | +0.03 | -0.02 |
| TimeWasting: Frequently | +0.07 (+0.7) | +0.04 (+0.5) | -0.02 | -0.06 |
| ShotsFromDistance: Standard | -0.10 (-0.9) | +0.04 (+0.5) | +0.03 | -0.01 |
| GoalkeeperDistributionSpeed: Slow pace down | +0.00 (+0.0) | +0.04 (+0.5) | +0.04 | +0.00 |
| PassReception: Pass Into Feet | -0.06 (-0.6) | +0.04 (+0.4) | -0.01 | -0.05 |
| PassingDirectness: Standard | +0.21 (+2.1) | +0.03 (+0.4) | +0.05 | +0.01 |
| TriggerPress: Less often | -0.01 (-0.1) | +0.03 (+0.4) | -0.03 | -0.06 |
| GoalkeeperUpForAttackingSetPieces: Go up | -0.08 (-0.8) | +0.03 (+0.3) | +0.02 | -0.01 |
| PreventShortGKDistribution: No | +0.04 (+0.4) | +0.02 (+0.3) | -0.01 | -0.03 |
| ProgressThrough: Balanced | -0.10 (-1.0) | +0.02 (+0.2) | +0.01 | -0.01 |
| Tackling: Standard | -0.04 (-0.4) | +0.02 (+0.2) | -0.02 | -0.04 |
| PlayForSetPieces: Play for set pieces | +0.02 (+0.2) | +0.02 (+0.2) | +0.03 | +0.01 |
| TriggerPress: Much less often | +0.02 (+0.2) | +0.01 (+0.1) | -0.08 | -0.09 |
| AttackingWidth: Wider | -0.11 (-1.1) | +0.01 (+0.1) | -0.01 | -0.02 |
| Tempo: Lower | -0.07 (-0.7) | +0.01 (+0.1) | +0.01 | -0.00 |
| TimeWasting: Sometimes | -0.15 (-1.6) | +0.01 (+0.1) | +0.02 | +0.01 |
| DefensiveLine: Higher | -0.10 (-1.1) | +0.01 (+0.1) | +0.02 | +0.01 |
| AttackingWidth: Standard | -0.13 (-1.4) | -0.00 (-0.0) | -0.04 | -0.04 |
| GoalkeeperDistributionTarget: Full-backs | -0.08 (-0.8) | -0.00 (-0.0) | -0.06 | -0.06 |
| LineOfEngagement: Mid block | +0.05 (+0.5) | -0.01 (-0.1) | -0.05 | -0.04 |
| Patience: Standard | +0.01 (+0.1) | -0.01 (-0.1) | -0.05 | -0.04 |
| GoalKicks: Long | -0.08 (-0.8) | -0.01 (-0.1) | -0.03 | -0.02 |
| BuildUpStrategy: Bypass Press | -0.05 (-0.6) | -0.01 (-0.1) | -0.04 | -0.03 |
| CreativeFreedom: More expressive | -0.16 (-1.7) | -0.02 (-0.2) | -0.05 | -0.04 |
| Patience: Hit Early Crosses | -0.12 (-1.2) | -0.02 (-0.2) | -0.13 | -0.11 |
| LineOfEngagement: Low block | -0.03 (-0.3) | -0.03 (-0.3) | -0.06 | -0.03 |
| GoalkeeperDistributionTarget: Balanced | +0.00 (+0.0) | -0.03 (-0.4) | -0.08 | -0.05 |
| BuildUpStrategy: Standard | -0.03 (-0.3) | -0.03 (-0.4) | -0.10 | -0.07 |
| Tackling: Stay on feet | +0.00 (+0.0) | -0.04 (-0.4) | +0.00 | +0.04 |
| PassingDirectness: Much More Direct | +0.04 (+0.4) | -0.04 (-0.4) | -0.00 | +0.04 |
| DefensiveLine: Much higher | -0.15 (-1.6) | -0.04 (-0.5) | +0.00 | +0.04 |
| GoalkeeperDistributionTarget: Playmaker | -0.09 (-0.9) | -0.06 (-0.8) | -0.05 | +0.02 |
| GoalkeeperDistributionTarget: Flanks | +0.03 (+0.3) | -0.06 (-0.8) | -0.08 | -0.02 |
| Dribbling: Discourage | +0.06 (+0.7) | -0.07 (-0.8) | -0.10 | -0.03 |
| GoalkeeperDistributionTarget: Target forward | -0.09 (-1.0) | -0.07 (-0.8) | -0.01 | +0.06 |
| GoalkeeperDistributionTarget: Over the opposition defence | -0.09 (-1.0) | -0.07 (-0.8) | -0.01 | +0.06 |
| PassingDirectness: Shorter | -0.09 (-1.0) | -0.08 (-0.9) | -0.07 | +0.01 |
| CrossEngagement: Stop crosses | -0.19 (-2.0) | -0.08 (-0.9) | -0.03 | +0.05 |
| PassingDirectness: Much Shorter | -0.15 (-1.5) | -0.09 (-1.0) | -0.06 | +0.03 |
| Tempo: Much Lower | -0.10 (-1.0) | -0.11 (-1.3) | -0.05 | +0.06 |
| Dribbling: Standard | -0.13 (-1.4) | -0.18 (-2.0) | -0.10 | +0.08 |
| PressingTrap: Show inside | -0.18 (-1.9) | -0.20 (-2.3) | -0.04 | +0.16 |
| PressingTrap: Show outside | -0.14 (-1.4) | -0.28 (-3.3) | -0.12 | +0.16 |

## Confirmation (seeds 31-120)

The screen's uncertain effects (|t| between 2 and 4), plus team cohesion, condition and sharpness, were rerun on 90
new seeds per match: 900 more pairs each, independent of the screen.

| Change | Screen (300 pairs): ppg / xGD | Confirmation (900 pairs): ppg (t) | xGD (t) | Verdict |
|---|---|---|---|---|
| TI Pressing trap: Show outside | −0.14 / −0.28 | −0.23 (−4.0) | **−0.40 (−8.5)** | confirmed, larger |
| TI Pressing trap: Show inside | −0.18 / −0.20 | −0.19 (−3.5) | **−0.30 (−6.3)** | confirmed |
| Team cohesion, highest vs lowest | +0.32 / +0.35 | +0.21 (+3.8) | **+0.32 (+6.7)** | confirmed |
| Mentality one step more attacking | −0.01 / −0.26 | −0.12 (−2.1) | **−0.22 (−4.5)** | confirmed |
| Condition 100% | +0.18 / +0.24 | +0.13 (+2.3) | **+0.19 (+4.0)** | confirmed |
| TI Dribbling: Standard | −0.13 / −0.18 | −0.11 (−1.9) | −0.15 (−3.0) | likely |
| Sharpness 100% | +0.16 / +0.25 | +0.10 (+1.8) | +0.11 (+2.2) | likely, smaller |
| Age −5 | −0.13 / −0.14 | +0.03 (+0.7) | −0.08 (−2.2) | unclear |
| Pressure handling 18 | +0.22 / +0.26 | +0.06 (+1.0) | +0.06 (+1.2) | not confirmed |
| Temperament 5 | −0.22 / −0.02 | −0.05 (−1.0) | −0.04 (−0.7) | not confirmed |
| Professionalism 18 | +0.07 / +0.19 | −0.03 (−0.5) | +0.00 (+0.1) | not confirmed |
| TI Tempo: Higher | +0.09 / +0.19 | +0.01 (+0.2) | −0.00 (−0.0) | not confirmed |
| TI Progress through: Left | +0.11 / +0.20 | −0.01 (−0.2) | −0.02 (−0.4) | not confirmed |
| TI When possession is won: Standard | +0.19 / +0.20 | −0.01 (−0.1) | −0.02 (−0.5) | not confirmed |
| TI When possession is won: Regroup | +0.26 / +0.12 | +0.03 (+0.6) | +0.01 (+0.3) | not confirmed |
| TI Underlaps: Standard | +0.21 / +0.19 | −0.04 (−0.7) | −0.05 (−1.0) | not confirmed |
| TI Goalkeeper distribution speed: Balanced | +0.15 / +0.18 | +0.06 (+1.1) | +0.02 (+0.4) | not confirmed |
| TI Passing directness: Standard | +0.21 / +0.03 | −0.03 (−0.5) | −0.05 (−1.1) | not confirmed |

**The lesson:** in a screen of 125 changes, results with |t| of 2-3 are often chance. Of the 15 such results rerun
here, 2 were confirmed (Show inside, condition 100%), 2 are likely (Dribbling standard, sharpness 100%), 1 is
unclear and 10 vanished. The three with |t| above 3 in the screen all held up.

**Goalkeeper check.** "All positions natural" cost 1.10 points per game in the screen. Making every starter natural
in the 14 outfield positions but leaving the goalkeeper rating as stored has **no effect at all** (+0.01 points
per game, 0.00 xGD, 300 pairs). The whole loss came from making outfield players natural goalkeepers: the engine
or the assistant uses that rating, with bad results. Being natural in more outfield positions neither helps nor
hurts in a single match.

## What it means

**Large and certain:**

1. **Match sharpness and condition matter enormously.**
   - Sharpness: dropping the squad to 50% costs a full point per game (−1.03, t −10.6); 75% costs 0.37.
   - Condition: playing at 80% costs 0.80 points; 90% costs 0.28. Full condition gains about 0.13 over the
     squad's normal values (confirmed); full sharpness about 0.10 (likely).
   - In practice: rotation and fitness management are worth more than any tactical tweak.
2. **Playing players out of position hurts a lot.** Capping the starters' position ratings at 15 costs 0.26 points
   per game. At 10 it costs 0.85. [Study 17](17-positions-in-and-out-of-possession.md) (17b) splits this: most of the cost
   comes from the goalkeeper's rating and from the outfield players' ratings for positions they don't play, not
   from their own positions.
3. **"In-match AI" costs 0.56 points per game against the assistant (t −5.8).** This mode hands in-match decisions
   to the game's AI manager logic for the team's side. Whether our "AI" setting matches what the game does for AI
   clubs is not yet checked, so treat this as provisional.
4. **The pressing trap: keep it on standard.** Showing the opponent inside or outside costs 0.19-0.23 points and
   0.30-0.40 xG difference per game for this team (confirmed on 1,200 pairs).
5. **Team cohesion:** the match's highest against its lowest possible value is worth about +0.2 to +0.3 points per
   game (confirmed).
6. **Mentality one step more attacking costs about 0.12 points and 0.22 xGD per game** (confirmed). One or two
   steps more defensive changes nothing clear.

**Not read by the match, or no effect:**

- **Weight ±10 kg:** exactly zero; the engine does not read it.
- **In-match "assistant":** exactly zero, as expected: the saved matches already use the assistant.
- **Opposition instructions "none":** exactly zero. Either the saved matches carry no opposition instructions for
  the team, or the assistant sets its own during the match. Not checked.
- **Current ability ±20, reputation ×0.5/×1.5, height ±10 cm, club cohesion and every personality field**
  (including Pressure, Temperament and Professionalism after the confirmation): no clear effect in a single match.
  The engine plays on attributes, not on the CA number.
- **Morale:** small (5 → −0.17 ppg, t −1.7).
- **Most team-instruction options:** no clear effect one at a time; the few that looked promising in the screen did
  not hold up.

## Next

- Check that the "In-match AI" setting matches what the game does for AI-managed clubs.
- Check the zero effect of turning opposition instructions off.

## Reproduce

```sh
FM27_SAVED_MATCHES=<27.0 saved matches> .venv/bin/python port/validation/study5_everything.py build \
  port/mac_host/runs/study5 port/mac_host/runs/attr_real_2701
FM27_STUDY_HOST=<frozen host> .venv/bin/python port/validation/overnight.py run port/mac_host/runs/study5 6
.venv/bin/python port/validation/study5_everything.py analyse port/mac_host/runs/study5
# confirmation and goalkeeper check
.venv/bin/python port/validation/study5_confirm.py build port/mac_host/runs/study5c port/mac_host/runs/study5
FM27_STUDY_HOST=<frozen host> .venv/bin/python port/validation/overnight.py run port/mac_host/runs/study5c 6
.venv/bin/python port/validation/study5_confirm.py analyse port/mac_host/runs/study5c port/mac_host/runs/study5
```
