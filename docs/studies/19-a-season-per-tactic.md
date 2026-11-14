# Study 19: which tactic suits which club? A whole season with each preset

**Status:** done (13 November, 24,400 matches; another 15,800 in a first run and checks). Does the best tactic for a title favourite
differ from the best for a relegation candidate or a lower-league side? Instead of neutral ground, each club plays its
real league season: its real fixtures, against every opponent's real squad, with the opponents' tactics picked by the
game's AI, once with each of the ten installed presets.

**In short:**
- **The same presets lead everywhere.** Gegenpress, Control Possession and Fluid Counter-Attack are the top three
  (by expected points) for the Premier League favourite, the Premier League's weakest side and a mid-table National
  League side. In expected points the rankings of the three clubs agree almost perfectly (rank correlation 0.95-0.96).
- **Park the Bus is last for all three,** 7 to 11 points a season behind the next-worst preset and 17 to 31 behind
  the best. Defending deep does not rescue the underdog: Hull City's worst results come from Park the Bus.
- **The gap between tactics is far larger lower down.** For the National League side the best preset is worth 31
  points a season more than the worst (68 against 37); for Arsenal 26; for Hull City 17.
- **Which leader is best is not settled for the underdog or the National League side** (differences of 0-2 points,
  |t| < 1). For Arsenal, Gegenpress is ahead (78 points; +4 over Control Possession and Wing Play, t 2.1-2.2).

## Design

- **The tool:** `scripts/season.py` (see below). A club's league season is read from an FM27 save: its fixtures for
  the current season, every squad (the save's players, the best eleven picked by position for the tactic), and each
  club's stadium capacity.
- **Three clubs:**

  | Club | League | Strength of its XI |
  |---|---|---|
  | Arsenal | Premier League (20 clubs, 38 games) | 1st of 20 |
  | Hull City | Premier League | 20th of 20 |
  | Altrincham | National League (24 clubs, 46 games) | 14th of 24 |

  The Premier League clubs come from a save on the first day of a season; Altrincham from a save early in a season
  with every English level loaded.
- **The tested club:** each of the ten installed presets, the assistant managing during the match (substitutions,
  as in an instant result), tactical familiarity held at 80 for every side.
- **The opponents:** a tactic the game's AI picked in a real match. FM27 does not keep the AI's tactics in the save,
  so they come from imported matches between other clubs: the club's own where one exists (15 or 16 of 19 Premier
  League opponents, 10 of 23 in the National League), otherwise the tactic of the AI club whose situation was closest
  (strength of the XI and the gap to its opponent). The AI then manages the opponent during the match, changing roles,
  duties and mentality as it does in the game.
- **Grounds:** matches are played on four imported matches between clubs of the same league, chosen so that their
  home advantage, measured in Study 15b, matches what the league's own stadiums would give (+0.28 xG per match for the
  Premier League, where half the grounds hold 40,000 or more; +0.17 for the National League).
- **Seasons:** 20 per preset. Every preset plays the same fixtures on the same seeds, so differences are paired.

## Results

Points per season (expected points in brackets); differences against Catenaccio, the first preset, are paired.

| Preset | Arsenal | Hull City | Altrincham |
|---|---|---|---|
| Gegenpress | **78.3** (67.6) | **44.5** (47.9) | 66.2 (**66.3**) |
| Control Possession | 73.9 (64.9) | 42.5 (46.6) | **68.4** (65.3) |
| Fluid Counter-Attack | 70.8 (63.4) | 43.0 (45.0) | 68.1 (64.6) |
| Wing Play | 74.3 (61.7) | 38.0 (42.2) | 57.4 (55.5) |
| Vertical Tiki-Taka | 66.5 (62.3) | 37.9 (40.7) | 57.1 (57.3) |
| Tiki-Taka | 63.5 (58.1) | 36.6 (40.9) | 54.1 (59.0) |
| Route One | 69.0 (56.3) | 38.6 (38.5) | 52.2 (46.2) |
| Direct Counter-Attack | 68.8 (56.2) | 37.4 (38.9) | 52.3 (48.4) |
| Catenaccio | 66.3 (54.9) | 38.6 (38.2) | 44.7 (40.1) |
| Park the Bus | 52.2 (44.6) | 27.9 (29.3) | 37.5 (34.3) |

- **The leaders against each other** (points, then expected points, per season; t in brackets):
  - Arsenal: Gegenpress over Control Possession +4.4 (+2.2) and +2.7 (+3.1); over Wing Play +4.0 (+2.1) and +5.9
    (+6.7); over Fluid Counter-Attack +7.5 (+4.1).
  - Hull City: Gegenpress over Fluid Counter-Attack +1.5 (+0.7) and +3.0 (+2.6); over Control Possession +1.9 (+0.7).
  - Altrincham: Control Possession over Fluid Counter-Attack +0.3 (+0.1), over Gegenpress +2.2 (+0.7); in expected
    points Gegenpress is 1.0 ahead (−0.9).
- **Rankings agree across clubs:** rank correlation 0.95-0.96 in expected points, 0.64-0.76 in points (noisier).
- **Points and expected points differ in level.** Arsenal wins more points than its expected points with every preset
  (4 to 13 a season), as a side with better finishers should, so its order by points differs a little from its order
  by expected points. Over 20 seasons expected points rank the presets more reliably.
- **The National League side gains most from a good tactic.** Catenaccio and Park the Bus concede 75 expected goals a
  season there, against 56-58 for the leaders.

## Checks

- **Opponents' tactics: their own or the closest situation's?** Aston Villa (Gegenpress, 12 seasons) against every
  opponent once with each opponent's own observed tactic, once with every opponent on the closest situation's tactic
  instead. For the 16 clubs with their own tactic, the replacement changes their results by +0.04 expected points
  per game (t 1.1) and +0.06 points (t 0.7): the season numbers barely depend on where a club's tactic came from,
  probably because the AI adjusts whichever tactic it starts with.
- **Opponents managed by the AI or by the assistant?** Aston Villa with Gegenpress, Park the Bus and Tiki-Taka (12
  seasons each), the opponents managed by the AI in one run and by the assistant (tactic kept, substitutions only) in
  the other. The ranking is the same; Park the Bus trails Gegenpress by 20 expected points a season against
  AI-managed opponents and by 25 against assistant-managed ones (difference t 3.1). Opponents that adapt narrow the
  gap a little. The tool keeps AI management (`--opponent-management assistant` for comparison).
- **Grounds.** A first run on the first four grounds found gave twice the usual home advantage; Study 15b traced it
  to big stadiums (Liverpool's ground +0.75 xG). With grounds chosen to match each league, the tested club's home
  advantage is +0.28 to +0.33 expected points per game. The rankings of the first run (10 seasons, other grounds)
  agree with these (rank correlation in points 0.75-0.92).

## What this means

- **Start from Gegenpress, Control Possession or Fluid Counter-Attack,** whatever the club. Among the presets, the
  best tactic does not depend on whether the side is a favourite, an underdog or a lower-league club.
- **Don't park the bus as an underdog.** A weaker side loses more by sitting deep, not less.
- **Tactics matter most for clubs in lower leagues,** where the same squad can finish 30 points apart.

## Caveats

- **The installed presets only,** without changes; a club's own tactic can be tested the same way (`--tactic my.fmf`).
- **One club per situation.** Another favourite or underdog might differ in detail.
- **Within a match only.** No injuries, suspensions, rotation, form, morale, cups or tactical familiarity growing over
  the season; every side's familiarity is held at 80.
- **Grounds are stand-ins:** matches are played on four imported matches from the league, not each club's own ground.
- **Opponents' tactics are the AI's picks in other matches,** not necessarily what each club would pick against this
  one; the check above suggests this matters little.

## Reproduce

```sh
.venv/bin/python scripts/season.py runs/season/arsenal --save "SAVE.fm" --club "Arsenal" \
    --tactic preset:Catenaccio --tactic "preset:Control Possession" ... --seeds 20 --workers 7
.venv/bin/python scripts/season.py runs/season/arsenal --report
```

Needs fmsave and imported matches between other clubs (`scripts/import_other_matches.py`) for the opponents' tactics
and the grounds; with Study 15b's results (`private/ground_home_advantage.json`) the grounds are chosen by home
advantage. About 7,600 matches for ten presets and 20 seasons in a 20-club league: 1.5-2 hours with 7 workers.
