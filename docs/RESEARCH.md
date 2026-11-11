# Engine host reference: options and research switches

The app drives the engine host (`private/engine/fm27_native/fm27_mac_host`, built by `scripts/build_native_mac.py`). You can
also run the host directly, for example to replay a saved match or dump what the engine computed. Every option here
reads or writes only the host's own process memory and its output file. Nothing touches the game install, and the
game must be closed while you run any of them.

The host prints one JSON object per line to `--output`. Research output can contain data derived from your game
files, so keep it in git-ignored folders (`port/mac_host/runs/`, `private/`, `build/`).

## Command-line options

| Option | Purpose |
|---|---|
| `--fixture <match.pkm>` | Match to play: a match FM27 saved (`matches/automatic/…_VER_fm.pkm`) or the bundled sample |
| `--seed <n>` | Random seed. A saved match on its own seed (the number in its file name) replays exactly |
| `--scenario-file <file.bin>` | Edits written before kick-off, as encoded by the app (`encode_scenario`) |
| `--output <file.jsonl>` | Event log |
| `--worker-manifest <file>` | Play many matches in one process (the app's and the studies' batch mode) |
| `--cancel-event <path>` | Stop when this file appears |
| `--tick-step <n>` | Engine steps per loop iteration (default 1) |
| `--dump-input <file.json>` | Write the match input before preparation (squads, attributes, profiles, tactics, set pieces) |
| `--inspect-fixture` | With `--dump-input`: dump and exit without playing |
| `--check-image <game_plugin>` | Check that the installed engine is a mapped build |
| `--policy-audit` | Write the build's player-instruction policy table (used by `build_native_mac.py`) |

## Environment: app and studies

| Variable | Purpose |
|---|---|
| `FM27_GAME_ROOT` | FM27 install (Steam folder, `fm.app` or `game_plugin.bundle/Contents/Resources`); found automatically if unset |
| `FM27_ENGINE_ROOT` | `private/engine` (set by `scripts/run.py`) |
| `FM27_DESKTOP_DATA` | App state folder (default `data/`) |
| `FM27_SAVED_MATCHES` | Folder to list saved matches from instead of FM27's own (for example a backup of 27.0 matches) |
| `FM27_ENGINE_PATH=fixture` | Keep the bundled sample's FM26.8 engine word instead of the FM27 one (comparison only) |
| `FM27_SKIP_EVENT_DETAILS` | Fast mode: no goal/card/player detail |
| `FM27_STUDY_HOST` | Study scripts: use this frozen host binary, so a long run stays on one build |

## Research switches (host)

Data writes are made between engine steps in the host's own memory. They are experiments, not features: results
with them are not what the game would produce.

| Variable | What it does |
|---|---|
| `FM27_MAC_RECORD_SUMMARY=1` | Log every player's tactical-effectiveness record after preparation and at full time: the five builder fields, player id and all 34 bytes (decode with `port/map/exec_record.py`; field meanings in `docs/studies/03-tactical-familiarity.md`) |
| `FM27_MAC_EXEC_FIELDS="side[@slot.slot]:offset=value,…"` | Hold record bytes at fixed values (Studies 3 and 6) |
| `FM27_MAC_ATTR` | Hold attribute values during the match (attribute studies) |
| `FM27_MAC_INPUT_FLAGS_AFTER_PREP="home,away"` | Set the manager input-flag words after preparation (−1 keeps one); the app's in-match option uses the same mechanism through the scenario |
| `FM27_MAC_LIVE_AFTER_PREP=1` | Clear the manual-input flag after preparation |
| `FM27_MAC_ENGINE_VERSION=<word>` | Override the engine version word (no policy table follows it) |
| `FM27_MAC_EXEC_ACCESSOR_TEST=<n>` | 27.0.1: call the game's record accessor on n random records (checks `exec_record.py`) |
| `FM27_MAC_XG_DUMP=<file>` | Dump the xG model store layout |
| `FM27_MAC_XG_KEY="a=b"` or `"a<>b"` | Rename or swap an xG model group key in memory (shows that xG takes part in decisions) |
| `FM27_MAC_FAMILIARITY_DUMP=<file>` | Per-player lists at player+0xa58 and +0xb30 (the latter is a training log) |
| `FM27_MAC_STAFF_SET`, `FM27_MAC_STAFF_PROBE` | Write or inspect the match-side manager/staff block |
| `FM27_MAC_PLAYER_DUMP`, `FM27_MAC_RAW_DUMP`, `FM27_MAC_LAYOUT_DUMP`, `FM27_MAC_STATS_PROBE`, `FM27_MAC_ROSTER_TRACE` | Layout calibration and checks |
| `FM27_MAC_PKM_INCIDENTS`, `FM27_MAC_RESTART_PROBE`, `FM27_MAC_ROUTINE_PROBE`, `FM27_SETPIECE_FLAGS_AUDIT`, `FM27_FMF_AUDIT` | Incident, restart, set-piece and FMF parser probes |
| `FM27_COACH_PRESET_EXPORT=1` | Export the installed tactic presets (styles, templates, formations) from the game's data |
| `FM27_IMPORT_FMF`, `FM27_IMPORT_TAC`, `FM27_EXPORT_TAC`, `FM27_EXPORT_SIDE`, `FM27_EXPORT_TITLE` | Tactic import/export through the game's parser and serializer (used by the app) |
| `FM27_EPISODE_TYPE`, `FM27_EPISODE_SIDE`, `FM27_EPISODE_SECONDS` | Set-piece episode mode (used by the app) |

## Examples

```sh
# replay a saved match exactly and dump the effectiveness records
FM27_MAC_RECORD_SUMMARY=1 private/engine/fm27_native/fm27_mac_host \
  --fixture ".../Team_v_Chelsea_156293044_VER_fm.pkm" --seed 156293044 --output runs/chelsea.jsonl

# the same match with the eight tactical areas of every player on side 0 (the team) held at 100
FM27_MAC_EXEC_FIELDS="$(python -c "print(','.join(f'0:{o+k}=100' for o in range(1,25,3) for k in (0,1,2)))")" \
  private/engine/fm27_native/fm27_mac_host --fixture ... --seed 156293044 --output runs/chelsea_areas100.jsonl
```
