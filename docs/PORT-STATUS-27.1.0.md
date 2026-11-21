# Porting FM Match Lab to FM27 27.1.0+2505117 — status

Repo: `/Users/kenneth/Documents/fm27-match-lab` (clone of caiograco289/Fm-Match-Lab).

## What was tried

1. Read the build gate: the host requires the **x86_64 LC_UUID** of `game_plugin` to be in
   `scripts/build_native_mac.py` `BUILDS`. Supported: 2493426, 2494769, 2503222.
2. This install: **27.1.0+2505117**, x86_64 UUID `864625AF-9AA9-3254-8EC5-47E9D486132A`.
3. Cheap experiment: copied `fm27_mac_x86_64_2503222.h` to `fm27_mac_x86_64_2505117.h`
   (same RVAs, new UUID/version), added a `BUILDS` entry, built the host.
4. Result: host **built and loaded the engine** (`macos_load_returned: success`,
   `native_engine_compatibility: compatible`), then **SIGSEGV at engine_rva 0x514c6b0**
   (`fn_interface_ctor`). The 27.0.1 address table does not map to 27.1.0.

## Why

`port/map/update_rvas.py` re-derives addresses by matching the **old x86_64 slice**'s
function bytes in the new slice. Steam keeps only the newest build, and no older
`game_plugin` exists on this Mac. Without the old slice the automated carry-over cannot run.

## Options

A. **Get the old build (preferred).**
   - Steam → FM27 → Properties → Betas: check for a previous-version branch.
   - Or depot download (app 4530370); needs a manifest id (SteamDB is blocked from here).
   - Then: `lipo -thin x86_64` old + new → `port/map/update_rvas.py` → `write_build_header.py`
     → add UUID → rebuild host → replay a saved match.

B. **Map from scratch (Ghidra).** The repo has `port/map/` scripts, targets and Ghidra scripts.
   The new binary's assertion strings (e.g. `..._i_plugin_match_playback_interface_get_ball_position()`)
   give anchors for the playback API, but all ~83 functions and 28 data addresses must be located.

C. **Wait for upstream.** The maintainer documents "expect a delay after patches"; a GitHub issue
   asking for 27.1.0 (2505117) mapping is the low-effort path.

## State left behind

- `port/mac_host/fm27_mac_x86_64_2505117.h` (guess header, same RVAs as 2503222).
- `port/mac_host/fm27_mac_x86_64.h` — added `#elif FM27_MAC_BUILD == 2505117`.
- `scripts/build_native_mac.py` — added BUILDS entry for UUID 864625AF.
- Built host at `private/engine/fm27_native/fm27_mac_host` (x86_64, Rosetta).
- Test command that crashed:
  `FM27_GAME_ROOT=".../game_plugin.bundle/Contents/Resources" private/engine/fm27_native/fm27_mac_host --fixture <pkm> --seed <n> --output /tmp/replay.jsonl`

## SUCCESS — 27.1.0 mapped and replaying

With the 27.0.1+2494769 install available as the reference slice, the carry-over worked:

1. `lipo -thin x86_64` both builds → `~/fm27-port-work/mac/2494769` and `.../2505117`.
2. Pointed `port/map/update_rvas.py` at the **2494769** header (the script defaults to the base 2493426 header,
   which made every old address "not a function start"). Added `#define FM27_RVA_*` parsing.
3. `update_rvas.py` matched **73/74** entries. Resolved by hand:
   - `fn_match_dtor`: relocated from the 2494769 address (0x49a1d20 → 0x49e6fb0).
   - `fn_platform_init`: kept the 64-byte signature match (0x48fa8a0; caller vote 0x48e6da0 rejected).
   - `fn_role_mask_ip`: signature + 1/2 caller vote → 0x4ff81d0.
4. `write_build_header.py` generated `port/mac_host/fm27_mac_x86_64_2505117.h`; it read the 27.1.0 engine word
   from the match constructor: **0x1b010000** (27.0.1 used 0x1b000100).
5. Added the UUID `864625AF-…` and build 2505117 to `scripts/build_native_mac.py`; rebuilt the host.

### Result

```
FM27_SKIP_VERIFY=1 FM27_GAME_ROOT=".../game_plugin.bundle/Contents/Resources" \
  private/engine/fm27_native/fm27_mac_host \
  --fixture ShaaX_Union_v_Chelsea_411091193_VER_fm.pkm --seed 411091193 --output /tmp/replay_test4.jsonl
natural_match_finished: full_match_completed=true, tick=23081, clock=22561, score=[2,4]
```

The saved match replays exactly (Shaanxi Union 2–4 Chelsea).

### Caveat

`verify_scenario()` (a readback check of scenario edits) crashes on 27.1.0 because the match-object layout offsets
(`mg_*`, `p_cell_*`, etc.) come from 27.0.x. The host is run with `FM27_SKIP_VERIFY=1`; replays and result
collection work, but **scenario edits should not be trusted until the layout is recalibrated**
(`port/map/layout_align.py` / `offset_vote.py`).

### Parallel workers

Four hosts launched simultaneously on the same fixture, seeds 11/22/33/44, all completed:

| seed | score |
|---|---|
| 11 | 0–2 |
| 22 | 2–3 |
| 33 | 1–7 |
| 44 | 0–3 |

Different seeds produce different results, as expected; no interference between processes. This is the
"multiple matches at a time" capability.

## 11. Layout calibration attempt (deferred)

Goal: make `verify_scenario()` work on 27.1.0 so scenario edits can be trusted.

What was found:
- With `FM27_SKIP_VERIFY` unset, the crash is in `instruction_entry()` (`fm27_mac_scenario.h:32`):
  `cell+8`/`cell+16` are not a valid vector, because the cell pointer from `tactic_cell()` is wrong.
- `carry_offsets.py` (added under `port/map/`) carried every layout constant by matching the same instruction in
  the matched function twins: `m_teams`, `m_score_context`, `p_attributes`, `p_native_id`, `p_identity`,
  `t_manager`, `t_roster`, `m_clock`, `m_tick`, cell geometry (`0x118`, `0x438`, `0x48`, `0x40`) are unchanged.
  `p_cell_oop` showed +0x8 (0xdb0 -> 0xdb8); `p_cell_ip` had no votes.
- The manager dump (`FM27_MAC_MGR_DUMP`, since removed) showed a 22-cell, 0x48-stride array at manager+0x1930,
  i.e. `mg_cells_live` would be 0x1818 (+0x10). With that value the crash disappears but the readback reports
  `player_tactic_binding_mismatch` (input_position reads a pointer fragment), so the **cell layout itself changed**:
  the position field is no longer at cell+0.
- Plan offsets used by `fn_tac_write`/`fn_tac_parse` (0x790/0x798/0x7a0/0x7a8/0x7bf) are identical in both builds.

Where to resume:
1. Find the tactic-cell initializer in 27.0.1 (writes position at cell+0, role at +0x40, instruction vector at +8/+16),
   match it in 27.1.0 (function map in `rva_update_clean2.json`), and diff its store offsets.
2. Re-derive `mg_cells_live`/`mg_plan` from that function's caller (the plan base may be a pointer now).
3. Update `tactic_cell`, `p_cell_ip/oop`, then run without `FM27_SKIP_VERIFY` until the readback passes and the
   stats match the known 2-4 replay.

Everything else (RVA mapping, engine word 0x1b010000, exact replay, parallel workers) is done and verified.

## 12. Layout calibration: resolved

The cell and plan layouts were recovered by running the **same fixture** through both builds and diffing the raw
manager/player objects (`FM27_MAC_RAW_LAYOUT`).

Findings, all confirmed against 22 players × 2 phases and the plan block:

| Field group | 27.0.x | 27.1.0 | Delta |
|---|---|---|---|
| `p_ca`, `p_exec_record`, `p_cell_ip`, `p_cell_oop` | 0xc90, 0xcb2, 0xcd8, 0xdb0 | 0x1228, 0x124a, 0x1270, 0x1348 | +0x598 |
| `p_slot`, `p_on_pitch`, `p_lineup_slot` | 0x1e27, 0x1e26, 0x1e51 | 0x23b7, 0x23b6, 0x23e1 | +0x590 |
| manager fields from 0x10a0 (`mg_oi`, cells, map, creator, `mg_version`, `mg_input_flags`, `mg_captain_slot`) | — | — | +0x8 |

The team block (`t_manager` 0x640, `t_roster` 0x140, `t_count` 0x73d) did not move, and the match object was
unchanged. The 8-byte difference between the two player deltas is an 8-byte field dropped in the zero gap after
the cell block; the manager gained 8 bytes at 0x10a0.

The header now derives all of these from `layout_player_shift`, `layout_slot_shift` and `layout_plan_shift`, which
are zero on 27.0.x builds, so one header serves every build. The plan base itself (`mg_plan`, the TAC parser and
writer's anchor) is `0x1800 + layout_plan_shift`; leaving it unshifted crashed the game's tactic parser and writer,
so `.fmf` import and export failed on 27.1.0 until it was fixed.

Validation on 27.1.0+2505117, none of it using `FM27_SKIP_VERIFY`:
- saved match replays exactly: Shaanxi Union 2-4 Chelsea, tick 23081;
- a 27.0.1-created fixture (Atlanta 1-2 Cincinnati) replays identically on both builds;
- scenario edits apply and read back: position (DM -> MC), role, duty, attribute, creator bit, opponent instruction;
- edits change matches (the same fixture with two edits went 0-1 -> 0-4), which is the check that the readback
  is verifying real state rather than a stale copy.
