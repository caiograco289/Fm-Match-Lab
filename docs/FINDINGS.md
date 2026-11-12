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

## Attributes by playing style ([Study 9](studies/09-attributes-by-style.md))

- **Physical attributes win under every style, possession styles included.** +5 in Pace, Acceleration, Stamina, Work
  Rate and Aggression for the whole squad is worth +0.38 to +0.48 expected points per game (14 to 18 points a season)
  under all five styles tested.
- **Passing attributes help the direct styles, not the possession styles.** +5 in Passing, Technique, Vision,
  Decisions, First Touch and Composure: +0.15 xPts per game with Direct Counter-Attack, +0.11 with Gegenpress, nothing
  measurable with Tiki-Taka or Control Possession.
- **Why:** possession styles already complete 90-92% of their passes, and better passers there keep the ball slightly
  less (likely more ambitious passes). Direct Counter-Attack completes 82%, and better passing lifts completion,
  possession and shots.

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

17 tactics (the 10 presets and 7 community tactics) play each other home and away over 20 seasons, 640 matches
each, on neutral ground: the same synthetic squad for every team, template matches between other clubs, both sides
starting alike and equal familiarity.

- **Every community tactic beats every preset.** STORMBRINGER (1.78 points per game) and ARGUS 3-4-3 (1.74) lead, then
  ZaZ's Ace of Clubs (1.70); the weakest community tactic (Ace of Hearts, 1.44) is still ahead of the best preset.
- **Best presets: Gegenpress (1.39) and Fluid Counter-Attack (1.38).** The defensive presets are last: Catenaccio 1.03,
  Park the Bus 0.92.
- **The setting hardly matters:** the two template matches give the same table (correlation 0.95), and so does the
  first version on the team's own match with real squads (0.90).
- **A second, 18-tactic league reproduces it** ([Study 7b](studies/07b-tactic-league-18.md)): every preset within about
  0.06 points per game of its Study 7 value, and every community tactic again ahead of every preset.
- **Matchups matter little.** A tactic's overall strength predicts almost all its head-to-head results: in Study 7b only
  one of 306 pairings differs clearly from that prediction.

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

- **Applied for a whole match, only Lock It Down has a clear effect on neutral ground** (every preset as the base,
  synthetic squads): about −0.2 expected points per game, with fewer goals at both ends.
- **Other tweaks depend on the tactic they modify.** Throw The Kitchen Sink, Go Long and Play With More Urgency cost
  clearly with one team's high-press, high-tempo tactic, but average about zero over the ten presets.
- **Goalkeeper Up For Set Pieces concedes more** in every version (+0.2 to +0.3 goals against per game).
- Using tweaks for part of a match, in the situation they are meant for, is not tested yet.

## In progress and open questions

- **In-match AI** (−0.56 points per game) and **opposition instructions "none"** (exactly zero): both still to be
  checked against what the game does.
- **Tactic complexity:** no clear effect when changed during the match; a test through a saved game would settle it.
- **One club.** Every result comes from one newly promoted side's matches. A dominant team may show different
  values; `scripts/study.py` lets anyone repeat the studies on their own club.
