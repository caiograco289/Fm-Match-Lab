# What we found

A summary of the studies of FM27's match engine (version 27.0.1), run with this tool: about 220,000 simulated
matches, plus a first tactic search. Each study and its full tables are in [docs/studies/](studies/README.md).

**How the studies work.** All of them use ten real matches that FM27 saved for one club, a newly promoted Premier
League side. Each test changes one thing for that team and replays every match on the same random seeds as the
unchanged version, 300 times or more, so every comparison is like for like. Results are in points per game and in
expected-goal difference (xGD: expected goals for minus against), which is less noisy. A "t" value of 3 or more
means the effect is solid.

For scale: +0.1 points per game is about 4 points over a 38-match season.

## The short version

1. **Fitness and selection matter more than anything you can do on the tactics screen.** Match sharpness, condition
   and playing people in their positions dwarf every individual team instruction.
2. **Pace and Acceleration are the most valuable attributes by far.** After them come Jumping Reach, Stamina,
   Anticipation, Dribbling and Concentration.
3. **Tactical familiarity is worth about half a point per game,** mostly through training. It stops paying off once
   the tactic is well learned.
4. **A tactic that suits the squad beats every installed preset** on these matches; the defensive presets are the
   worst.
5. **Tests on made-up matches mislead.** On a generic test match most attribute effects shrink and some disappear.

## Attributes ([Study 1](studies/01-attribute-values.md))

Each attribute moved by 5 points for the whole squad.

- **Pace and Acceleration:** about +0.07 points per game and +0.10 xGD per point. +5 Pace across the squad is worth
  about 13 points a season.
- **Next:** Jumping Reach, Stamina, Anticipation, Dribbling, Concentration (+0.04 to +0.07 xGD per point), then
  Balance, Composure, Work Rate and Vision.
- **Finishing doesn't create chances, it converts them:** xG doesn't move, goals and points do.
- **Most technical attributes show no clear effect:** Passing, Technique, First Touch, Crossing, Off the Ball,
  Tackling, Marking, Positioning.
- **Goalkeeper Kicking is the only clearly negative attribute** (fewer chances for the team), and only with real
  players.
- The 27.0.1 patch changed nothing measurable (the two versions agree at r = 0.98).

## Tactical familiarity ([Study 3](studies/03-tactical-familiarity.md))

In FM27, familiarity is the "Tactical Understanding" part of the Tactical Effectiveness screen: for each of the
eight tactical areas, training plus match exposure, plus the player's tactical ability, minus the tactic's
complexity.

- **Training counts about twice as much as match exposure.** That matches the engine's own weights.
- **An untrained tactic costs about 0.4 points per game; well trained (about 75) gains about 0.2.** Beyond that,
  more training buys nothing: each area is capped.
- **The curve flattens from about the middle of the scale.** Holding all eight areas at 50 already gives the full
  gain; 90 and 100 play identical matches.
- **No single area matters much on its own.** The effect is spread over all eight areas, so a tactic has to be
  learned as a whole. Untrained pressing intensity hurt most for this pressing side.
- **Player tactical ability** is the median of Anticipation, Decisions, Composure, Concentration and Versatility.
  It counts, but less per point.
- **Tactic complexity showed no clear effect** when changed during the match. Probably the game applies it before
  kick-off; this is still open.

## Attributes and familiarity together ([Study 4](studies/04-attributes-x-familiarity.md))

- **They add up; they don't interact.** Good players are worth the same with a familiar or an unfamiliar tactic.
- **Familiarity from low (20) to high (80) in every area is worth +0.52 points per game**, about the same as +7 Pace
  for the whole squad.

## Tactics ([Study 6](studies/06-tactics-x-familiarity.md))

23 tactics on the same matches: the 10 FM27 preset styles and 13 user tactic files.

- **The club's own tactic, STORMBRINGER 27 BBMIW 424 (a downloaded 4-2-4), was the best.** HIGHWAY STAR 27 BBM 4231
  P90 and ZaZ Ace of Spades were statistically level with it.
- **Every installed preset was worse.** The best preset (Gegenpress) costs about 0.2 xGD per game. Park the Bus
  (0.86 points per game against 1.80) and Catenaccio (1.20) are by far the worst: they create about 1 xG less per
  game and concede slightly *more*.
- At low familiarity some tactics lose much more than others; the top of the ranking hardly changes.
- Picking each tactic's own XI by position (a rerun) changed little: the ranking held (r = 0.96).

## A tactic league ([Study 7](studies/07-tactic-league.md))

17 tactics (the 10 presets and 7 user tactics) play each other home and away, 640 matches each, with equal
familiarity and each side picking its own XI.

- **User tactics take the top six places:** STORMBRINGER and HIGHWAY STAR P90 (1.71 and 1.70 points per game),
  ARGUS 3-4-3 (1.63), then ZaZ's Ace of Hearts, Clubs and Spades (about 1.55).
- **Best preset: Gegenpress (1.48),** then Fluid Counter-Attack (1.39). Five presets sit level around 1.25.
- **Defensive presets are last:** Catenaccio 1.05, Park the Bus 0.89.
- With its own XI and equal conditions, the back-three ARGUS ranks third, which supports the point that a fixed
  4-2-4 lineup had handicapped it in Study 6.

## Everything else ([Study 5](studies/05-everything-else.md))

125 single changes: start state, body, personality, positions, mentality, every team-instruction option, opposition
instructions and in-match management.

- **Match sharpness at 50% costs a full point per game; condition at 80% costs 0.8.** Rotation and fitness
  management matter more than any tactical tweak.
- **Out of position:** starters capped at 15 in their positions cost 0.26 points per game; capped at 10, 0.85.
- **Letting the AI manage the team during the match costs 0.56 points per game** against the assistant
  (provisional: our "AI" setting is still to be checked against what the game does for AI clubs).
- **Team cohesion**, lowest to highest: about +0.2 to +0.3 points per game (confirmed).
- **Mentality one step more attacking:** −0.12 points and −0.22 xGD per game (confirmed). More defensive: no clear
  change.
- **Pressing trap: keep it standard.** Showing the opponent inside or outside costs 0.19-0.23 points per game for
  this team (confirmed).
- **Most single team instructions make no clear difference.** Several looked promising in the first screen, but a
  rerun on 900 more pairs each showed they were chance.
- **Not read in a match, or no effect:** weight (exactly zero), current ability, reputation, height, and every
  personality field tested (Pressure, Temperament and Professionalism included, after the rerun). The engine plays
  on attributes, not on the CA number.

## Real matches against test matches ([Study 2](studies/02-real-vs-levelled.md))

Earlier tests on a generic test match, with every attribute at 12, suggested that mental attributes barely matter.
On real matches, even with every player levelled to 12, Anticipation and Concentration are clearly rewarded. On
the test match most effects shrink (to about 40% overall) and several vanish. **Test on real matches.**

## Other FM27 tests

Two other testers have published FM27 results with different methods (in-game seasons; the engine outside the
game). They agree with ours on the top attributes and on familiarity mattering mostly through training; the
differences mostly come from season-long effects a single match can't show. See [OTHER-TESTS.md](OTHER-TESTS.md).

## Tactical Tweaks ([Study 8](studies/08-tactical-tweaks.md))

- **None helps over a whole match,** on the team's matches or against any of the 10 presets, and none is reliably
  better against a particular preset.
- **Lock It Down, Throw The Kitchen Sink, Go Long and Play With More Urgency cost clearly;** Goalkeeper Up For Set
  Pieces concedes more.
- Using them for part of a match, in the situation they are meant for, is not tested yet.

## A tactic search (`scripts/optimise.py`)

A search for better team instructions and mentality, scored by expected points (xPts, from both sides' xG) and xG
difference, with the team's tactical areas held at the same level for every candidate. It screens hundreds of
random valid combinations, models the effect of each option and of pairs of options, confirms the best predictions
on fresh seeds and makes the final check on opponents the search never played. First run (17 saved matches: 11 for
the search, 6 held out; about 21,600 matches):

- **No clear gain on the held-out opponents.** The kept combination (six changes) scored +0.06 xPts per game (t 1.8),
  +0.12 xG difference (t 1.7) and +0.04 points (t 0.6). Every measure points the same way, mostly through fewer
  chances conceded (−0.11 xG against, t −2.7), but it is not established.
- **Most single instructions matter little** for this team (within about ±0.03 xPts per game each). The clear
  exceptions: dribbling less, and moving away from its usual Attacking mentality, both cost.
- **Large model-picked combinations failed on fresh seeds:** two of 12 or more changes, predicted at +0.20 and +0.18
  xPts, came out at −0.01 and −0.17 (t −4.1). The model is only reliable close to what was tested, so candidates are
  now limited to 4 changes, and the best of several is kept only at t ≥ 2.5.
- The changed instructions would also have to be learned in the game; the search does not count that cost, and
  tactical complexity is not recomputed by the match engine, so complex instructions are not penalised.

Next: the same search with the current squad against many more real opponents (`--save`: other clubs' matches the
game played, and this season's fixtures from the save), with every saved match held out for the final check.

## In progress and open questions

- **In-match AI** (−0.56 points per game) and **opposition instructions "none"** (exactly zero): both still to be
  checked against what the game does.
- **Tactic complexity:** no clear effect when changed during the match; a test through a saved game would settle it.
- **One club.** Every result comes from one newly promoted side's matches. A dominant team may show different
  values; `scripts/study.py` lets anyone repeat the studies on their own club.
