# FM Tactics Lab: Mac port report

Branch `mac-port`, based on upstream `lqf0624/fm-tactics-lab` @ `de5368c` (v1108.5).

## Phase 0: Inventory (2026-11-08)

### Host system
| Item | Value |
|---|---|
| macOS | 13.0.1 (22A400), Darwin 22.1.0 |
| CPU | arm64 (Apple Silicon), Rosetta 2 running (`oahd`) |
| RAM / free disk | 16 GB / ~62 GB free |
| Compiler | Apple clang 14.0.0 (CommandLineTools) |
| Python | 3.12.11 (miniforge) |
| Homebrew | /opt/homebrew |
| JDK | Corretto 11 (system). Temurin 25.0.5 in `$FM27_WORK_DIR/tools/` (SHA-256 checked against Adoptium). Ghidra 12.2 needs **JDK 25** |
| Ghidra | **12.2** (latest; plan said 11.x) in `$FM27_WORK_DIR/tools/ghidra_12.2_PUBLIC`, zip SHA-256 `2c2cd776…be67` matches release notes. The macOS decompiler was built locally with `gradlew buildNatives` (the release ships only Linux/Windows natives). The Homebrew formula was abandoned: on macOS 13 it builds the whole dependency tree, including OpenJDK, from source |
| DepotDownloader / SteamCMD | not installed. The user runs DepotDownloader by hand (needs their Steam login). A file list is ready at `$FM27_WORK_DIR/win/filelist.txt` |
| Steam | running (`steam_osx`), FM27 app 4530370 installed |

### FM27 Mac install
Root: `~/Library/Application Support/Steam/steamapps/common/Football Manager 27/fm.app`

| Item | Value |
|---|---|
| CFBundleShortVersionString | **27.0.0.2493426** (matches upstream reference `27.0.0+2493426`) |
| Steam buildid | **26340721** (matches the build mapping in the plan) |
| Signing | Team `3JJX9QL35J`, hardened runtime (`flags=0x10000`) |
| Entitlements | `allow-dyld-environment-variables`, `disable-library-validation`, camera, photos. **No `get-task-allow`** |
| Main exe | `Contents/MacOS/Football Manager 27`, universal; SHA-256 `a4f17651…80aca` |
| Main exe UUIDs | x86_64 `10EA884D-9D68-353A-A24E-576E76DCAE30`, arm64 `A681C867-120A-327E-957C-4D968ACE4047` |
| Engine | `Contents/PlugIns/game_plugin.bundle/Contents/MacOS/game_plugin`, universal, 192,253,504 bytes |
| Engine SHA-256 (fat file) | `774cacde63567fd3901c47719e7a6ed94cc3a0a62e9b94989dcac6b4890ec0e1` |
| **Engine UUID x86_64** | `0981AB31-AC3B-3D93-944F-47FE4B59CD9E` |
| **Engine UUID arm64** | `F4540355-2186-39CB-9119-C706A6A35346` |
| Engine LC_RPATH | `@loader_path/../Frameworks` |
| Engine deps (bundled) | `libsteam_api.dylib`, `libEOSSDK-Mac-Shipping.dylib`, `PlayFabPartyMac.framework`, `PlayFabMultiplayerFramework_macOS.framework` |
| Engine deps (system) | libSystem, libc++, libobjc, CoreFoundation, CoreServices, Foundation, SystemConfiguration, CFNetwork, Security, Metal, AppKit, IOKit, CoreGraphics |
| Other plug-ins | BacktraceMacUnity, GadsmeMacPlugin, lib_burst_generated |

### Windows reference (STOP b: approved, downloaded 2026-11-08)
| Item | Value |
|---|---|
| Expected `game_plugin.dll` SHA-256 | `252ff8fb5b7a4a5a5464db6ba632e309eef9b6e65ffa992ae20575a189e66c6a` (`native/adapter_version.json`) |
| Actual | **`252ff8fb5b7a4a5a5464db6ba632e309eef9b6e65ffa992ae20575a189e66c6a` (MATCH)** |
| Source | DepotDownloader 3.4.0, run by the user with their own Steam login (QR), app 4530370, branch `public`, depot 4530372 manifest 8917922912096381935 (2026-10-31); only the 2 files from `filelist.txt` were fetched |
| Size | 404308480 bytes |
| `steam_api64.dll` SHA-256 | `eb17909a76668cf9ae0b92a618a34a50f6c73d3a6787cb4dd8ce36a8b10bfb75` |
| Location | `$FM27_WORK_DIR/win/depot/fm_Data/Plugins/x86_64/` (outside the repo, never committed) |

### Target list size (rough count, for Phase 2)
About 110 `at(0x…)` call sites in `native/` (56 in `desktop_host.cpp`, 22 in `native_coach_presets.h`, the rest spread over 8 headers), plus the `ranges` and `data_addresses` in `profile_metadata.json`.

### Not yet checked
- `scripts/prepare_private.py` on macOS: it needs the upstream release EXE as input, which we don't have yet.

## Phase 1: Feasibility spike (done: GO)

`port/spike/load.c`: `dlopen(game_plugin, RTLD_NOW|RTLD_LOCAL)` from our own unsigned process, with
`SteamAppId=SteamGameId=4530370`, Steam running, cwd `$FM27_WORK_DIR/spike-cwd`, bundle used in place
and not modified.

| Slice | Result |
|---|---|
| x86_64 (Rosetta) | **Loads.** Static initialisers run (EOS "[UE4] Shutdown handler", PlayFab Party). game_plugin image base e.g. `0x116382000`, cputype `0x1000007`. Clean exit. |
| arm64 (native) | **Loads.** Same initialiser output, cputype `0x100000c`. Clean exit. |

- `@rpath` dependencies resolve from the bundle's own `Frameworks/`; no `DYLD_LIBRARY_PATH` or copies needed.
- No files were written (PlayFab only logs a path in `~/Documents`; nothing was created).
- **Mapped-function call (2026-11-09): PASS.** `port/spike/go_test.cpp` (x86_64, Rosetta, Steam running) `dlopen`s the
  bundle and calls Mac `0x55afb0`, the twin of Windows `0x64fe90` (`unsigned(*)(unsigned)`, team-instruction value →
  option bit; matched with const + consts_sim + callgraph). For all **103** entries of upstream's
  `fm27_team_options[]` (`native/fm27_tactic_bindings.h`) the result equals the expected bit: **103/103**, including
  **75 distinct non-zero bits**. No crash, clean exit.
- Spike bug to fix: the image filter matches every dylib under `game_plugin.bundle/`; filter on `/MacOS/game_plugin` instead.

**Verdict: GO for route A (standalone host).** The bundle loads in our own process on both slices, and a mapped engine
function returns correct data. Route B (injection) isn't needed.

## Phase 2: Address mapping (started)

### Step 1: target list (done)
`port/map/extract_targets.py` writes `port/map/targets.json` (re-runnable; reads upstream source and metadata only).

| | Count |
|---|---|
| Distinct Windows RVAs used by the host | **109** |
| of which code (functions) | 81 (80 in `.text`, 1 in `.sbss`) |
| of which data (globals and vtables) | 28 (22 RW, 6 RO) |
| Kinds | 105 via `at()`, 2 hooked via `execution_redirect()` (`0xd85a0`, `0x41a50`), 1 instruction-pointer compare (`0x51a90`) |
| Compatibility ranges in `profile_metadata.json` | 95 (73 code, 15 saved-fixture reader/factory, 3 factory jump, 2 vtable, 2 plan serializer); 32 contain no `at()` target (callees checked transitively) |

### Findings
- **In-memory hooks.** `execution_redirect()` patches engine entry points in the host's own memory (not on disk). Phase 4 needs a Mac
  version (`mprotect`/`vm_protect`; on arm64 also W^X and icache flush). Function-pointer globals are also
  overwritten (`0x5701a00`/`0x5701a08` ← `0xdf78e0`/`0xdf7a20`).
- **Mac slice anchors.** Game C++ symbols are stripped (5,763 exported C++ symbols, all ICU/std; 16,705 in total, mostly OpenSSL).
  Usable anchors: 233 `CLASS::method` assert/log strings, 180 build source paths
  (the match engine's source files are named in them),
  ~580 `db::` Itanium type names.

### Step 2: Ghidra analysis
- Mac x86_64 slice (`lipo -thin` copy in `$FM27_WORK_DIR/mac/`): **full auto-analysis done** (2,922 s ≈ 49 min, no errors, though with the 2 GB default heap, see below; project
  `$FM27_WORK_DIR/ghidra/fm27`, 1.3 GB, log `$FM27_WORK_DIR/logs/analyze_mac_x86_64.log`).
- Windows DLL, first attempt: full auto-analysis was stopped after ~9 h. It was still decompiling inside a very large
  section (`.sbss`, about 293 MB) that the Mac build doesn't have. Log kept as `logs/analyze_win_full_aborted.log`.
- Windows DLL, second attempt (2026-11-09): that section excluded from the analysis (in the Ghidra database copy only;
  the DLL is untouched), then `.text` and data analysed. The 4 host targets inside
  `.sbss` need a separate later pass. Stopped after 1 h 49 min: still stuck in the no-return "Repair Flow Damage"
  pass (log kept as `logs/analyze_win_text_aborted.log`).
- Windows DLL, third attempt (2026-11-09): same exclusion, now also turning off
  `Non-Returning Functions - Discovered.Repair Flow Damage` (not needed for function matching).
  Moved quickly through the stages (switch tables, constant propagation, scalar operands), then died about 35 minutes in with
  `OutOfMemoryError`. **Root cause:** Ghidra 12.2 ignores `MAXMEM`; the heap is set by `GHIDRA_HEADLESS_MAXMEM`. Every
  run so far (including the Mac x86_64 one) used the 2 GB default, which also explains the slow, GC-heavy runs.
  (Logs: `logs/analyze_win_oom_2g.log`, `logs/win_stages_oom_2g.log`.)
- Windows DLL, fourth attempt (2026-11-09): same exclusion, `GHIDRA_HEADLESS_MAXMEM=11G` (checked: `-Xmx11G`).
  Stage and memory are sampled every 5 min to `logs/win_stages.log`.
  Died about 40 minutes in with the **identical** `OutOfMemoryError` (same stack, same log size), so it's deterministic and not
  about heap size: `AddressTableAnalyzer.added` → `AddressSet.subtract` explodes on this DLL.
  (Logs: `logs/analyze_win_oom_11g.log`, `logs/win_stages_oom_11g.log`.)
- Windows DLL, fifth attempt (2026-11-09): also turns off `Create Address Tables`. Switch tables come
  from `DecompilerSwitchAnalyzer` and vtables from RTTI, so matching shouldn't need it.
  **Succeeded:** 2,746 s (≈46 min), peak ≈5.6 GB, **148,756 functions**, 974,058 symbols, saved as `fm27:/game_plugin.dll`.
  (Mac x86_64 for comparison: 121,090 functions, 728,866 symbols.)
- **Use `GHIDRA_HEADLESS_MAXMEM`, not `MAXMEM`,** for all later headless runs (Mac arm64, feature export).

### Step 2b: function fingerprints (done, 2026-11-09)
`port/ghidra_scripts/ExportFunctionFeatures.java` writes one JSON line per function (strings, distinctive
constants, callees, ordered calls, globals, size) to `$FM27_WORK_DIR/features/` (outside the repo).
Windows: 143,828 functions (thunks included). Mac x86_64: 120,437. Mac image base is 0, so a Mac RVA is
the offset from the `dlopen` base.

**Windows stubs.** 9 of the host's targets are 1-instruction Windows stubs (`thunk_EXT_FUN_…`)
jumping into the excluded `.sbss` section. In total **4,168** engine functions exist on Windows only inside
that section (24,792 calls from normal code). The matcher adds them as body-less nodes and
matches them through their callers. They stay "unverified" until confirmed on the Mac side.

### Step 3: matching (first results)
`port/map/match.py` → `port/map/rva_map.json`. Pipeline: unique-string anchors (3,836), unique-constant
anchors (2,351), call-graph propagation; then evidence tagging (`string`, `const`, `strings_sim`,
`consts_sim`, `callgraph`, `callseq`, and `size` as support only). **34,844** Windows functions matched overall.

**Precision check.** Starting from constant anchors only, call-graph propagation reproduced the independent
string-anchor matches **97.4 %** of the time (2,273/2,333). Constant anchors agreed with string anchors 98.1 %
(371/378). So single-evidence matches are wrong about 1 time in 40. Hence the 2-kinds rule.

| Host targets (109) | Count |
|---|---|
| verified (≥ 2 kinds) | 17 |
| unverified (1 kind, or a protected body) | 34 |
| unmapped | 23 |
| blocked: mid-function code locations (need instruction-level alignment) | 7 |
| data addresses (not started) | 28 |

**Key match:** detailed match step Windows `0x4520bd0` → **Mac x86_64 `0x498afc0`** (unique assert string
about calling the match's play method in the wrong state, + call graph; 293 vs 289 instructions).

Next: second evidence for unverified targets, mid-function locations (`0x4520d2e`, `0x4520f05`,
`0x4520f4c` inside the match step; `0x51a90`, `0x8375c`, `0x1866c1`, `0x49870d0`), data globals.

## Milestone (2026-11-09): first full FM27 match on macOS

`port/mac_host/fm27_mac_host.cpp` + `port/mac_host/fm27_mac_x86_64.h` (x86_64 slice, Rosetta, Steam running) run upstream's
core pipeline against the unchanged `game_plugin` from the FM27 install:

ICU from `Resources/icudt65l.dat` → resource managers → `simatch.fmf` + `simatchshared.fmf` (2 roots) → index (status 0)
→ xG folder (132 entries) → original bootstrap (accepted; 12 version groups / 132 models) → PKM via FM's reader →
MATCH ctor + benchmark vtable + thread-local match context → deserialize (accepted) → prepare (gates 1,1,1) →
`MATCH::play` step loop → **natural finish** (≈23,100 quarter-second clock ticks ≈ 96 min, ~3.5 s simulation).

**Determinism (Phase 6.1): PASS.** Same seed twice → byte-identical event logs (except wall-clock timings).
Seeds 1–5 → 2-1, 2-1, 1-2, 0-2, 1-2, 3-3 (seed field verified: identical PCG seeding expression
`seed*0x5851f42d4c957f2d+0x5851f42d4c957f2e` in both deserializers; Windows `+0x20`, Mac `+0x18`).

### Method notes (Phase 2/3)
- Decompiled pairs (`port/ghidra_scripts/DecompileFunctions.java`, `port/map/decompile.sh`) of the original routines the
  host imitates ("test match" runner `0xa84cd0`/`0x2a0d4d0`, main init `0x1d22d0`/`0x296c0`, bootstrap, resource setup)
  gave most core-path mappings with statement-level evidence → `port/map/manual_map.json`.
- Call-site voting (`port/map/callsite_vote.py`): independent per-target evidence; it caught 2 wrong matcher picks
  (allocator → `operator new`; string ctor → `0x4884ba0`, 1,061 votes).
- Displacement voting (`port/map/offset_vote.py`): Mac twin of a Windows struct offset, e.g. teams `0x15380→0x15370`
  (225/238), score context `0x14ea0→0x14e90` (109/109).
- ABI rules found: Itanium vtables have 2 destructor slots (Windows slot n≥1 → Mac n+1); refcount release
  `vtable[0](p,1)` → `vtable[1](p)`; by-value returns: MSVC `(this,&ret)` vs Itanium `(&ret,this)`; ≤16-byte struct
  returns in registers on Mac (reader factory loses its first argument).
- MATCH layout: size `0x155b0`→`0x15590`; early fields −8 (seed), `0x12d40…0x15588` −0x10, `0x155a0` −0x18.
  Resource manager `0x110`→`0x1c0` (roots `0x78`→`0x118`, file system `0xc0`→`0x160`). Interface object `0x48`→`0x60`.

## Phase 3: layout calibration (in progress)

New tools: `port/map/offset_vote.py` (now also over register-relative displacements exported as `disps`),
`port/map/layout_align.py` (aligns the Mac host's raw dump, `FM27_MAC_RAW_DUMP`, against upstream's Windows dump
of the same fixture in `private/.../editor_manual_default.json`). Votes alone proved unreliable for small offsets
(e.g. `team+0x121` voted +0, data says +8); every adopted offset has data or decompiled-code support, listed with
its evidence in `port/mac_host/fm27_mac_x86_64.h`.

Layout findings (Windows → Mac x86_64):
- TEAM: `0x10–0x40` +0; `0x80–0x138` +8 (roster `0x138→0x140`, adjustment `0x121→0x129`); count `0x72d→0x73d`;
  manager pointer `0x630→0x640`.
- MATCH_PLAYER: uniformly −8 from `0x4c` up to at least `0xdb8` (attributes `0x480→0x478`, height `0x6c→0x64`,
  cells `0xce0/0xdb8→0xcd8/0xdb0`); back to +0 by `0x1bf0` (slot byte `0x1e27` unchanged).
- MANAGER: three tactic-plan blocks with stride `0x7a8` (Windows) vs `0x7c0` (Mac); inside a block the shift grows
  −0x18 (creator) → −0x10 (cells) → +0 (slot map). Block model predicted the slot-map copies at `0x2774`/`0x2f34`
  and the kind-3 byte at `0x2885`, all confirmed in data. OI array `0x16f8→0x16e0`, OI rows `0x1748→0x1730`,
  routines `0x8f0→0x8e8`, input flags `0x30a0→0x30d0`.
- ABI: Mac effective-OI function returns the 3 packed bytes in EAX (Windows writes an out buffer).

**Engine-derived validation on Mac (every run):** effective opposition instructions for 22/22 players and
player tactic bindings for 22 players × 2 phases match the manager plans after native preparation.

**Scenario editor port** (`port/mac_host/fm27_mac_scenario.h`): kinds 1–7, 10–12, 13 (without game-constraint
role checks), 14, 15, 17, 18, 20, 21, 46, 60, 61 ported with read-back. Not yet ported (explicitly rejected
with `scenario_kind_not_ported`): 30/31 (priority lists, captain), 40–45 and 47 (set-piece routines), 13 with
constraints on. **Note:** upstream's encoder always emits set-piece records, so the UI path needs 40–47.

## Phase 4: Mac host feature status (2026-11-09)

`port/mac_host/` now produces every event upstream's Python post-processing requires:
worker manifest mode (`FM27DW1`, bootstrap once, per-match release, `.worker_done` markers; 3 matches in 9.1 s),
scenario apply/read-back, `native_opposition_effective_verified`, `native_player_tactic_bindings_verified`,
`native_match_statistics` (team record `team+0x6a0`), `native_player_match_totals` + identity check (40/40 records),
`native_final_incident_registry` (context `+0x38`), `native_event_observer_stopped`, `original_match_release_completed`
(`tls_context_cleared: true`), `native_image_fingerprint`, `native_engine_compatibility`, `steam_session_cleanup`.
Cancellation: `--cancel-file PATH` (macOS has no named events; `--cancel-event` is accepted as a file path).

Consistency over seeds 3/5/11/17/23 (+ scenario with 165 attribute and 11 height edits): registry goals = score =
player totals in every match; registry yellow cards = player-total yellow cards.

ABI rule #4: MSVC member functions return class types through a hidden pointer `(this, &ret, args)` even when 4
bytes; Itanium returns them in EAX: person key `= vtable[63](iface, player+0x20)`.

Differences from the Windows host, by design:
- No hardware-breakpoint event-queue observer (x86 debug registers are not available under Rosetta). Goals and cards
  come from the engine's final incident registry, which upstream's collector already accepts when it agrees with
  the native totals and score (`goal_source: original_final_incident_registry`). Per-goal clock positions from the
  live queue are therefore not available on macOS.
- The match object is allocated by the host (calloc + original ctor/dtor) rather than from the engine's GAME_MATCH pool.
- Optional diagnostics not ported: coach-preset export, FMF probe, saved-fixture probe, AI-tactics reader, source
  generation (`FM27CFG2`), execution experiment, stats audit (debug registers).

## Phase 5: Python app on macOS (2026-11-09): working

- `src/desktop_platform.py` + small edits (Windows paths unchanged): host name `fm27_mac_host`, engine discovery from
  the Steam library (`libraryfolders.vdf`) → `game_plugin.bundle/Contents/Resources`, file lease (open handle +
  identity check), file-based cancellation, memory sizing, AppleScript save picker, no `CREATE_NO_WINDOW`.
- `scripts/build_native_mac.py` builds and ad-hoc signs the host into `private/engine/fm27_native/` and writes the Mac
  `engine_compat_profile.json` (local SHA-256 + LC_UUID). `scripts/run.py` runs on macOS with Python 3.12
  (`.venv`, `pip install -r requirements.txt`).
- The app reports the engine as **verified** ("Engine key interfaces check passed"; at the time the UI was in Chinese, profile `fm27-27.0.0+2493426-macos-x86_64`).
- **End-to-end:** the app's own `/api/run` with its default scenario (369 records, game rules) completed **20/20** matches
  in 60 s (1 worker), every match passing upstream's post-processing (read-back, bindings, statistics ranges,
  registry vs totals for goals and cards).
- Bug found and fixed on the way: `root/'fm27_native/'+name` precedence (TypeError swallowed by the job pool).
- Game constraints (kind 13) ported: OOP role mask Windows `0xbb5b0` (stub → `0xbb5c0(pos,1,count)`) ↔ Mac `0x4ed6020(pos,count)`.

## Phase 6: validation status

- 6.1 Determinism: **PASS** (identical logs for repeated seeds; seeds change outcomes).
- 6.2 Cross-platform statistics: see "Phase 6.2 results" below.

## FMF tactic import (ported)

- `port/mac_host/fm27_mac_fmf.h`: Mac twin of `native_fmf_probe.h` + `native_tactic_import.h`. The user's archive is
  opened by the game's archive driver (`file_open`/`folder_open`, as for `simatch.fmf`) and read through the game's
  reader factory; the TAC plan is parsed by the game's parser (Windows `0x16fca0` ↔ Mac `0x4de9870`, 6/6 caller votes).
- Evidence: archive layout runtime-dumped on Mac (folder `+0x30` directories, `+0x38` files; node `+0x18` title,
  `+0x38` size: identical to Windows). Parser pair decompiled: stream vtable tell/seek/read at Mac slots 3/4/6
  (Windows 2/3/5; seek returns in RAX), error flag `+0x10` on both. Parser base Mac `manager+0x1800` (Windows `+0x1818`):
  its fields land exactly on offsets already runtime-verified by the scenario port (bits `+0xe0`→`0x18e0`, version
  `+0xf0`→`0x18f0`, cells `+0x120`→`0x1920`, map `+0x7b4`→`0x1fb4`).
- Result: user tactics `ZaZ - Ace of Clubs 0.1 ST` and `424 ROUTE1 TORQUAY P93` accepted by the original parser with
  every byte consumed (3557/3557, 2125/2125); `/api/import-fmf` imports both; a 6-seed `/api/run` with the imported
  tactics completed 6/6 with all post-processing checks passing.
- Set-piece routine archives are detected (details handler) and rejected with `scenario_kind_not_ported` (exit 174).
- Host: an empty `FM27_GAME_ROOT` (as the app passes) now falls back to the Steam install; default fixture/output
  resolve next to the executable, as on Windows.

## Coach preset export (ported)

- `port/mac_host/fm27_mac_presets.h`: Mac twin of `native_coach_presets.h` (`FM27_COACH_PRESET_EXPORT`).
- Resource type: Windows `c53910(resources, 0x57169e0)` ↔ Mac `0x4862810(resources, 0x5c8c2c0)`; `0x5c8c2c0` is the same
  argument of the decompiled pair `0xc5f7d0`/`0x486b230` ("xml_resource_record_data"). Windows' protected `0x16c921e0`
  builds that descriptor; on Mac the static initialisers already did (checked at runtime: descriptor initialised).
  Key symbols via `0x9bc480↔0x4889b80`. Style-record attribute symbols ("tactical_style_id"/`stID`, ...) are registered
  by the game's own `0x4f38e50`, normally called from game startup `0x296c0`; without it every style code read 0.
- match_folder binding: the file-manager map (`0x5c5cf40`, tree at `+0x18→+8`) is a libc++ `std::map<symbol, folder>`
  (node key `+0x20`, value `+0x28`, layout read from the inlined lookup in `0x4dcd1e0`). The host inserts the
  installation's `simatch.fmf` folder under symbol `0x5cd7d08` (as Windows does via `0x7a4310`) with libc++'s
  insert + `__tree_balance_after_insert`, then verifies with the game's own accessor `0x4dcd1e0` (succeeds).
- Loader `0x2c9a0`/`0x5c60430`, load `0x4dcd340`; plans are parsed by the TAC parser `0x4de9870` into `new(0x7c0)`
  objects, so plan fields use the parser layout (bits `+0xe0`, name `+0xf8`, style `+0x100`, cells `+0x120`, map `+0x7b4`).
  Formations: valid `0x50c8c20`, plan ctor `0xd2900(plan, 0x58d1718, 1)` (same call in the decompiled loader pair as
  Windows `0x160930(plan, 0x4aff5b9, 1)`), set formation `0x4ddc670`, dtor `0x49ee960` (loader failure path).
- Result: 10 styles (codes are fourccs matching the names, e.g. `GEGE`, `WING`), 90 installed templates (Gegenpress,
  Wing Play, Tiki-Taka, ... 7–9 formations each, names decoded as UTF-8), 55 formations.

## Phase 6.2 results: statistical comparison with harvestgreen22's Windows figures

Setup (reconstructed from the plan; the exact reference configuration is not published): app default fixture and
lineups; home all non-position attributes 12 (raw 60), away 13 with pace and acceleration 12; both feet 20
("two-footed"); everyone 180 cm / 70 kg; position familiarity left at fixture defaults. Tactics: installed presets
from the Mac preset export, applied with the app's own `apply_plan` (Wing Play 424-442 = template 43, Gegenpress
433-433 = template 16, Tiki-Taka 4231-442 = template 22); ZaZ Ace of Clubs imported from the user's `.fmf`. Every
batch went through the app's `/api/run` (3 workers); 0 failures in 3,200 matches. Scripts: `port/validation/`.

| Home (away: Gegenpress 433-433) | seeds | W-D-L | Mac win % | Windows win % | diff | z (two-sample) | Goals H-A | xG H-A | Poss. H |
|---|---|---|---|---|---|---|---|---|---|
| Wing Play 424-442 | 1-300 | 123-77-100 | 41.0 | 45.3 | -4.3 | -1.06 | 1.31-1.13 | 1.04-1.00 | 43.7% |
| Wing Play 424-442 | 1-1000 | 396-254-350 | 39.6 | 45.3 | -5.7 | -1.75 | 1.27-1.19 | 1.04-1.04 | 44.0% |
| ZaZ Ace of Clubs | 1-300 | 137-74-89 | 45.7 | 51.0 | -5.3 | -1.30 | 1.76-1.32 | 1.54-1.10 | 46.6% |
| ZaZ Ace of Clubs | 1-1000 | 471-244-285 | 47.1 | 51.0 | -3.9 | -1.19 | 1.84-1.38 | 1.53-1.12 | 46.4% |
| Tiki-Taka 4231-442 | 1-300 | 80-78-142 | 26.7 | 23.5 | +3.2 | +0.90 | 1.06-1.51 | 0.87-1.27 | 57.6% |
| Wing Play, both feet 12 (sensitivity) | 1-300 | 105-88-107 | 35.0 | 45.3 | -10.3 | — | 1.19-1.16 | 1.07-1.11 | 44.2% |

z treats the Windows figures as n=300 estimates (their own 95% half-width is ±5.6 points).

- At n=300 all three fall inside the plan's ±5.6 band (**PASS** by the plan's criterion).
- At n=1000 both re-runs fall outside the plan's band computed with the Mac sample size (±3.1), but that criterion
  treats the Windows figure as exact. Comparing the two samples, no difference is significant at 5% (|z| ≤ 1.75;
  combined χ² ≈ 5.3 on 3 df, p ≈ 0.15).
- The rankings agree (Ace of Clubs > Wing Play > Tiki-Taka against Gegenpress), and the differences between the
  presets are compressed on Mac (Mac 47/40/27 vs Windows 51/45/24).
- Setup sensitivity is as large as the gap: changing only the "two-footed" interpretation (feet 20 → 12) moves Wing
  Play from 41.0% to 35.0% on the same seeds. Without the reference's exact configuration the residual gap cannot
  be attributed to the port.

**Verdict: PASS by the plan's n=300 criterion; no statistically significant cross-platform difference; not
conclusive.** A definitive check needs plan step 6.3: the same exported scenario JSON (attributes, profile,
tactics) run on Windows and Mac with the same seeds, comparing full distributions.

## Further ports (all through `/api/*` on macOS, every batch passing upstream's post-processing)

| Feature | Windows source | Mac evidence | Result |
|---|---|---|---|
| FMF tactic export (`FM27_EXPORT_TAC`) | `0x49a9ab0` writer | `0x507c550`, 15/15 votes, decompiled pair (title `+0x790`) | `/api/export-fmf` native round trip verified |
| Taker lists, captain (kinds 30/31) | selection object `manager+0x6e8` | `+0x6e0`; identical internal layout in 2 decompiled caller pairs; getter/insert pairs identical | engine picks the chosen captain (60/60 checks); all 5 penalty goals by the first-listed taker |
| Set-piece routine edits (kinds 40-45, 47) | routine container `+0x8f0` | vectors `-0x10` (getter pair); object fields + vtable slots runtime-checked against the fixture for all 10 types; engine pool alloc/sized free | 12 routines incl. 2 new corner variants read back on both teams |
| Set-piece routine FMF import/export | routine `vtable[5]` | slot 6 | "Routine 1" parsed, every byte consumed; app import + export round trip verified |
| Set-piece selection log (`native_setpiece_selected`) | dead ball `+0x12d70`, table `0x4e38a90`, restart team `+0x12d50` | `+0x12d60` (pair), `0x59ba738` (equal on all admitted codes), `+0x12d40` (votes; runtime) | attack/defence types pair up and alternate between teams |
| Set-piece episodes (`/api/run-episodes`) | `native_setpiece_episode.h` | as above | 20/20 corner episodes found and settled |

Not ported (same behaviour as Windows or Windows-only): routine *collections* (`SET_PIECE_ROUTINE_COLLECTION_TYPE_HANDLER`,
rejected by the Windows host too), save-mode readers (`FM27_AI_TACTICS_SECTION`, `FM27_SOURCE_PLAN_DIRECTORY`,
`FM27_STAFF_FRAGMENT_DIRECTORY`, `FM27_SAVE_SECTION_PROBE`), the stats/events audit diagnostics.

## Tactical-effectiveness record (upstream `native_execution_experiment.h`) on macOS

**Mapping** (x86_64 slice; Windows → Mac):

| Item | Windows | Mac | Evidence |
|---|---|---|---|
| Record builder | `0xd85a0` | `0x4dd5f80` | matcher (callgraph, call sequence, constants, size); decompiled pair: 10 arguments ending in u16 CA, writes record `+0x1c..+0x20`; its only caller `0x4d07140` is the matched twin of `0xd7340` (the only Windows caller) |
| Record consumer (action sampling) | `0x41a50` | `0x4ad49c0` | 79/96 shared constants; the only common callee of the matched twins of both Windows callers (`0x32580↔0x4acfa60`, `0x49ee200↔0x5043060`); reads `player+0xcb2..+0xcd3` (Windows range −8). Matcher's first guess `0x4a88260` rejected: its callers are not the twins |
| Record | `MATCH_PLAYER+0xcba`, 33 bytes | `+0xcb2` | builder call `FUN_04dd5f80(player+0xcb2, …)`; consumer displacements |
| Fields | raw `+0xcd6`, role `+0xcd7`, overall `+0xcd8`, buy-in `+0xcd9`, next-match `+0xcda` | `+0xcce`, `+0xccf`, `+0xcd0`, `+0xcd1`, `+0xcd2` | record offsets `+0x1c..+0x20` identical |
| Engine version word | `match+0xa3a` | `match+0xa2c` | decompiled pair `0xe0b00/0x4a23470` (same version compares); votes 172/180 |

**Builder inputs** (both callers decompiled; Mac offsets): record `player+0xcb2`; the team's live plan `manager+0x1800`;
per-player history `player+0xa58`; exposure `player+0xb30`; attributes `player+0x470`; **opposition = the team's own
opposition-instruction block `manager+0x16e0`** (not the analyst object); a team block built from the plan's
in-possession cells (`manager+0x1920`); the player's in/out-of-possession cells `player+0xcd8`/`+0xdb0`; CA
`u16 player+0xc90`. The builder computes raw/role/overall; it *reads* buy-in (`+0x1f`) and next-match (`+0x20`), which
are set elsewhere (0 in the bundled fixture). History/exposure/record lie in the serialized match-player input, which is
where a save's real tactical understanding would arrive.

**Engine version word.** Normal tool runs (no experiment) log `0x1a080000` before and after preparation, and the record
stays **all zero for the whole match** (the builder never runs). With only the word switched to `0x1b000000` (no
policy), records are built once play starts (bundled fixture: raw 69–93, role 79–100, overall 17–21, buy-in 0,
next-match 0) and matches change: 100 paired seeds, 95/100 different scores; home W-D-L 57-22-21 → 42-39-19; xG
1.73-1.26 → 1.67-1.47 (total xG +0.15/match, t=1.0). **All tool results so far (Phase 6, the league) ran at
`0x1a080000`, i.e. without the tactical-effectiveness mechanism.**

**Experiment (kind 61) on macOS:** no code patching. The host sets the version word before preparation, then writes the
policy into all 33 bytes of every listed player of both teams after preparation and before every step call, counting
records the engine rebuilt in between (≈605 rebuilds per side per match, each overwritten before the next tick; upstream's
hooks also cover samples inside the tick of a rebuild). Gated on the x86_64 `LC_UUID` in host and server. Through
`/api/run`: probe `record_hex` = policy in all 33 bytes for every player at full time; app checks pass.

**Manager fractions** (`manager+0x34fc` 0.31/0.50, `+0x3504`): set to 0.95 on both teams → bit-identical match (score,
tick count, all records). Not buy-in; no effect observed.

**Match-manager person bytes `+0x61..+0x69`** (fixture home 10,19,17,12,14,14,18,17,44): each set to 1 and 20 on the home
manager, 3 seeds, both version words. Byte-identical matches for `0x61, 0x63, 0x67, 0x68, 0x69`; `0x62, 0x65, 0x66` change
the match occasionally; `0x64` always. `0x64` 1 vs 20 over 200 paired seeds: home xG diff −0.15 (t=−1.67), goal diff
+0.14 (t=0.85), possession/shots unchanged; buy-in stays 0 throughout. Read by the engine, no measurable effect on
results at this sample size; not labelled.

### Tactical-effectiveness dose-response (kind 61, data writes)

Gegenpress 433-433 mirror on identical levelled squads (`tactic_league.py` squads), seeds 1..100 for every pair,
`port/validation/execution_dose.py` + `execution_dose_analyse.py`. "off" is the normal 0x1a080000 run.

| pair (home x away) | W-D-L | xG | total xG |
|---|---|---|---|
| off | 29-54-17 | 0.64-0.46 | 1.10 |
| 0x0 | 20-65-15 | 0.64-0.49 | 1.13 |
| 20x20 … 100x100 | 18–26 / 60–65 | 0.47–0.53 / 0.36–0.38 | 0.85–0.90 |
| 0x50 / 25x50 / 50x50 / 75x50 / 100x50 | 22/21/20/21/25 wins | home 0.43/0.46/0.47/0.45/0.53, away 0.43/0.35/0.37/0.34/0.36 | 0.79–0.89 |

- Any non-zero record cuts total xG by ~22% against off (paired t −2.6 to −3.7) and shots by ~1.5 per side; the level
  itself (20..100) barely matters. A record of 0 behaves like off (all-zero records, as in normal runs).
- Relative advantage is weak: home 100 vs 0 (away 50) moves xG difference by +0.17 (paired t 2.3), slope +0.13 xGD per
  100 points (t 2.2); goals and wins do not move significantly at n=100.
- Caveats: all 33 bytes hold one value (the engine's own records have raw 69–93, role 79–100, overall 17–21, so
  no policy reproduces a natural record); a record the engine rebuilds mid-tick stands until the next step.

Repeat with stronger players and a complex tactic: every non-position attribute 18 (raw 90), "HIGHWAY STAR 27 BBM 4231
P90 FA" imported through the game's parser for both sides (`DOSE_ATTRIBUTE=18 DOSE_FMF=...`), same pairs and seeds.

| pair | W-D-L | goals | xG | goals/xG |
|---|---|---|---|---|
| off | 34-45-21 | 0.99-0.68 | 0.77-0.66 | 1.17 |
| 0x0 | 31-48-21 | 0.47-0.33 | 0.74-0.61 | 0.59 |
| 20x20 … 100x100 | 29–38 wins | 0.52–0.64 / 0.29–0.46 | 0.65–0.79 / 0.48–0.56 | 0.73–0.88 |
| 0x50 | 23-46-31 | 0.43-0.60 | 0.54-0.74 | 0.80 |
| 50x50 | 30-49-21 | 0.54-0.37 | 0.71-0.46 | 0.78 |
| 100x50 | 32-54-14 | 0.57-0.32 | 0.68-0.48 | 0.77 |

- Every experiment setting, including 0x0, roughly halves goals against off (−0.6 to −0.9 per match, t −3.5 to −5.6)
  while xG falls far less; the Gegenpress run shows the same pattern more weakly (goals/xG 0.73 → 0.49–0.71). Since
  0x0 matches off on xG but not on goals, this is the 0x1b000000 version word, not the record value.
- The relative effect is clear here but one-sided: home 0 against away 50 loses 0.44 xGD (t −4.9) and 0.34 GD (t −2.5)
  compared with 50x50; above 25 there is no further gain (75x50 and 100x50 within ±0.1). 100x50 vs 0x50: xGD +0.39
  (t 4.3), GD +0.42 (t 3.2).

### Which engine path a real match takes (version word +0xa2c)

- Static (x86_64 slice): the match constructor (0x49868a0, store at 0x4986a3b) initialises the word to 0x1b000000
  (27.0); a match-creation path in the game (0x2e091e0 → 0x4e9c230, Windows twin 0x4a218c0; also 0x4e9aeb0, twin
  0x309c420) raises it to 0x1c000000 when the major byte is ≤ 27. The bundled fixture is deserialised from upstream's
  captured input and carries 0x1a080000 (26.8). The engine compares the word against ~100 thresholds at ~400 sites,
  almost all 26.8 revisions (0x1a080002 … 0x1a080421) plus 0x1b050001 (6 sites), so 0x1a080000 sits below nearly
  every branch while 0x1b000000 and 0x1c000000 differ only at the 0x1b050001 sites and the major-byte checks.
  A live in-game match therefore most likely runs at 0x1b000000 or 0x1c000000, not at the tool's 0x1a080000.
- Fixture squads, 100 seeds each (host, research override): 0x1a080000 57-22-21, goals 2.00-1.30, xG 1.73-1.26;
  0x1b000000 42-39-19, 2.06-1.45, 1.67-1.47; 0x1c000000 41-22-37, 2.12-1.80, 1.81-1.54 (total goals +0.62, t 2.5 vs
  0x1a080000). Goals/xG stays 1.10–1.17.
- Levelled 18-rated Highway Star squads, the app's signed scenario replayed on the host (100/100 scores identical to
  the app): 0x1b000000 with the engine's own records gives goals 1.06 vs 1.67 off (t −3.6), goals/xG 0.71, close to
  the policy runs (0.59–0.79). The goal drop in the dose runs is therefore the 0x1b000000 path itself on these
  squads, not an artefact of the written record values.

### Default engine path: FM27 (0x1b000000)

38 functions construct a match; all go through the constructor (0x49868a0), which stores 0x1b000000. Only two
special paths (0x4e9c230, 0x4e9aeb0) raise it to 0x1c000000. The Mac tool now runs the FM27 path by default: the host
writes 0x1b000000 before preparation (`native_engine_path` receipt, checked by the server per run), the server uses the
`1b000000` player-instruction policies (21 role/duty entries differ from `1a080000`), jobs carry `engine_path`, and
resume refuses a different path. Checks: the app's levelled Highway Star run reproduces the host's 0x1b000000 replay
on all 6 seeds; defaults and all 90 installed presets validate; kind 61 still passes its receipt. Results above that
were labelled "off"/0x1a080000 (Phase 6, the league, the dose baselines) belong to the old fixture path.

### In-game replay: exact match with FM27's own results

FM27 autosaves every played match to `matches/automatic/<competition>/<home>_v_<away>_<seed>_VER_fm.pkm`; the number
is the match seed and every file carries version word 0x1b000000. The host loads such a file unchanged
(`FM27_ENGINE_PATH=fixture`, no `--seed`, no scenario) and plays it with its own seed. Compared with the game's
result screens for four of the user's matches (a Premier League career save, 2038):

| match | in-game | host replay |
|---|---|---|
| Team v Stoke | 0-0, xG 1.85-0.71, shots 18-5, on target 8-1, yellows 3-0 | identical |
| Team v Fleetwood (FA Cup) | 5-2, xG 3.83-1.06, shots 30-10, on target 14-4; goals 45+1', 48', 51', 65', 72', 86', 90+8'; yellows 1-4 | identical, same goal minutes and sides |
| Young Boys v Team (UEL) | 1-3, xG 0.89-3.01, shots 9-19, on target 6-13; goals 45+1', 52', 64', 80' | identical, same goal minutes and sides |
| Team v Man City | 0-1 | 0-1 |

Only possession differs (e.g. 55-45 in-game vs 50-50): the tool reports possession ticks, the game's screen uses its
own formula. The engine, input and seed handling therefore reproduce live FM27 matches exactly. Debug probe
`FM27_MAC_PKM_INCIDENTS` showed a loaded file carries no incidents: FM replays a saved match by re-simulating it.
All four were played on holiday (the assistant manager in charge); a match managed by the user (touchline
instructions, substitutions) has not been compared yet.

### Tactical effectiveness on the user's real saved matches (FM27 path)

10 saved matches of the team × seeds 1-30, the team's record fields held between steps (`exec_real.py`), opponent
natural. Natural records on these squads after preparation: raw 58-72, role 93-100, overall 50-68, buy-in 52-78,
next-match 50-66.

| Team record | W-D-L | ppg | Δ xGD (t) | Δ GD (t) | Δ ppg (t) |
|---|---|---|---|---|---|
| natural | 151-66-83 | 1.73 | | | |
| all 33 bytes = 30 | 153-60-87 | 1.73 | +0.04 (0.5) | +0.05 (0.4) | +0.00 (0.0) |
| all 33 bytes = 90 | 178-54-68 | 1.96 | +0.37 (4.2) | +0.41 (2.8) | +0.23 (2.3) |
| overall = 30 / 90 | | 1.86 / 1.80 | +0.05 / +0.03 | +0.13 / +0.13 | +0.13 / +0.07 |
| buy-in = 30 / 90 | | 1.71 / 1.84 | +0.03 / +0.08 | +0.03 / +0.09 | −0.02 / +0.11 |
| next-match = 30 / 90 | | 1.89 / 1.79 | +0.06 / −0.02 | +0.20 / +0.14 | +0.16 / +0.06 |

None of the three named fields matters on its own (all |t| < 1.7). Raising all 33 bytes to 90 is worth +0.37 xGD
and +0.23 points per match; lowering them to 30 changes nothing. The effect therefore sits in the raw/role fields or
the 28 unmapped bytes, and only above the natural level (the overnight run tests raw and role separately).

### Overnight sensitivity study (FM27 path)

`port/validation/overnight.py`: 30,400 matches. Full tables are in `port/mac_host/runs/overnight/report.md` (git-ignored).
Base: the fixture on the FM27 path, defaults 4-3-3 on both sides, every attribute 13, natural in every position,
180 cm / 70 kg. Changes go to the home side only and are compared with the base on the same seeds.

The base is a low-event match: 0.50–0.38 xG, 0.33–0.17 goals, 13-41-6. With 40–60 seeds, effects smaller than about
0.2 xGD cannot be detected. The study also makes about 400 comparisons, so roughly 20 will reach |t| ≥ 2 by chance;
single bold cells in the per-position tables should not be trusted on their own.

**Process caveat.** FM27 was open for the whole run, against the rule not to run engine tests while
the game is open. The rows the run shares with the earlier smoke run (same seeds) are identical, but the smoke run
probably had FM27 open too, so a check with the game closed is still due.

The study's findings:

- **Start state.**
  - Condition matters most. At 40% the home side goes 1-3-56 (xGD −4.3); at 80% it loses 0.48 xGD (t −5.7).
  - Sharpness 25 or 50 costs 0.7–0.85 xGD; sharpness 75 costs 0.22.
  - Morale (1–15 against 20), team cohesion (45–85 against 80) and club cohesion (0–75 against 100) show no
    detectable effect.
  - Fatigue is not usable. Values of 16000 and 32000 fail the read-back check: preparation rewrites the field
    (exit 109). Values of 48000 and 65535 read back but leave every match identical to the base.
- **Attributes, whole team.**
  - Physical attributes dominate. Jumping Reach has a 3→18 range of +1.03 xGD, Acceleration +0.75, Pace +0.49 and
    Balance +0.37. A low value hurts more than a high value helps.
  - Technical and mental attributes show no clear effect. Whole-team Passing 3 and 18 both give 0.892 pass
    completion, the same as the base. Finishing 3 and 18 give the same goals per xG.
  - Consistency, Leadership and Natural Fitness give exactly the base result: the match engine never reads them.
  - Either the FM27 path takes technical and mental ability from somewhere this harness does not write, or the
    attribute map is wrong for those indices. **This is the main open question**, and it needs checking before the
    per-position results are used.
- **Attributes by position (18 against 3).** Only the physical pattern survives (wingers: Acceleration +0.29 xGD,
  t 3.0, and Pace; centre-backs: Jumping Reach). The rest is at the noise level expected from the number of
  comparisons.
- **Tactical-effectiveness record.**
  - On the user's real matches, raw (+0x1c) and role (+0x1d) at 10, 50 or 90 give exactly the natural result: the
    match does not read them.
  - Overall, buy-in and next-match alone do nothing (all |t| < 1.7). By position group on the fixture they also do
    nothing.
  - So the earlier "all 33 bytes = 90" effect (+0.23 ppg) comes from the 28 unmapped bytes.
- **Tactics at low against high effectiveness.** Holding overall, buy-in and next-match at 20 or 80 changes nothing
  across 23 tactics: pooled Δ ppg +0.02 (t 0.55), n = 1380 pairs. Rank changes between the low and high columns are
  noise. The only robust result is that Park the Bus, Catenaccio and Route One are worse (−0.25 to −0.5 xGD) against
  Gegenpress on levelled squads.

### In-game check of inputs and statistics (Team v Stoke, seed 2987626)

- **Attributes.** The host's player dump (`FM27_MAC_PLAYER_DUMP`) of the saved match was checked against the game's
  profile screens for five players (three of the team's, two of Stoke's).
  All 184 values match. The game shows each stored value (1–100) divided by 5 and rounded to nearest; floor would
  give 54 mismatches. Footedness matches too. The catalog's attribute names, taken from an external layout, are
  therefore correct for every slot, and the small technical and mental effects in the overnight study are not a
  labelling error.
- **Team statistics.** Shots 18–5, shots on target 8–1, xG 1.85–0.71, yellow cards 3–0, passes completed 393/459
  and 360/443 all equal the host replay. The tool's "possession" (possession ticks, 52.6%) is the game's **Ball
  Share** (53/47), not its "Possession" figure (52/48).
- **Shown in-game but not yet in the tool's output:** corners, headers won, tackles won, fouls, clear-cut chances,
  crosses, offsides, final-third and progressive passes, distance covered, and per-player statistics.

### Passing and Finishing at higher power (200 seeds, FM27 closed)

Same fixture and base as the overnight study. Whole home team at 3, 13 (base) or 18. The 220 matches this run
shares with the overnight run are identical, so having FM27 open overnight did not change any result.

| attribute 18 − 3 (paired, n = 200) | Δ pass completion | Δ passes | Δ goals | Δ xG | Δ (goals − xG) | Δ points |
|---|---|---|---|---|---|---|
| Passing | +0.5 pp (t 3.4) | +11.6 (t 2.4) | +0.05 (t 0.9) | +0.02 (t 0.7) | +0.02 (t 0.5) | +0.16 (t 1.7) |
| Finishing | +0.2 pp (t 1.9) | +7.9 (t 1.8) | −0.06 (t −1.3) | −0.01 (t −0.4) | −0.04 (t −1.0) | −0.15 (t −2.1) |

- Passing is read, but its effect is small: 88.7% → 89.2% pass completion. No goal or xG effect is detectable.
- Finishing shows no effect on conversion over about 1,500 shots per arm. On these squads goals run at only about
  55% of xG at every Finishing level.
- Correlating every byte of the first 0x2000 bytes of the player object against each attribute (46 real players)
  finds no second copy of the attributes. A derived copy held elsewhere, or as 16-bit values, has not been ruled out.

### Attribute sensitivity on the user's real saved matches (27.0 engine)

`port/validation/attr_real.py` with the host's `FM27_MAC_ATTR` (written before preparation, read back after it):
10 saved matches of the team × seeds 1-30. The team's whole squad moved by −5 and +5 in-game (±25 stored, clamped to
1-20); opponent unchanged. 32,700 matches, run on the 27.0 backup engine. Effect per +5 = (plus − minus) / 2, paired
by match and seed, n = 300. Natural: 1.73 points, 2.00–1.34 goals, 2.13–1.44 xG. Full table in
`port/mac_host/runs/attr_real/report.md` (git-ignored).

| attribute (+5, whole squad) | Δ points (t) | main channel |
|---|---|---|
| Pace | +0.40 (8.7) | +0.51 goals, +0.32 xG for, −0.21 xG against |
| Acceleration | +0.33 (6.6) | +0.23 xG for, −0.27 xG against |
| Stamina | +0.22 (4.4) | +0.17 xG for, −0.13 xG against |
| Work Rate | +0.16 (3.2) | −0.17 goals against |
| Dribbling | +0.16 (3.3) | +0.19 xG for, +1 shot |
| Anticipation | +0.14 (3.0) | +0.16 xG for, −0.14 xG against |
| Jumping Reach | +0.14 (2.7) | +0.17 xG for, −0.18 xG against |
| Strength, Flair, Concentration, Composure | +0.08 to +0.11 (1.5-2.3) | Strength: conversion; Concentration and Composure: pass completion, xG |
| Finishing | +0.02 (0.4) | +0.21 goals (t 4.0), all conversion (goals − xG +0.18); xG against also rises (+0.08, t 3.0) |
| Passing, Technique, Vision, Decisions, First Touch, Marking, Tackling, Positioning, Heading, Crossing | −0.07 to +0.07 | none detectable |
| Natural Fitness | exactly 0 | not read during a match |

On real squads Finishing works as expected, unlike on the levelled fixture: the levelled squads were the problem. The
FM27 match engine is driven mostly by physical attributes (speed, stamina, jumping), then by work rate, anticipation
and dribbling. Most other technical and mental attributes move individual measures (pass completion, ball share)
without a detectable effect on points at ±5. With 54 attributes × 10 measures, isolated |t| 2-3 cells are expected by
chance. A +5 is partly lost to the cap for players already near 20. These are 27.0 results; 27.0.1 changed the engine
(version word 0x1b000100).

### In-game replay on 27.0.1 (engine word 0x1b000100)

Five matches saved by FM27 27.0.1, replayed by the 27.0.1 host on each file's own seed with the file's version word.
For the three with in-game screenshots, every statistic the tool reports equals the game: score, shots, shots on
target, xG, yellow cards, passes completed and attempted, and Ball Share.

| match | how it was played | game | host replay |
|---|---|---|---|
| Team v Hull | instant result | 1-0, shots 13-5, on target 8-2, xG 1.06-0.47, yellows 0-3, passes 461/534 and 461/531, share 51/49 | identical |
| Team v Newcastle (Carabao Cup) | watched, no changes | 4-3, 14-13, 10-7, xG 2.54-1.52, yellows 4-3, passes 352/427 and 575/633, share 43/57 | identical |
| Sunderland v Team | watched, many touchline changes by the user | 1-2, 10-16, 4-6, xG 1.22-1.58, yellows 5-0, passes 377/431 and 443/508, share 44/56 | identical |
| Brighton v Team, Team v Real San Sebastián | instant result | not compared | 3-0 and 3-1 |

So the saved match carries the manager's in-match decisions: a match the user managed by hand replays exactly too,
which settles the holiday-mode caveat above. On 27.0.1, holiday-mode matches are not saved; instant-result and watched
matches are. Incident type 2 is an own goal, credited to the other side (Sunderland 4'). The study runners' goal-minute
lists count only types 1 and 3, so they omit own goals; scores are unaffected.

### In-match decisions: live or replayed? (substitutions)

The host now logs every on-pitch change (`native_on_pitch_change`). Player byte +0x1e26 is 1 while the player is on the
pitch and +0x1e51 is his lineup slot (255 off). Both were found by searching snapshots of the Hull replay for exactly
11 players per side with a changing set. A substitution is an "off with slot 255" paired with an "on" at the same
clock; a brief off/on with an unchanged slot is treatment. `port/validation/subs_check.py` replays a saved match on
its own seed and on other seeds and compares the substitutions.

| base match | how it was played | user's side | AI side |
|---|---|---|---|
| Team v Stoke (27.0) | holiday (assistant) | **live**: different players and minutes per seed | live |
| Team v Hull (27.0.1) | instant result (assistant) | **live** (e.g. own seed 67'/73'/87', seed 1 70'/76'/90', other players) | live |
| Sunderland v Team (27.0.1) | watched, user made changes | **replayed**: the same 3 swaps (0→11, 3→13, 8→16) in nearly every seed, ±2 minutes; 1-2 dropped in 3 of 10 seeds | live |
| Team v Newcastle (27.0.1) | watched, no changes | **none**: no substitution in any seed | live |
| bundled fixture, no scenario | — | live, both sides | live |
| bundled fixture, app batches (before the in-match option) | — | **none** (see correction below) | **none** |

Consequences:
- The studies on the user's real matches (all holiday matches, replayed without a scenario) re-make in-match
  decisions live, as an in-game instant result would. There is no fixed-substitution bias in those.
- **Correction (2026-11-10):** the "live" row for the fixture was measured without a scenario. Every app batch sends
  the manual-input flag (kind 10), and that flag also stops all in-match decisions: 0.1–0.2 substitutions per match
  and no tactical change in any of 40 team-matches. Runs on the fixture with an encoded scenario before the in-match
  option below had no in-match management at all: the tactic league, the dose-response runs, and the overnight
  sensitivity study (829 of its 989 conditions use a scenario file). Their comparisons hold for "tactic as set, no
  substitutions"; they say nothing about matches the assistant or the AI manages. See "Manager input flags and
  in-match management".
- Pre-match decisions saved in the file stay fixed in what-if runs: the opponent's selection, tactic and opposition
  instructions.
- A manually managed match keeps the manager's recorded substitutions (players fixed, timing near the original); a
  watched match without input gives the user's side no substitutions at all. Neither should be used as the base for
  what-if studies; holiday or instant-result matches should.

### Manager input flags and in-match management (kind 62)

The manager input-flag word (Mac manager+0x30d0, Windows +0x30a0) in the user's saved matches:

| how the user's side was run | word | in a replay |
|---|---|---|
| managed (Sunderland) or watched (Newcastle) | 0x24001 (bit 0) | managed: the manager's recorded substitutions; watched: none |
| instant result or holiday (Hull, Stoke, …) | 0x25306 (bits 1, 2, 8, 9, 12; no bit 0) | assistant substitutes live, tactic kept |
| AI opponents | 0x24000 / 0x20000 | AI substitutes and adjusts the tactic |

Bit 0 means a human controls the team. The fixture path sets it (kind 10) so that preparation keeps the edited
tactic. Without it the fixture fails read-back (exit 109) because the AI re-plans during preparation. With it, the
team makes no in-match decision.

Writing the word after preparation and before kick-off (data write) hands the match over (bundled fixture, seeds
1-10, both sides):

| after preparation | cells changed at kick-off | later tactic changes | players off (home/away) |
|---|---|---|---|
| unchanged (bit 0) | 0 | 0 | 2 / 0 |
| 0x25306 (assistant) | 0 | 2 | 52 / 50 |
| 0x24000 (AI) | 180 / 164 | 120 | 50 / 50 |

With the assistant word the edited tactic is kept and substitutions are made as in an instant result. With the AI
word the AI rewrites roles and duties in about 15 of 22 cells at kick-off, the same on every seed, and keeps
adjusting. On saved matches the assistant word also replaces a manager's recorded substitutions (Sunderland: 5-7
live substitutions instead of the recorded 3), and gives a watched side substitutions (Newcastle: 5-6 instead of
none). The tactic is kept in both. Hull, whose user side already holds 0x25306, replays exactly with it.

Scenario kind 62 (side, value = 0x25306 or 0x24000) writes the word after preparation; the host logs
`native_in_match_management` and the batch checks it per team. In the app each team has "in-match management":
assistant (default for new scenarios on the fixture), fixed (the earlier behaviour; scenarios without the field), or
AI. Saved matches add "as saved" (default). The host also logs `native_tactic_change` (mentality and the 22 cells,
when they change) and `native_mentality_span`.

### Saved matches as the editor's base

Any match FM27 saved (instant result, watched, managed) can replace the bundled fixture as the base of the editor:

- The host's `--dump-input SNAPSHOT --inspect-fixture` reads a .pkm with the game's reader and writes the editor
  snapshot before preparation, in upstream's Windows format (header, team instructions and mentality, OOP map, both
  phases' cells, player instructions, opposition instructions, set-piece routines, throw-in styles). Mac offsets are
  mapped back to the Windows layout. Players are listed in input-roster order, with name and the 23 profile fields.
  Check: on the bundled fixture it reproduces upstream's `editor_*` snapshots exactly for every field the server
  reads.
- `src/desktop_saved_matches.py` lists `matches/automatic/*/*_VER_fm.pkm`, copies an opened match into the app's
  data folder (the game deletes old matches), and builds a `MatchBase`. The server's defaults, validation and
  encoding take the base from the scenario's `fixture` key.
- A saved base keeps every stored player value (no controlled start), keeps the file's engine version word, never
  sends the manual-input flag, and writes only edited fields. Setting the flag on an unedited saved match changes it
  completely (Hull: 1-0, 13 shots becomes 3-0, 29 shots). Edits without it pass the host's read-back after
  preparation and take effect (mentality 6 to 1, attributes).
- Check: the unedited Hull base on its own seed through `/api/run` gives 1-0, xG 1.064-0.473, shots 13-5, as in-game;
  Newcastle gives 4-3, as in-game. Every saved match opens, and the 27.0 matches are marked as not exactly replayable
  on 27.0.1.
- The app's "Saved matches" page lists the matches with who ran each side (from the flag word), opens one in the editor
  (seed set to the match's own seed), or replays it exactly in one click. A banner names the base, and advises
  assistant mode where the user managed or watched.

Results now also carry substitutions, players leaving without replacement, minutes played (from
`native_on_pitch_initial` and the on-pitch changes) and the match length, per run and per player across a batch.
They are kept in fast mode too.

### Player-instruction policy table for 27.0.1

`fm27_mac_host --policy-audit` calls the game's own role-mask and policy functions for every role, position and duty,
and three version words, as upstream's Windows audit does. On 27.0.1 it reproduces the catalog's 1a080000 and
1b000000 tables exactly for every in-phase option (1,547 entries). Upstream marks out-of-phase options unavailable;
the game reports some of them as editable. Role eligibility matches in all 192 contexts. The 0x1b000100 table equals
the 0x1b000000 table. `scripts/build_native_mac.py` now writes it to `private/engine/fm27_native/pi_policies_<word>.json`
(refused if the audit does not reproduce the catalog), and the server merges it.

### Tactical-effectiveness record on 27.0.1

`port/map/exec_locate.py` finds the builder and sampler through their callers. The builder's caller has 75 calls
instead of 141 (inlining), so the call is matched by its argument set-up. Builder 0x4e49240: same arguments (rdi =
player+0xcb2) and exactly the same stores through the record pointer. Sampler 0x4affce0 (callers 2/2): it now reads
the record through a new accessor 0x4e49020(record, category), with an offset table pointing at the same bytes 27.0
read inline. The layout is unchanged, so the experiment is enabled for 27.0.1 (gate: both LC_UUIDs).

Dose-response on 27.0.1 (same design and seeds as 27.0, n=100 per pair): any non-zero record lowers total xG (50x50 vs
off −0.21, t −2.9); home 0 vs 50 loses 0.13 xGD (t −1.9); 100 vs 50 changes nothing. Same pattern as 27.0.

The 28 unmapped bytes, from the accessor (`port/map/exec_record.py`; exact against the game's function on 20,000
random records, 0 mismatches; the 27.0 sampler has the same constants):

- value(category) = clamp(round(A) + round(B), 0, 100), with T = round(S) and
  S = 0.45·r[0x19] + 0.35·r[0x1a] + 0.2·r[0x1b] (mode 1) or 0.6·r[0x19] + 0.3·r[0x1a] + 0.1·r[0x1b] (other modes);
  A = p0·(100 − T) + p1·r[0x00] + g·k·t2; B = g·t1. The bytes are signed, and t1, t2 are bytes +1 and +2 of the
  category's triple.
- Triples: categories 0-8 use offsets 13, 16, 19, 1, 4, 7, 10, 22, 10 (6 and 8 share one). The first byte of each
  triple is not read by the accessor.
- Mode = byte +0x21, just past the record: mode 1: k = p0 = p1 = 1/3, g = 1; modes 2/3: k = 0.25, p0 = 0.5,
  p1 = 0.25, g = 0.7 (2) or 0.6 (3); otherwise k = 0.5, p0 = p1 = 0.25, g = 0.6.
- So bytes 0x19-0x1b form a team-level score that enters as (100 − S): the higher it is, the lower every category.
  Byte 0 is a player-level term, and each category adds its own two bytes. With all 33 bytes = v (the experiment;
  the mode byte keeps its natural value), category 0 gives:

  | v | 0 | 10 | 25 | 40 | 50 | 60 | 75 | 100 |
  |---|---|---|---|---|---|---|---|---|
  | mode 1 | 33 | 47 | 67 | 87 | 100 | 100 | 100 | 100 |
  | mode 2 | 50 | 56 | 66 | 75 | 81 | 88 | 97 | 100 |
  | mode 3 | 50 | 55 | 63 | 70 | 75 | 80 | 88 | 100 |
  | other | 25 | 34 | 48 | 61 | 70 | 79 | 93 | 100 |

  A record of 0 is therefore not "no effectiveness" (33-50), and in mode 1 the value saturates from v = 50. That fits
  the earlier dose-response: no gain above about 50.

### xG models (partial)

The xG model store holds three parallel tables keyed by engine version words: 0, 0x18050202 … 0x1a080422, and
0x1b000002, with 11 models per group. 27.0 had 12 groups; 27.0.1 adds 0x1b000002. Renaming or swapping a group key
in memory (all three tables, this process only) makes every lookup fail: xG becomes 0, and the whole match changes
(passes, shots, goals; 8 of 8 seeds). The lookup does not go through these keys alone: a swap with an existing group
also fails.

Static trace (27.0.1): the store is referenced by three functions. Two are load and clean-up; the third, 0x4f5cee0,
builds a shot-feature record (distances and angles from positions) and evaluates it through the store (0x4ffaca0). It
also sets a flag bit when xG < 0.15. Its callers are 0x49c8a00, the 40 KB function 0x4cde930 (two sites) and
0x4d16380. At three of the five call sites the caller reads the chance's xG (+0x2c of the result) and branches on
**xG ≥ 0.15** (constant 0x59375cc). So the engine computes xG for a chance during play and uses it in its decisions.
It is not only a reported statistic, which is why a failed lookup (xG 0 everywhere) changes shots and goals. Whether
the model also decides if a shot is scored is still open.
Host research switches: `FM27_MAC_XG_DUMP`, `FM27_MAC_XG_KEY` ("a=b" or "a<>b").

### Recorded manager decisions

Not decoded. Where the recorded substitutions of a managed match are stored is still unknown. In practice the
assistant word (kind 62) replaces them with live assistant decisions and keeps the tactic, so managed and watched
matches can now serve as what-if bases.

### English interface (2026-11-10)

The app's interface and server messages are now English. Upstream's UI and server text (about 1,260 Chinese text
runs in `src/`) were translated in place. Catalog labels (roles, attributes, instructions, mentalities, set-piece
options) are translated in memory when the server loads the private catalog (`src/catalog_en.py`): they are derived
from the English already in the data (role ids, attribute names, team-instruction source names, the set-piece
catalog's `english` field), or translated by hand where there is none. The private catalog itself is unchanged.
