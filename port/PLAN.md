> **Historical.** This is the brief the port started from (Windows reference: upstream v1108.5). File paths under
> `native/` and `scripts/` refer to upstream's repository, not this one. Current documentation: `docs/MACOS.md`.

# Mac port of FM Tactics Lab (lqf0624/fm-tactics-lab): agent brief

Put this file in the root of your fork of `lqf0624/fm-tactics-lab` and tell your agent:
"Read MAC_PORT_PLAN.md and start Phase 0. Stop at every STOP point."

---

## 0. Goal and ground rules

**Goal:** run FM Tactics Lab's batch match simulations on macOS, using the Mac build of FM27 that the
user owns, and get results that agree statistically with the Windows tool.

**Ground rules (do not break these):**
- The user owns FM27 on Steam. Steam must be running and logged in, just as the Windows tool requires.
  Never bypass, stub out or emulate Steam ownership checks, DRM or online services.
- Never modify the FM27 install (no patched binaries, no replaced files). Load the game's code as it is.
- Never disable SIP or ask the user to. If a route needs it, abandon that route.
- Never commit or publish SI/SEGA binaries, extracted function bytes or game data. Follow upstream's
  approach: the repo holds addresses, digests and metadata only; anything derived from game files
  goes in git-ignored `private/` or `build/` folders (see `scripts/export_source.py`).
- Keep upstream's MIT licence and credit lqf0624. This is personal-use interoperability work.
- **STOP points:** pause and ask the user before (a) installing anything over 1 GB, (b) downloading the
  Windows depot, (c) any step that writes outside the repo, `$FM27_WORK_DIR/` or
  `~/Library/Application Support/FMTacticsLabMac/`, (d) concluding a phase failed.

---

## 1. What the Windows tool actually does (verified from source, v1108.5)

- **UI:** a local web app (`src/tactics_ui/*.html|js|css`) served by Python (`src/desktop_server.py`,
  `src/fm27_tactics_server.py`). Mostly portable already.
- **Launcher:** `Launcher.cs` (.NET Framework) only wraps the app in a window. Replace it on Mac.
- **Native host:** `native/desktop_host.cpp` (~1,050 lines) plus headers. It:
  - maps FM27's `fm_Data\Plugins\x86_64\game_plugin.dll` into its own process. `native_base` is the
    module base, and `at(rva)` turns an RVA into a pointer;
  - calls **about 95 internal, unexported engine functions by hard-coded RVA**, via C function-pointer
    casts. For example, the detailed match step is `0x4520bd0` (see `docs/SIMULATION_FIDELITY.md`);
  - reads and writes engine objects at **hard-coded struct offsets**, for example `match+0x15380` (the
    team pointers), `team+0x630` (manager), `manager+0x8f0`, `manager+0x1748` and tactic cells at `+0x40`;
  - checks compatibility (`native/fm27_engine_compat.h`) against `native/profile_metadata.json`:
    PE layout, 13 sections, TLS callbacks, 809 import bindings, 95 byte ranges and 14 data addresses.
    The reference build is `27.0.0+2493426`, with the DLL SHA-256 in `native/adapter_version.json`;
  - handles the Steam session (`native/native_steam_lifecycle.h`), runs workers with
    `CreateProcessW(... CREATE_SUSPENDED)`, uses named events for cancelling, SEH `__try/__except`,
    and `bcrypt` for hashing.
- `scripts/build_native.py` rebuilds the "comparison bytes" from the user's local DLL. **That step needs
  the Windows `game_plugin.dll`.**
- `scripts/prepare_private.py` pulls the initial input assets out of the release EXE without running
  it. It should work on macOS with Python 3.12; check this.
- Fidelity caveat (from upstream): the tool runs the detailed match loop, but upstream has **not**
  shown that in-game manual, holiday or instant-result paths give the same results. Upstream also
  found a separate simplified match model in the code. Don't claim more than upstream does.

## 2. What is known about FM27 on macOS (measured by other projects)

From `mavarobli/FMSuperScout` (`docs/macos.md`) and `tozmoz/FMLibreEditor`
(`profiles/fm27/*macos*`, `docs/recon/`, `crates/fmlibre-bridge`):
- App: `~/Library/Application Support/Steam/steamapps/common/Football Manager 27/fm.app`, with the
  executable `Contents/MacOS/Football Manager 27`. It's a **universal binary (x86_64 + arm64)**.
- The engine counterpart of `game_plugin.dll` is **`Contents/PlugIns/game_plugin.bundle`**, also
  universal. Unity sits in `Contents/Frameworks/UnityPlayer.dylib` and `GameAssembly.dylib`.
- Steam app id: **4530370**.
- FM27 is Developer-ID signed with hardened runtime, but it has
  `com.apple.security.cs.allow-dyld-environment-variables` and `...disable-library-validation`. So
  `DYLD_INSERT_LIBRARIES` works with SIP on, as long as FM is started directly. It has **no**
  `get-task-allow`, so outside processes can't read its memory without help.
- macOS strips `DYLD_*` variables when they go through SIP-protected binaries (`env`, `nohup`). Launch
  straight from bash, or `exec` from your own binary. FMSuperScout says Steam's launch options don't
  pass the variable on, while FMLibreEditor uses a Steam launch option. Test both.
- Steam must be open and logged in, or FM quits straight away. Set `SteamAppId=4530370` and
  `SteamGameId=4530370`.
- **The Mac build keeps RTTI with readable class names** (Itanium ABI), for example `db::ACTUAL_PLAYER`
  and `db::TEAM`. This is the biggest help for mapping functions.
- Struct layouts: plain records (contracts, clubs, teams, nations) are laid out **as on Windows**.
  Classes with virtual or multiple bases (players, staff) shift between MSVC and Itanium: the player
  block is −8 (no vbptr) and person/identity blocks move. Expect the same with match, team and manager
  objects that use multiple inheritance, and with members of MSVC STL types (see section 5).
- Build mapping: FM 27.0.0+2493426 corresponds to Steam build 26340721. FMLibreEditor has separate
  `-macos-arm64` and `-macos-x86_64` profiles, so RVAs differ per slice. Identify a slice by its
  `LC_UUID`.

## 3. Strategy

Use **FM27 Windows and FM27 Mac of the exact same build** as the Rosetta stone. It's the same source
code compiled twice (MSVC and clang), so every Windows RVA in the host has a Mac twin. **Do not use
FM24.** FM26/27 moved to a Unity front end with a separate `game_plugin`, so FM24's addresses and
layouts say nothing about FM27. At most it's practice material.

Preferred route **A, standalone host (same as Windows):** our own process `dlopen()`s
`game_plugin.bundle`, then calls the mapped functions. No injection, and the game isn't running.

Fallback route **B, in-process:** a loader injected with `DYLD_INSERT_LIBRARIES` into a normally
started FM27 (the FMSuperScout/FMLibreEditor technique) runs matches inside the game process. It's
heavier and riskier; use it only if A is impossible.

Start with the **x86_64 slice under Rosetta**. Its instruction set matches the Windows DLL, which makes
side-by-side comparison much easier. Port to the native arm64 slice once x86_64 works.

---

## 4. Phases (each one ends with a written report in `port/REPORT.md` plus exit criteria)

### Phase 0: Inventory and tooling (≈1–2 h)
1. Check: macOS version, CPU (`uname -m`), Rosetta (`/usr/bin/pgrep oahd`), Xcode command-line tools,
   Python 3.12, Homebrew.
2. Find the Mac game: path, `lipo -info` on the executable and `game_plugin.bundle`, `otool -l`
   `LC_UUID` per slice, `codesign -d --entitlements :- fm.app`, and the FM version string.
3. Install Ghidra (latest 11.x) and a JDK 21. Optionally install GhidraMCP so the agent can query
   Ghidra directly. **STOP (a).**
4. **STOP (b):** get the **Windows** `game_plugin.dll` for the same build with the user's own Steam
   login. Use DepotDownloader (open source) or SteamCMD with
   `+@sSteamCmdForcePlatformType windows`, app `4530370`, and download only
   `fm_Data/Plugins/x86_64/game_plugin.dll` (plus `steam_api64.dll` for reference) into
   `$FM27_WORK_DIR/win/`. Confirm its SHA-256 equals `reference_dll_sha256` in
   `native/adapter_version.json`. If it doesn't, the Mac and Windows builds differ, so stop and report.
5. Exit: a table of paths, versions, UUIDs and hashes in `port/REPORT.md`.

### Phase 1: Feasibility spike, go/no-go (≈half a day)
1. Write `port/spike/load.c`: `dlopen()` the `game_plugin.bundle` binary (path inside
   `Contents/MacOS/`) with `RTLD_NOW|RTLD_LOCAL`. Log `dlerror()`, the module base (`dladdr`) and the
   image index (`_dyld_get_image_header`).
2. Build it twice: `-arch x86_64` (runs under Rosetta) and `-arch arm64`. Run it with Steam open and
   `SteamAppId` set. Record crashes, missing dependencies (`otool -L`) and what static initialisers
   need. Use a scratch working directory and copies of the needed Frameworks via `DYLD_LIBRARY_PATH`
   if required. **Never change the app bundle.**
3. If `dlopen` succeeds, find the function matching Windows' engine init or match-step entry
   (Phase 2 method) and call one harmless function, such as a pure getter.
4. Exit: GO for route A if the bundle loads and one mapped function returns sane data. Otherwise
   write up why and try route B: a tiny `DYLD_INSERT_LIBRARIES` loader that only logs the
   `game_plugin` base inside FM. **STOP (d)** before giving up on both.

### Phase 2: Address mapping (the bulk of the work; days)
1. Make the **target list**: every `at(0x…)` in `native/*.h` and `native/desktop_host.cpp`, all
   `data_addresses` and `ranges` in `native/profile_metadata.json`, and every vtable RVA the host
   reads. Save it as `port/map/targets.json` with each target's call site and the signature implied
   by its cast.
2. Load the Windows DLL and the Mac x86_64 slice into Ghidra as separate programs. Run full analysis;
   these are huge, so allow hours and lots of RAM.
3. Match each target. Use at least **two independent kinds of evidence** per match:
   - RTTI and vtables: Mac Itanium type names, Windows MSVC RTTI (Complete Object Locators) if present,
     and the same slot index in vtables of the same class;
   - unique strings, asserts, log messages and file names referenced by the function;
   - unique constants (the host uses tags like `0x4e554c4c` "NULL", `0x54464c4f`, `0x54465348`,
     masks like `0xfffffffbf91fffff`, and struct sizes like `0x155b0`, `0x738` and `0x1e60`);
   - call-graph neighbourhood: callers and callees already matched;
   - Ghidra BSim or Version Tracking similarity, which copes with MSVC vs clang code.
4. Save `port/map/rva_map.json`: `{win_rva, mac_x86_64_rva, mac_arm64_rva, name_guess, evidence[],
   confidence}`. Anything with only one kind of evidence is "unverified" and gets flagged at runtime.
5. Exit: every target mapped with ≥2 kinds of evidence, or listed as blocked with what's missing.

### Phase 3: Struct offsets and ABI audit
1. For each offset the host uses (`grep -n "+0x"`), find the accessor in both binaries and confirm the
   Mac offset. Expect shifts wherever a class has virtual or multiple bases or contains MSVC STL members.
2. ABI differences to check for **every** function-pointer cast:
   - Windows x64 vs System V (x86_64) or AAPCS64 (arm64). Plain scalar or pointer signatures port
     automatically when clang compiles the cast, but **struct returns don't**: MSVC passes the hidden
     return pointer *after* `this` for member functions, and Itanium passes it *before*. Small-struct
     return rules differ too;
   - `long` is 32-bit on Windows and 64-bit on macOS. `wchar_t` is 16-bit on Windows and 32-bit on
     macOS, so check any engine string the host builds or reads;
   - `bool` and enum sizes, `#pragma pack`, and alignment of the structs the host fills in;
   - STL types inside engine objects: MSVC `std::string` is 32 bytes and libc++'s is 24; `std::map`,
     `std::unordered_map` and `std::function` differ. `std::vector` is three pointers on both, but
     check the order.
3. Exit: `port/map/offsets.json` plus an ABI note per function in `rva_map.json`.

### Phase 4: Port the host
1. Add a thin platform layer (`native/platform_win.h` and `native/platform_mac.h`) covering: module
   loading (`LoadLibrary`/manual map vs `dlopen`), process launch (`CreateProcessW` vs `posix_spawn`),
   cancelling (named event vs a pipe or signal file), crash containment (SEH vs a `sigaction` handler
   that logs and exits), hashing (`bcrypt` vs CommonCrypto), and the Steam session
   (`steam_api64.dll` vs `libsteam_api.dylib`, with the same orderly `SteamAPI_Shutdown`).
2. Replace raw RVAs with a generated table per platform and slice (`rva_map.json` → header).
   Keep Windows behaviour byte-for-byte unchanged.
3. Port `fm27_engine_compat.h` to Mach-O: check `LC_UUID`, segments and a digest of the mapped
   functions, the Mac equivalent of the PE checks. Refuse to run on an unknown build, as Windows does.
4. Build with `clang++ -std=c++17` for `x86_64` first, then `arm64`, using a new `scripts/build_native_mac.py`.
5. Exit: the host runs **one full match** with the built-in sample squads and fixed seed, ends
   naturally, and its score and team stats pass upstream's own consistency checks.

### Phase 5: Python server and app wrapper
1. `grep -rn -E "winreg|windll|creationflags|CREATE_NO_WINDOW|\\\\|\.exe|APPDATA|LOCALAPPDATA" src scripts`
   and make each hit portable. Use `~/Library/Application Support/FMTacticsLabMac/` for state.
2. Find the game root (Steam libraries in `libraryfolders.vdf`, as FMSuperScout's `app/server.js` does).
3. Replace `Launcher.cs` with `scripts/run.py` plus the browser, or a minimal Swift WKWebView wrapper
   (see FMSuperScout `mac/app/main.swift`). Sign it ad hoc; no Developer ID needed for personal use.

### Phase 6: Validation (don't skip this)
1. Determinism: the same seed and inputs on the Mac twice give identical results.
2. Cross-platform: don't expect bit-identical matches between Windows and Mac. Compilers and CPUs
   differ in floating-point code (for example, arm64 fused multiply-add). Validate **statistically**:
   - Repeat harvestgreen22's setup: home team all 12s, away team all 13s with pace and acceleration
     at 12, everyone 180 cm / 70 kg and two-footed. Run preset Wing Play 424-442 (home) against preset
     Gegenpress 433-433 (away), seeds 1–300. Windows reference: **45.3% wins**. Also run ZaZ Ace of
     Clubs (51.0%) and one weak preset, such as Tiki-taka 4231-442 (about 23–24%).
   - Pass if each Mac win rate falls inside the 95% interval of the Windows figure (about ±5.6 points
     at n=300). Run 1,000+ seeds if it's borderline.
   - Also compare goals per match, xG and possession averages.
3. If the user can reach a Windows PC, run identical configs on both and compare full distributions.
4. Exit: a validation table in `port/REPORT.md` and a clear PASS/FAIL.

### Phase 7: Packaging and upstreaming
- Keep this work on a fork branch. Open a PR or issue upstream offering the platform layer and the
  Mac RVA tables (metadata only, no game bytes), and credit FMSuperScout and FMLibreEditor for the Mac
  research you relied on.
- After each FM27 patch, re-run Phase 2 with the matches you already have as anchors. Most RVAs shift
  by section deltas, so try that first.

---

## 5. Reference projects (clone into `$FM27_WORK_DIR/refs/`, read only)

| Project | Why it helps |
|---|---|
| `mavarobli/FMSuperScout`: `docs/macos.md`, `mac/loader/fmss_loader.c`, `core/MemScan.Mac.cs`, `tools/mac-probe/` | Mac app layout, entitlements, the DYLD loader pattern, Itanium RTTI class detection, and the Win↔Mac field-shift tables |
| `tozmoz/FMLibreEditor`: `profiles/fm27/*macos*`, `layout-macos.toml`, `docs/recon/`, `crates/fmlibre-bridge`, `crates/fmlibre-mem/src/macos/` | Per-slice (arm64/x86_64) RVA profiles for the same builds, measured Mac layouts, and how to hand over a task port through a Steam launch option |
| `barak14/fm-editor`: `docs/fm27/memory-layout.md` and its read-only `fm-debug` MCP server | Windows FM27 layout notes and a memory-probing MCP your agent can use on Windows/Linux |
| Ghidra (+ BSim, Version Tracking) and GhidraMCP | Cross-compiler function matching that the agent can drive |
| DepotDownloader / SteamCMD | Getting the Windows DLL of the same build with the user's own Steam login |

## 6. Realistic expectations

- Phases 0–1 tell you within a day whether route A is possible.
- Phases 2–4 are the real work: probably **1–3 weeks** of agent time with the user checking in, mostly
  spent proving about 95 function matches and a few dozen struct offsets.
- Every FM27 patch can break the mapping, as it does on Windows. Budget a re-map after each one.
