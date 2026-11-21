# Live positions in the FM27 27.1.0 native engine

Where the simulation keeps the 22 on-pitch players' x/y and the ball, how the slot
index maps to a player, and how to dump them every tick from a headless host.

Verified on **FM27 27.1.0+2505117, macOS x86_64 slice** (`game_plugin` x86_64, LC_UUID
`864625AF-…`), run through `port/mac_host`. Addresses are file offsets = VAs, as elsewhere in
`port/`. Read-only: no engine function is called and nothing in the match is written.

## Answer

| What | Where | Type |
|---|---|---|
| Player position, current tick | `player + 0x140` | `float x, float y, float z` |
| Ball position | `match + 0xaf0` | `float x, float y, float z` |
| On the pitch | `player + 0x1e26 + layout_slot_shift` = `0x23b6` | `uint8` (1 = on) |
| Slot (0–10) | `player + 0x1e51 + layout_slot_shift` = `0x23e1` | `uint8` (255 = off) |
| Team | `match + 0x15370 + 8*side` | pointer |
| Roster entry | `team + 0x140 + 8*i` | pointer |
| Roster count | `team + 0x73d` | `uint8` |

`x` is **across** the pitch and `y` is **along** it (see "Coordinates" below — this is the
opposite of the intuitive order). Units are yards. Origin is the centre spot.

The roster object *is* the match player. `+0x1270`/`+0x1348` remain the tactical cells and
`+0x1e10` remains the presentation record, which stays empty in headless mode — the position
exported here is the simulation's own value, not a view mirror.

## Coordinates

Measured over two full matches:

* player `x` (across): about −39…+39, typical touchline ≈ ±37.5
* player `y` (along): about −56…+56, typical goal line ≈ ±52.5…±55
* ball `z` at rest: `0.111` — the ball radius, which is what puts the unit at yards
* `x`/`y` 1st/99th percentile of the ball: ±40 / ±57 in play; the ball does go further
  (restarts, into the stands) so do not clamp it when analysing

**The ends swap at half-time.** In seed 1 the away side scored four times before the break with
the ball at `y ≈ +52…+54`, and after the break its goals were at `y ≈ −53`; the home side's
goals mirror that. Any per-team pitch control or attacking-direction analysis must therefore
flip the longitudinal sign at half-time (or read the team's current attacking direction)
instead of assuming a fixed end.

Kickoffs and restarts reposition all 22 players at once. Those jumps are real, not corruption:
22 players moving >1.5 yd in one tick happens only at those resets.

## Slot mapping

Filter `player[0x23b6] == 1` and take `player[0x23e1] < 11`. That gives exactly 0–10 once per
side in 23,213 of 23,377 seed-1 ticks. Roster index is **not** the slot — e.g. a roster entry at
index 2 can hold slot 3 — so always read `+0x23e1`.

A handful of ticks produce 21 rows (seed 1: 164 ticks, mostly a single 162-tick run just after
the interval; seed 2: 2). One side then has a slot missing because that player is genuinely off
the pitch (substitution/injury window) and `+0x23b6` is not 1. Emit the rows that exist rather
than guessing a position for the absent player.

## Evidence

**The writer.** `0x4b106a0` updates a player's position each tick:

```
4b106b7  mov  rax, [rdi+0x280]        ; the match
4b106be  mov  r12d, [rax+0x154dc]     ; current tick
4b10718  movsxd rax, r13d             ; index = clamp(tick, base, last) - base
4b1071b  shl  rax, 5                  ; stride 0x20
4b1071f  add  rax, r12                ; r12 = [rdi+0x170] = frame array
4b10722  movsd xmm0, [rax]            ; two floats
4b10726  movss xmm1, [rax+8]          ; third float (height)
4b1072b  movsd [rdi+0x140], xmm0
4b10733  movss [rdi+0x148], xmm1
```

So `+0x140` is the frame for the current tick, copied out of a per-tick history array. Consumers
treat it as an entity position: `0x4c0f6d5` measures a distance with
`movsd xmm1, [rax+0x140]`, and `0x4c0edd7` does the same through `[r14+0x10]`.

**Goal test (the decisive check).** Every score change in seed 1 (9 goals) and 3 of 4 in seed 2
lands with the ball at a goal line and the correct sign:

```
seed 1  748 [0,1] ball ( -3.3,  50.7)     10273 [1,4] ball ( -3.1, -54.3)
        1454 [0,2] ball ( -0.6,  52.4)     14952 [1,5] ball ( -0.9, -47.3)
        5508 [0,3] ball ( -6.5,  47.0)     18526 [2,5] ball (  2.7,  54.0)
        6884 [0,4] ball ( -3.5,  54.1)     21060 [2,6] ball ( -3.3, -53.1)
                                           21980 [3,6] ball ( -1.7,  54.2)
```

The 4th seed-2 goal is scored at tick 305 while the ball crossed at tick 301 (`y = −55.0`); the
host logs the score at the top of the next loop iteration, so the samples straddle it.

**Adjacent ticks.** 3000 → 3001 for seed 1, 22 players, all finite and in bounds: median
movement 0.35 yd per tick, p99 1.9 yd, max 1.15 yd for the exported field — about 4.6 yd/s at
four ticks per second, i.e. a sprint. Formation at kickoff is a 4-4-2: goalkeeper deepest
(`y ≈ +43`), back four around `+16…+20`, midfield four `+8…+11`, two forwards `+2…+3`, mirrored
for the other side.

**Determinism.** Two runs of the same seed produce byte-identical JSONL, and a run with the
variable unset produces an engine log identical to one with it set apart from the measured
timings.

## The playback interface lead

The vtable-slot suggestion does not apply to headless capture. `0x21280` is a *wrapper* that
calls slot `0xb0`; the slot does not point back at the wrapper.

* The interface's RTTI (`N15simatchplayback2si5match33I_PLUGIN_MATCH_PLAYBACK_INTERFACEE`,
  `0x599bb53`) has no vtable of its own; the shim that implements it
  (`PLUGIN_MATCH_PLAYBACK_INTERFACE_SHIM`, vtable `0x5b6e920`) forwards slot `0xb0` to
  `0x787110` via the object at `shim+0x10`.
* `0x787110` and its sibling `0x787200` interpolate between two time slices
  (`movsd xmm0,[rax+0x50]`, `subps`, `mulps`, `addps` — a lerp, plus a clamped blend factor).
  That is the presentation path, one layer above the engine's discrete per-tick values.
* The playback object is created by the playback layer, which the headless host does not run, so
  `0x21280` would take its `rdi == null` branch and return zeros.

For a host stepping `MATCH::play` directly, `player+0x140` and `match+0xaf0` are the engine's own
values for the tick just simulated, with no interpolation and no presentation dependency.

## Probe and reproduction

`port/mac_host/fm27_mac_positions.h`, called once per iteration after `episode_step()`:

```sh
FM27_GAME_ROOT="<app>/Contents/PlugIns/game_plugin.bundle/Contents/Resources" \
FM27_POSITIONS_JSONL="$PWD/runs/positions.jsonl" \
private/engine/fm27_native/fm27_mac_host --fixture <pkm> --seed 1 --output run.jsonl
```

One JSON object per player per tick, in roster order:

```json
{"tick":3000,"side":0,"slot":0,"x":-0.46,"y":47.5,"ball_x":20.84,"ball_y":3.68}
```

With `FM27_POSITIONS_JSONL` unset it is one `getenv()` per tick and nothing else; the match
result, tick count and score are unchanged. Writing it costs about 25 % of the 3.5 s simulation
(4.4 s total for a full match, 514 k rows). The file is flushed once per tick, so the tail
survives `finish()`'s `_exit()` and a crash, and it switches to guarded direct reads because
`safe_copy()` is a `mach_vm_read_overwrite` syscall and ~200 per tick dominated the cost.

### Per-tick history (for `--tick-step > 1`)

The array the writer copies from is reachable per player, and lets a host that steps several
ticks at once recover every intermediate frame:

| Field | Meaning |
|---|---|
| `player + 0x170` | pointer to frame array |
| `player + 0x200` | tick of frame 0 |
| `player + 0x208` | last valid frame tick, or −1 for "unbounded" |
| frame | `+0x00 float x, +0x04 float y, +0x08 float z`, stride `0x20` |
| index | `clamp(tick, base, last) - base` |

Reading it in the probe showed `base`/`last` bracketing the current tick (e.g. base 2999,
last 3000 and base 2998, last 3003 for two players at tick 3000). This is disassembly-derived
and only partially exercised; the per-tick `+0x140` read above is what is fully validated.

## Caveats

* Pitch dimensions are stadium-dependent; normalise by the fixture's real pitch if an analysis
  needs metric coordinates rather than engine yards.
* Do not use `player+0x1e10` in headless mode: the presentation record is not filled (zeros and
  NaNs), which is consistent with the earlier finding that it must not be mistaken for missing
  positions.
* `+0x140` is the position *for the tick just simulated*. With `--tick-step N` the probe samples
  every N-th tick (seed 1 with `--tick-step 4`: 128,549 rows, same 23,376 ticks and 3–6 score);
  use the history array to fill the gaps.
* The ball is legitimately outside the pitch during restarts and after shots into the stands;
  report it unfiltered.
