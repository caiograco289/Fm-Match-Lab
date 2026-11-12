# Third-party notices

## FM Tactics Lab (upstream)

This project is derived from [FM Tactics Lab](https://github.com/lqf0624/fm-tactics-lab) by lqf0624, released under
the MIT licence. Its copyright notice is kept in [LICENSE](LICENSE). The browser UI, scenario model and much of the
Python server originate there.

## The game

Football Manager 27 is © Sports Interactive / SEGA. This repository contains no game binaries, no game data, no
extracted function bytes and no saved games. It holds addresses, digests, structure offsets and metadata needed to
call the engine of a copy the user owns, which is loaded unchanged from the user's own installation at run time.
Anything derived from game files on the user's machine is written only to the git-ignored `private/`, `build/` and
`data/` folders.

One exception: `src/reference_squads.json` holds **synthetic reference squads**: invented players with invented
names, generated at random by `scripts/reference_squads.py` from statistical profiles (averages, spreads and
correlations of attributes by position and tier) of the FM27 player database, calibrated on version 27.0.1+2503222
(database 27.0.0, Premier League clubs at the start of the 2026/27 season). They are not real players: every
generated player was checked to be farther from every real player than real players usually are from each other.
The profiles and the save they come from are not in the repository.

The MIT grant does not relicense game-related inputs, derived data or trademarks.

## Python packages

The app itself uses only the Python standard library.

- capstone is used only by the address-mapping tools in `port/map/`; numpy by those tools and by the tactic search
  (`scripts/optimise.py`) (BSD-3-Clause each).
- fmsave (MIT, https://github.com/rhiever/fmsave) is optional and not bundled. It reads squads and fixtures from your
  saves for `scripts/squad_from_save.py`, `study.py league --squad`, `optimise.py --save`, and to name the clubs in
  `scripts/import_other_matches.py`; everything else runs without it.
- UnityPy (MIT) is used only by the set-up (`scripts/build_catalog.py`) to read the game's tactic data.
