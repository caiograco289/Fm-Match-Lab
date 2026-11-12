# Guide

The tool runs batch simulations with the **Mac** FM27 you own. It loads the unchanged `game_plugin` from your Steam
install and drives the original match engine headlessly. Technical details, evidence and validation: [`port/REPORT.md`](../port/REPORT.md).

## Requirements

- macOS on Apple Silicon or Intel. The host is an x86_64 binary; on Apple Silicon it runs under Rosetta 2.
- FM27 installed through Steam, one of the mapped builds. The host refuses any other: it checks the x86_64 slice's
  `LC_UUID`, and `scripts/build_native_mac.py` compiles the address table for the build it finds.

  | Game version | x86_64 `LC_UUID` | Engine version word |
  |---|---|---|
  | 27.0.0+2493426 | `0981AB31-AC3B-3D93-944F-47FE4B59CD9E` | 0x1b000000 |
  | 27.0.1+2494769 | `94CDDC80-8474-327A-85E0-E4FF95DC6893` | 0x1b000100 |
  | 27.0.1+2503222 (12 November hotfix) | `DD0EE157-4C9C-31A7-81DD-0D1122E62FC7` | 0x1b000100 |

  The hotfix moved two data constants and nothing the match engine uses; 36 of 36 matches played on the previous
  build replay identically on it. On a build not in this table, `scripts/setup.py` stops with "Unsupported FM27
  build" and the app runs nothing. If FM27 updates after the set-up, the app says so and asks you to run the set-up
  again.
- Steam running and logged in.
- Python 3.12 and the Xcode command line tools (`clang++`, `codesign`).
- At least one match saved by FM27 (instant result is fine): the set-up uses your newest as the sample match.
  Everything the set-up derives from your game files goes to the git-ignored `private/` folder.
- Set-up needs FM27 closed. Batches can run while the game is open (results are identical); both run slower.
- FM27 keeps only your last 10 saved matches. The app, `study.py` and `optimise.py` copy each new one into a backup
  (`~/fm27-port-work/saved_matches`) when they start and read from there, so nothing is lost as long as one of them
  runs before 10 newer matches are saved; `scripts/backup_matches.py` does the same by hand.
- FM27 also leaves the inputs of some matches between other clubs in its `Temporary` folder (`*.apm`); the backup
  keeps them too. `scripts/import_other_matches.py` turns them into matches the app and the scripts open
  (`Other_clubs` in the backup). Played on their own seed they reproduce the scores in the save (25 of 28 checked), so
  the game ran them on the same engine with the same input. `scripts/optimise.py --save` uses them as opponents.

## Build and run

```sh
python3.12 -m venv .venv
.venv/bin/pip install UnityPy                 # set-up only: reads the game's tactic data
.venv/bin/python scripts/setup.py             # host (ad-hoc signed), tactic catalogue, sample match; FM27 closed
.venv/bin/python scripts/run.py               # finds FM27 in your Steam libraries; or pass --game-root
```

Then open `http://127.0.0.1:18765` (or the port you passed with `--port`). App state is kept in `data/` in the repo.

## What works

| Area | Status |
|---|---|
| Full natural matches, seeds, batch mode, workers, cancellation | yes (about 3 s per match per worker) |
| Results: score, xG, shots, passes, possession, goals and cards with players and minutes | yes |
| Scenario editor: attributes, profiles (height, weight, …), lineups, squad size, formations, roles, duties, team and player instructions, opposition instructions, game-rule constraints | yes |
| Set-piece takers, captain, set-piece routines (tasks, backups, priorities, frequency, strategy, swing, variants) | yes |
| Import FM27 tactics (`.fmf`) and set-piece routines through the game's own parser; export both | yes |
| Set-piece episodes | yes |
| FM's installed coach presets (export used by save mode) | yes |
| Saved matches as the base: open any match FM27 saved, replay it exactly, edit and run what-ifs | yes (see below) |
| In-match management per team: assistant (substitutes, keeps your tactic), fixed, AI | yes |
| Substitutions and minutes played in the results | yes |
| Career-save mode (upstream) | removed; saved matches cover the use case |
| Set-piece routine *collections* | no |

## Your own matches (Saved matches)

1. Save your career before a match, and play the match with **instant result** (or watch it). FM27 saves it under
   `~/Library/Application Support/Sports Interactive/Football Manager 27/matches/automatic/`. Holiday matches are not
   saved on 27.0.1.
2. In the app, open **Saved matches**. Each match shows who ran each side. **Exact replay** replays it on its own seed: with the
   same game version, every reported statistic matches what the game showed. **Open in editor** loads the real squads,
   tactics, player states and set pieces into the editor. The start seed is set to the match's own seed.
3. Change anything (attributes, lineup, tactic, instructions, set pieces) and run. One match on the original seed
   shows what this exact match would have done with your change; more seeds show the spread.
4. To try the change in the game, export the tactic (FMF), reload your save from before the match, and play it.
   The game will use a new seed.

Only the values you edit are written; everything else stays as stored (fitness, morale, cohesion, the opponent's
selection and tactic). **In-match management** per team decides who acts during the match. "As saved" replays what
happened: a match you managed repeats your recorded substitutions, and a watched one makes none. "Assistant" keeps
your tactic and lets the assistant substitute, as with an instant result; use it for what-ifs on managed or watched
matches. "AI" hands the team to the AI manager, which re-plans the roles at kick-off. On the bundled sample match,
new scenarios default to "assistant"; "fixed" (no substitutions, no changes) is how every earlier batch ran.

## Engine notes

- **Engine path.** Every match the game creates starts with engine version word 0x1b000000 (FM27 27.0). The fixture
  the tool ships with was captured with 0x1a080000 (FM26.8), which sits below ~400 version branches of the engine.
  The host sets 0x1b000000 before preparation, so matches run the FM27 rules, and
  the server validates player instructions against the FM27 policy table. Jobs record the path and are not resumed
  across paths. `FM27_ENGINE_PATH=fixture` (server environment) restores the fixture word, for comparison only.

- **Goal and card events** come from the engine's end-of-match incident registry, not live hardware breakpoints
  (Rosetta has no debug registers). Minutes are exact, but per-event match-clock ticks are not recorded.
- **Results are not bit-identical to the Windows game.** Compilers and CPUs differ in floating-point code, so the
  same seed gives a different match there. Matches saved by the Mac game replay exactly.
- The host runs headless: no window is created.

## Updating after an FM27 patch

**For users.** When Steam updates FM27, the tool checks the new build before running anything. If the build has
not been mapped yet, the app says the engine is unsupported and runs nothing; it never runs against the wrong
addresses. Once a release of this repository supports the new build, update the repository and run
`.venv/bin/python scripts/setup.py` again (FM27 closed): it rebuilds the host and regenerates the tactic catalogue
and player-instruction policies from the updated game. Matches saved by the old version still open, but no longer
replay exactly on the new engine.

**For maintainers.** Mapping a build uses a local work folder outside the repository for game-file copies,
Ghidra projects and feature dumps; set `FM27_WORK_DIR` to choose it (default `~/fm27-port-work`). Paths below
written as `$FM27_WORK_DIR/...` are in that folder, and nothing in it is ever committed.

The host only accepts the build above. After a game update, the RVA tables in `port/mac_host/fm27_mac_x86_64.h` have
to be re-derived (`port/map/`), then the new `LC_UUID` added. Until then the app reports the engine as unsupported
rather than running against the wrong addresses.

**Keeping an old version usable.** Steam keeps only the newest build, so keep a local copy of the previous one
before updating (here: `$FM27_WORK_DIR/mac/27.0.0-2493426/`, outside the repository). It holds the unchanged signed `game_plugin.bundle` (sha256 `774cacde…`), the
app's `Info.plist`, and the saved matches as of the update. Nothing in it is committed. To run against it, set
`FM27_GAME_ROOT=$FM27_WORK_DIR/mac/27.0.0-2493426/game_plugin.bundle/Contents/Resources` in the environment of
`scripts/run.py` or the host. Steam still has to be running. Matches saved under 27.0 should be replayed with this
copy: a newer engine may change the result or refuse the file.

**Re-deriving the addresses (automated).** For a new build:

```sh
lipo -thin x86_64 <new game_plugin> -output $FM27_WORK_DIR/mac/<build>/game_plugin_x86_64
.venv/bin/python port/map/update_rvas.py $FM27_WORK_DIR/mac/game_plugin_x86_64 $FM27_WORK_DIR/mac/<build>/game_plugin_x86_64 \
    > $FM27_WORK_DIR/mac/<build>/rva_update.json
.venv/bin/python port/map/write_build_header.py $FM27_WORK_DIR/mac/<build>/rva_update.json \
    $FM27_WORK_DIR/mac/<build>/game_plugin_x86_64 <build> <game version>
```

`update_rvas.py` matches each function by its masked code at function starts, and checks it, or rescues it if its code
changed, through call sites in already-matched callers. Data addresses are voted from up to 12 references each.
`write_build_header.py` refuses unresolved conflicts, and reads the engine version word from the new match
constructor. Before it, run `port/map/exec_locate.py OLD_SLICE NEW_SLICE 0x4dd5f80 0x4ad49c0 > <build>/exec_locate.json`
to locate the tactical-effectiveness builder and sampler (it compares the builder's record stores; check a changed
sampler by hand, as in `port/REPORT.md`). `write_build_header.py` picks the result up. `scripts/build_catalog.py` (run by `setup.py`)
generates the build's player-instruction policy table from the game (`--policy-audit`), with FM27 closed. Then add the build to `BUILDS` in `scripts/build_native_mac.py` and to the `#elif` list in
`fm27_mac_x86_64.h`, rebuild, and validate as below. For 27.0.1 every function the host calls was found (38 by
signature, 12 by callers, 1 tie settled by callers), and all 18 data addresses agreed in 3-12 of 3-12 references.
The tactical-effectiveness builder and sampler, not found by `update_rvas.py`, were located by `exec_locate.py`. The
record layout is unchanged, and the experiment (kind 61) runs on both builds.

**Re-deriving the addresses (by hand).** The update is expected to move functions without renaming them.

1. **What to find.** Every function, global and field the host uses is named in `fm27_mac_x86_64.h`, with its Windows
   RVA in the comment. `port/map/manual_map.json` gives the evidence for each one: string, constant, call site or
   aligned decompilation, and the "via" function it was aligned through. `rva_map.json` holds the automatic matches.
2. **Old to new.** Use the previous build's x86_64 slice as the reference (a local copy, kept outside the
   repository), ideally with a Ghidra project of it already analysed. Match each address to the new slice by
   function content (Ghidra Version Tracking, or the `port/map/match.py` string, constant and call-site voting), then
   check each match the same way the original was evidenced. Struct offsets (`m_*`, `p_*`, `pp_*`, record and roster
   offsets) can move too; the host's read-back checks and layout probes (`FM27_MAC_LAYOUT_DUMP`, `FM27_MAC_RAW_DUMP`,
   `FM27_MAC_PLAYER_DUMP`) show a move as a failed check rather than a wrong result.
3. **Constants to recheck.** The engine version word (27.0: the constructor at 0x49868a0 writes 0x1b000000), the
   version thresholds, and the player-instruction policy table keyed by version.
4. **Validation.** Replay a match saved in-game after the update. Score, xG, shots, cards and goal minutes must match
   the game exactly, as they did for 27.0 (`port/REPORT.md`, in-game replay). Then rebuild with
   `scripts/build_native_mac.py` and run `tests/`.

## Where the set-up's data comes from

`scripts/setup.py` builds everything from the user's own install; the repository ships no game data.

| Part | Source |
|---|---|
| Team instructions, roles, player instructions, formations, mentalities | the game's Unity static data (`ui-staticdataentries` bundle), read with UnityPy |
| Engine bits of team-instruction options | the game's own resolver function, called by the host (`--option-bits`) |
| Engine bits of roles and duties | enum values in the game's IL2CPP metadata (`port/map/il2cpp_enums.py`, read as data) |
| Role eligibility per position, player-instruction policies | the game's own policy functions, called by the host (`--policy-audit`) |
| Position masks, mentality ids, attribute layout, set-piece options | this project's constants (`port/map/catalog_constants.json`), checked by the host |
| Sample match | the user's newest saved match (`scripts/prepare_sample.py`) |

## Contributing and publishing

Never commit anything that comes from the game or a user's save: the git-ignored `private/`, `build/`, `data/` and
`runs/` folders, saved matches (`.pkm`), tactic files (`.fmf`), engine bytes or screenshots of a real save.
`tests/test_boundary.py` enforces this: it rejects game and binary files, private folders, long hex runs (raw
bytes), personal paths, and any term listed in your own git-ignored `private/personal_terms.txt` (your name, user
name, machine name). Screenshots in `docs/images/` are of the sample match in sample mode, where the app shows
generic names. Run `.venv/bin/python -m unittest discover tests` before every commit.

`scripts/public_snapshot.py` prepares a public copy in a separate repository: it copies the tracked files, commits
them under an anonymous identity with UTC times, and runs the tests with `FM27_PUBLISH_CHECK=1` (which also checks
every commit's author and time zone). It never pushes.

