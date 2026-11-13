# Engine studies: plan and index

Questions about how FM27's match engine responds to what you control. Each study gets its own page here when it
finishes. Pages for studies still running say so.

| # | Question | Status | Page |
|---|---|---|---|
| 1 | What is each attribute worth? | **done** (27.0 and 27.0.1) | [01-attribute-values.md](01-attribute-values.md) |
| 2 | Are attribute values in real matches the same as in "everyone 12" tests? | **done**: levelling squads changes little; the test match shrinks most effects | [02-real-vs-levelled.md](02-real-vs-levelled.md) |
| 3 | What does tactical familiarity do? | **done**: familiarity = trained and played area values; training counts double | [03-tactical-familiarity.md](03-tactical-familiarity.md) |
| 4 | Do attributes matter more at high familiarity than at low? | **done**: no; attributes and familiarity add up | [04-attributes-x-familiarity.md](04-attributes-x-familiarity.md) |
| 5 | Of everything else we can change, what matters and by how much? | **done**: sharpness, condition, positions and cohesion lead; pressing trap and mentality confirmed | [05-everything-else.md](05-everything-else.md) |
| 6 | Do tactics differ, and does the best tactic depend on familiarity? | **done**: the team's own tactic (STORMBRINGER) is best; defensive presets far worse | [06-tactics-x-familiarity.md](06-tactics-x-familiarity.md) |
| 7 | How do tactics do against each other? | **done** (neutral ground: synthetic squads, other clubs' matches): every community tactic beats every preset; STORMBRINGER and ARGUS lead; Park the Bus last | [07-tactic-league.md](07-tactic-league.md) |
| 7b | An 18-tactic league: does it reproduce, and do particular matchups matter? | **done**: Study 7 reproduces; newer ZaZ Aces stronger; overall strength predicts almost every head to head | [07b-tactic-league-18.md](07b-tactic-league-18.md) |
| 8 | What do FM27's in-match Tactical Tweaks do, and does it depend on the opponent's tactic? | done | 08-tactical-tweaks.md |
| 9 | Are attribute values tied to the tactic? Physical and passing attributes under five playing styles | done | 09-attributes-by-style.md |
| 10 | Are attributes worth more together? Four groups of four, alone and together | **done**: no; groups add up, carried by Jumping Reach, Anticipation, Dribbling and Balance | [10-attribute-combinations.md](10-attribute-combinations.md) |
| 11 | Which hidden and personality attributes matter, and does Important Matches count in big matches? | **done**: Pressure (low) is the one clear effect; Consistency barely matters and is often not read; Dirtiness and Temperament drive cards | [11-hidden-attributes.md](11-hidden-attributes.md) |
| 12 | Are there thresholds? 13 attributes from 1 to 20 | **done**: mostly straight lines; Work Rate has a floor, Jumping Reach pays above 9-12, Pace and Acceleration diminish above 12; Strength works through goals, not xG | [12-thresholds.md](12-thresholds.md) |
| 13 | What is an attribute worth in each position, and is one player one-eleventh of the team? | **done**: no clear position-specific values; Jumping Reach pays everywhere; the first few jumpers are worth most | [13-value-by-position.md](13-value-by-position.md) |
| 14 | Do attribute values and rankings hold for strong and weak sides, favourites and underdogs? | **done**: yes; same ranking at every strength (rank correlation 0.84), no attribute differs (p 0.81) | [14-team-strength.md](14-team-strength.md) |
| 15 | How big is home advantage, does it depend on the ground, and does morale matter? | **done**: home 1.54 v away 1.18 points (+0.21 xG); differs by ground, not by level; morale no measurable effect | [15-home-advantage-morale.md](15-home-advantage-morale.md) |
| 17 | Does an unfamiliar in- or out-of-possession position cost more? (and 17b: where the cost of playing out of position comes from) | **done**: neither measurably; other-position ratings and the goalkeeper's rating carry the cost | [17-positions-in-and-out-of-possession.md](17-positions-in-and-out-of-possession.md) |
| 20 | Does Current Ability play a role in the match? | **done**: no; CA 40-200 with attributes fixed changes nothing measurable, alone or with Passing or Decisions | [20-current-ability.md](20-current-ability.md) |
| 21 | What makes a goalkeeper good? Eighteen attributes alone, all together, and the position rating (21b) | **done**: no single attribute clear; all +5 together +4-5 points of save rate, +0.26 points per game; position rating 10 concedes +0.69 goals per game | [21-goalkeepers.md](21-goalkeepers.md) |

## Common design

Unless a page says otherwise, every study uses the same set-up.

- **Bases: real saved matches.** Ten matches of a Premier League team ("the team") the game saved on holiday under 27.0 (Fleetwood, Brentford,
  Burnley, Chelsea, Man City, Stoke, Man Utd, Norwich, West Ham, Young Boys), replayed on the 27.0.1 engine. Each
  match keeps everything stored in it: both squads, both tactics, fitness, morale and the opponent's selection.
- **In-match decisions are live.** In these matches the assistant and the AI substitute and adjust during the match,
  as with an instant result (checked: different seeds give different substitutions).
- **Paired comparison.** Each condition changes one thing for the team only and replays every match on the same 30
  seeds as the unchanged version. The effect is the average paired difference over 10 × 30 = 300 matches. The t value
  says how clearly it differs from zero: |t| ≥ 2 is about 95% confidence, and |t| ≥ 3 is solid.
- **Outcomes:** points per game (ppg), expected-goal difference (xGD), goals for and against, shots and xG per shot.
  xGD is the most sensitive; ppg is what you ultimately care about but is noisier.
- **Resolution:** with 300 pairs, effects of about 0.1 ppg or 0.1 xGD can be detected. Smaller ones read as "no
  clear effect", not as "no effect".
- **Many comparisons:** a study with 100 conditions will show a few |t| ≈ 2 results by chance. The pages call out
  only effects that are large, consistent in direction (both +5 and −5) or confirmed with more seeds.
- **Limits:** all bases are one club, mostly Premier League matches, so results describe a lower-table side
  against stronger teams.

Throughput is about 5,400 matches per hour on this machine (6 workers). Running costs are noted per study.

## Study 1: attribute values

Each of the 54 non-position attributes is moved by ±5 in-game points (±25 stored) for the team's whole squad and
clamped to 1–20. That gives 109 conditions × 300 = 32,700 matches, about 6 hours.

**Done.** Pace and Acceleration lead by far (about +0.07 ppg and +0.10 xGD per point), followed by Jumping Reach,
Stamina, Anticipation, Dribbling and Concentration. Finishing converts chances rather than creating them, and most
technical attributes show no clear effect. 27.0.1 matches 27.0 (r = 0.98). See
[01-attribute-values.md](01-attribute-values.md).

## Study 2: real matches against "everyone 12" tests

**Done.** Earlier tests on the original tool's sample match, with every attribute levelled to 12, suggested that
physical attributes dominate and mental ones barely register. Study 2 shows that this came from the test match,
not the engine: in real matches Anticipation and Concentration are clearly rewarded, even with every player levelled
to 12, while on the sample match most effects shrink and several vanish. Not every mental attribute matters
(Decisions, Teamwork, Determination and Flair show no clear effect anywhere). See
[02-real-vs-levelled.md](02-real-vs-levelled.md).

## Study 3: tactical familiarity

**Step 0: find the input (done).** Screenshots of the game's panel before two matches identified it. FM27's familiarity is
the Tactical Understanding part of Tactical Effectiveness: per-area values in the effectiveness record, plus
tactical ability and tactic complexity. See [03-tactical-familiarity.md](03-tactical-familiarity.md).

**Step 1: dose-response (done).** Untrained areas cost about 0.4 points per game; well-trained areas (around 75)
gain about 0.2, and more gains nothing. Match exposure counts about half as much as training. Complexity held alone
showed no clear effect. See [03-tactical-familiarity.md](03-tactical-familiarity.md).

## Study 4: attributes × familiarity

Take the six attributes with the largest xGD effects in Study 1 (Pace, Acceleration, Jumping Reach, Stamina,
Anticipation, Dribbling). Familiarity low = all eight tactical areas held at 20, high = 80. Move each by +5 and −5 at low and at high familiarity,
giving 6 × 2 × 2 conditions plus the two familiarity baselines, × 300 ≈ 7,800 matches (about 1.5 hours).

The interaction is (attribute effect at high familiarity) − (attribute effect at low familiarity), paired on the same
matches and seeds. A positive interaction means good players need a familiar tactic to show it. A negative one means
quality compensates for unfamiliarity.

## Study 5: everything else

A screen over every other input the app can change, each moved one step for the team only, 300 pairs each. Then
the 10–15 largest effects are rerun with 3× the seeds to confirm them and give tighter estimates.

| group | conditions |
|---|---|
| Start state | condition 80/90/100%, match sharpness 50/75/100%, morale low/high, team cohesion low/high, club cohesion low/high |
| Body | height ±10 cm, weight ±10 kg |
| Person | age, the 7 personality fields (professionalism, temperament, pressure, …) low/high, current ability ±20, reputation |
| Position | starters' familiarity with their position: natural → accomplished → unconvincing |
| Mentality | one and two steps more defensive and more attacking |
| Team instructions | every option of every in- and out-of-possession instruction, one at a time |
| Player instructions | the main ones by position group (e.g. full-backs "get further forward", forwards "shoot more often") |
| Opposition instructions | press all / none, tight-mark all |
| Set pieces | taker order, routine frequency, throw-in strategy |
| In-match management | assistant vs fixed tactic vs AI manager |

Cost: about 150 conditions × 300 ≈ 45,000 matches (8 hours) for the screen, plus about 2 hours to confirm.

The page ranks everything by effect on ppg and xGD, with the mechanism (shots, xG per shot, chances conceded), and
gives a short "worth changing / not worth it" summary.

## Study 6: tactics × familiarity

Run the installed FM27 presets (one per style, about 20) plus the user's own .fmf tactics on the team in the 10 real
matches, 300 pairs each. That gives a ranking on real matches, which the earlier tactic league (levelled squads, no
substitutions) could not. Once Study 3 has the familiarity input, each tactic also runs at low and high familiarity,
to see whether the ranking changes: some tactics may only pay off once learned.

Cost: about 6,000 matches per familiarity level (about 1 hour each).

## Order and timing

Studies 1, 3, 4, 6, 5 and 2 ran in that order on 10 and 11 November 2026, at about 6,500 matches per hour on six
workers; the Study 5 confirmation followed.

Each page states its design, results, interpretation, caveats and how to reproduce it.
