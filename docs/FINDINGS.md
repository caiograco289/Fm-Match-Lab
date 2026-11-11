# What we found

A summary of six studies of FM27's match engine (version 27.0.1), run with this tool: about 190,000 simulated
matches. Each study and its full tables are in [docs/studies/](studies/README.md).

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
- Caveat: every tactic used the same starting XI in the same slots, which handicaps shapes far from the club's own.

## Everything else ([Study 5](studies/05-everything-else.md))

125 single changes: start state, body, personality, positions, mentality, every team-instruction option, opposition
instructions and in-match management.

- **Match sharpness at 50% costs a full point per game; condition at 80% costs 0.8.** Rotation and fitness
  management matter more than any tactical tweak.
- **Out of position:** starters capped at 15 in their positions cost 0.26 points per game; capped at 10, 0.85.
- **Letting the AI manage the team during the match costs 0.56 points per game** against the assistant.
- **Team cohesion**, lowest to highest: +0.32 points per game.
- **Mentality one step more attacking:** −0.26 xGD, no clear change in points. More defensive: no clear change.
- **Single team instructions mostly make no clear difference.** One that may hurt is Pressing Trap "Show outside"
  (−0.28 xGD).
- **Not read in a match, or no effect:** weight (exactly zero), current ability, reputation, height, most
  personality fields. The engine plays on attributes, not on the CA number.

## Real matches against test matches ([Study 2](studies/02-real-vs-levelled.md))

Earlier tests on a generic test match, with every attribute at 12, suggested that mental attributes barely matter.
On real matches, even with every player levelled to 12, Anticipation and Concentration are clearly rewarded. On
the test match most effects shrink (to about 40% overall) and several vanish. **Test on real matches.**

## In progress and open questions

- **Study 5 confirmation (running).** The uncertain Study 5 effects (|t| between 2 and 4: some team instructions,
  mentality, personality) are being rerun on 90 more seeds per match. Until then, treat them as unconfirmed.
- **"All positions natural" (−1.1 points per game).** This is probably an artefact: it also makes outfield players
  natural goalkeepers. A check that leaves the goalkeeper rating alone is part of the same run.
- **Tactic complexity:** no clear effect when changed during the match; a test through a saved game would settle it.
- **One club.** Every result comes from one newly promoted side's matches. A dominant team may show different
  values; `scripts/study.py` lets anyone repeat the studies on their own club.
