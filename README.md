# FM27 Match Lab for macOS

Run Football Manager 27's own match engine on your Mac, outside the game: replay matches you played, change
attributes, lineups, tactics, instructions or set pieces, and simulate thousands of matches to see what difference
the change makes.

It loads the unchanged match engine from **your own Steam install** of FM27 and drives it headlessly. Nothing from the
game is included in this repository.

This project began as a macOS port of [FM Tactics Lab](https://github.com/lqf0624/fm-tactics-lab) by **lqf0624**
(Windows, MIT licence). The browser UI, scenario model and much of the server come from that project. The macOS
engine host, address mapping, saved-match replay, in-match management and the studies are new. Upstream is now a
reference only: this repository is macOS-only and does not track or support the Windows tool.

> Personal-use interoperability project. Not affiliated with or endorsed by Sports Interactive or SEGA. Football
> Manager is their trademark.

![The tactics board: both phases, team instructions and the run bar](docs/images/tactics-board.png)

## What you can do

- **Replay your own matches.** Open any match FM27 saved, replay it exactly (same score, xG, shots and goal minutes
  as the game showed), then change something and see how the match would have gone.
- **Batch simulations.** Run hundreds or thousands of seeds of a scenario on several workers (about 3 s per match
  per worker) and compare results: points, goals, xG, shots, possession, cards, substitutions and minutes.
- **Edit everything the engine reads:** player attributes and profiles, lineups, formations, roles and duties, team,
  player and opposition instructions, set-piece takers and routines, and who manages each side during the match
  (your assistant, a fixed tactic or the AI manager).
- **Import and export FM27 tactics** (`.fmf`) and set-piece routines through the game's own parser.

## Studies on your own matches

For questions with many conditions ("what is each attribute worth for my team?"), `scripts/study.py` replays your
saved matches under each condition on the same seeds and reports paired differences with t values:

```sh
.venv/bin/python scripts/study.py new runs/my-study --team "Your Club" --newest 10
.venv/bin/python scripts/study.py add runs/my-study attributes familiarity:20 instructions
.venv/bin/python scripts/study.py run runs/my-study        # resumable; FM27 closed
.venv/bin/python scripts/study.py report runs/my-study
```

| Player editor | Results of a comparison |
|---|---|
| ![Player attributes](docs/images/player-attributes.png) | ![Paired comparison of two tactics](docs/images/results.png) |

Screenshots show the sample match, where the app uses generic player names.

**What we found:** [docs/FINDINGS.md](docs/FINDINGS.md) summarises six studies of the engine (about 190,000
matches); the full studies are in [docs/studies/](docs/studies/README.md). Using an AI agent? Point it at
[AGENTS.md](AGENTS.md): the rules, the set-up and how to design and read a study.

## Requirements

- macOS on Apple Silicon (via Rosetta 2) or Intel.
- FM27 installed through Steam, at a supported version: **27.0.0** or **27.0.1**. Other builds are refused until
  they have been mapped (see "Game updates" in the guide).
- Steam running and logged in. The tool does not bypass or emulate Steam, DRM or any online service.
- Python 3.12 and the Xcode command line tools (`clang++`, `codesign`).
- FM27 itself closed while simulations run.

## Set-up

```sh
git clone https://github.com/caiograco289/Fm-Match-Lab.git && cd Fm-Match-Lab
python3.12 -m venv .venv                       # the app itself needs only the standard library
.venv/bin/pip install UnityPy                  # used once by the set-up, to read the game's tactic data
.venv/bin/python scripts/setup.py              # one-off, and again after a game update
.venv/bin/python scripts/run.py                # then open http://127.0.0.1:18765
```

`setup.py` builds the engine host for your installed FM27, builds the tactic catalogue (roles, instructions,
policies) from the game's own data, and makes your newest saved match the sample match. Play at least one match in
FM27 first (instant result is fine). It reads the game's files and runs its engine functions; it never changes them.

Tests: `.venv/bin/python -m unittest discover tests` (add `FM27_INTEGRATION=1` to also replay your newest saved
match through the engine).

Everything derived from your game files stays in the git-ignored folders `private/`, `build/` and `data/`.

## Documentation

- [docs/MACOS.md](docs/MACOS.md): full guide: what works, saved matches, in-match management, game updates.
- [docs/studies/](docs/studies/README.md): engine studies (attribute values, familiarity, tactics, …).
- [docs/RESEARCH.md](docs/RESEARCH.md): running the engine host directly; research switches.
- [port/REPORT.md](port/REPORT.md): the technical notebook of the port: how each engine function was located and
  validated, with all findings and corrections.
- [port/PLAN.md](port/PLAN.md): the original port plan and ground rules.

## Licence

MIT, see [LICENSE](LICENSE). The licence covers this repository's code only; it does not cover the game or anything
derived from it. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
