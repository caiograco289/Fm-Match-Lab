# Ball position in FM27 27.1.0 (macOS x86_64) — what is known, and what is not

Status: **the live ball is not in the native match state we can reach.** Player coordinates are correct
and validated; the only ball-like field behaves like a coarse spot, not the simulated ball. This note
records the evidence and the dead ends so the search does not repeat them.

Everything below is read-only observation of the installed engine through the host.

## What works

| Item | Where | Notes |
|---|---|---|
| Player position | `player + 0x140` | `float x, y, z` in yards; **x across (±37.5), y along (±52.5)**, origin centre spot |
| On pitch | `player + 0x23b6` | `1` while playing |
| Slot | `player + 0x23e1` | `0..10`; roster index ≠ slot |
| Per-tick history | `player + 0x170` | pointer to an array, stride `0x20`, first tick `+0x200`, last `+0x208` |
| Current tick | shared context `+0x154dc` | |

Validation: 22 players per tick, median 0.36 yd of movement per engine tick (4 ticks = 1 match second),
sane bounds, coherent formations, and the goalkeeper's position fixes the attacking direction.

## The ball candidate, and why it is not the ball

`match + 0xaf0` holds `float x, y, z`; at rest `z = 0.111`, which is the ball radius, and at goals it sits
on the goal line. That is what made it look right at first. It fails every behavioural test:

| Test | Live ball | `match+0xaf0` |
|---|---|---|
| within 2 yd of a player | almost always | **11%** |
| within 5 yd | — | 32% |
| within 10 yd | — | 62% |
| more than 20 yd from everyone | rare | 14% |
| within 3 yd while "slow" | ~always (at the carrier's feet) | **18%** |
| moves every tick | ~always | static **67%** of ticks |
| update interval | 1 tick | median 1, mean **3.0**, p90 3 ticks |
| step when it does move | small | median 3.8 yd, p90 **23.1 yd** |
| time-lag alignment (players shifted −8..+8) | best at 0 | best at **+6 ticks, 27%** |

Eight coordinate transforms were tried (flip x/y/both, swap, and swaps with flips): as-is is the best at
19.5%, every other transform scores 2–6%, so it is not a frame/orientation error. It is also not a target
ahead of the carrier: the ball is ahead of the nearest player's movement 52% of the time — a coin flip.

## Searches performed (all negative)

1. **Pointer scan of the match object** (`match+0x0..0x1000`, 8-byte aligned): 54 pointers whose target
   looked positioned; all had zero floats at `+0x140`. Nothing ball-like.
2. **Entity scan of the shared match context** (`*(match+0x280)`, 0x18000 bytes, every pointer): 4,010
   candidates; none had a plausible `+0x170` history pointer or sane tick range, i.e. no entity objects
   other than those already known (players are reached through the teams, not this context).
3. **Full writable-memory scan** at tick 6000: every 4-byte-aligned float pair with `|x|≤40`, `|y|≤56`
   within 2 yd of an on-pitch player, excluding ±0x4000 around each player object → **3,764 candidates**.
   After three more ticks (still within 12 yd of a player, still in bounds): **3,755 survivors** — but only
   **578 distinct positions**, i.e. copies of the 22 players' own coordinates, and the `0xaf0` value itself
   appears at 24 addresses. The scan cannot separate the ball from position copies this way.

## Interpretation

FM's smooth ball in 2D/3D comes from the **presentation layer** — the managed `MatchSimulationData` mirror
that the in-game recorder reads at ~10 Hz (see `fm-cache/RE-match-memory.md`). Headless that layer is never
created (confirmed earlier: the playback interface is not constructed, and its vtable path returns zeros).
The native state only keeps the coarse value above. So this is not a missing offset; there may be no
per-tick native ball at all.

## Where to look next

1. **Per-tick history for the ball.** Players keep their own position history (`+0x170`, stride `0x20`,
   ticks at `+0x200/+0x208`, filled by the update at `0x4b106a0`). Find the entity the same update writes
   for the ball, or a 23rd entry in a shared frame array. That function is the anchor: `rdi` is the entity.
2. **`PLAYER_POSITIONS_PACKET`.** RTTI name at VA `0x5a7d898`, engine path
   `simatch/generic/engine/match_player_tactical_position.cpp`. Find its producer; the packet may carry the
   ball as an extra entry.
3. **Trajectory model.** If the ball is modelled as start/end/velocity (which would explain a 1.3 Hz field
   and 23 yd steps), find the ball struct with those fields and integrate it — that is what the presentation
   layer does. Search near `setup_basic_tactical_positions` (`0x4cd609b`) and for gravity/air-resistance
   constants.
4. **Managed mirror is not available headless**; do not spend time on it for this purpose.

## Reproducing the measurements

```sh
# one match with positions (one row per on-pitch player per tick)
FM27_POSITIONS_JSONL=/tmp/pos.jsonl \
FM27_GAME_ROOT="/Users/kenneth/FM27/Football Manager 27.app/Contents/PlugIns/game_plugin.bundle/Contents/Resources" \
  private/engine/fm27_native/fm27_mac_host \
  --fixture ~/fm27-port-work/saved_matches/Friendly/ShaaX_Union_v_Chelsea_411091193_VER_fm.pkm \
  --seed 411091193 --output /tmp/run.jsonl

# the diagnostics (proximity, static spells, lags, transforms, ahead-of-carrier)
.venv/bin/python scripts/ball_diagnostics.py /tmp/pos.jsonl
```

A one-minute window of the same fixture is enough; the conclusions hold on both seed-1 and seed-15 runs
(ShaaX and SH Port fixtures) that were tested.
