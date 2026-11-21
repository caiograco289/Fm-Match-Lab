// Optional read-only dump of the engine's own per-tick coordinates.
//
// Written once per simulation tick to FM27_POSITIONS_JSONL when that variable is
// set; with it unset this is a single getenv() per tick and nothing else. No
// engine function is called and nothing in the match is written.
//
// Layout (verified on 27.1.0+2505117 x86_64, see docs/POSITIONS-27.1.0.md):
//   player+0x140      {float x, float y, float z}  current position, yards
//   match +0xaf0      {float x, float y, float z}  ball position, yards
//   x = across the pitch, y = along it, origin at the centre spot.
#include <cmath>
#include <cstdio>
#include <string>

// The match, its teams and the roster entries are the same objects the host
// reads directly elsewhere; the pointer chase is still validated because a null
// or stale entry would be a fault. Field reads then use plain loads: safe_copy()
// is a mach_vm_read_overwrite syscall (~200 per tick) and dominated the runtime.
static bool readable_ptr(const void* p, size_t n) {
    auto a = (uintptr_t)p;
    return a > 0x100000000ull && !(a & 7) && n < (1u << 20);
}

static void position_probe(unsigned char* match, int tick) {
    static const char* path = getenv("FM27_POSITIONS_JSONL");
    if (!path || !*path) return;
#if FM27_MAC_BUILD == 2505117
    static FILE* file = nullptr;
    static bool attempted = false;
    static std::string line;
    if (!attempted) {   // one attempt: a bad path must not retry every tick
        attempted = true;
        file = fopen(path, "w");
        if (!file) LOG("{\"event\":\"position_probe_error\",\"reason\":\"open_failed\"}");
    }
    if (!file) return;
    const float* ball = (const float*)(match + 0xaf0);
    if (!std::isfinite(ball[0]) || !std::isfinite(ball[1])) return;
    line.clear();
    char row[192];
    for (unsigned side = 0; side < 2; side++) {
        unsigned char* team = *(unsigned char**)(match + m_teams + 8 * side);
        if (!readable_ptr(team, 0x900)) continue;
        unsigned count = team[t_count];
        if (count > 26) continue;
        for (unsigned i = 0; i < count; i++) {
            unsigned char* player = *(unsigned char**)(team + t_roster + 8 * i);
            if (!readable_ptr(player, 0x2400)) continue;
            if (player[p_on_pitch] != 1) continue;
            unsigned slot = player[p_lineup_slot];
            if (slot >= 11) continue;
            const float* p = (const float*)(player + 0x140);
            if (!std::isfinite(p[0]) || !std::isfinite(p[1])) continue;
            snprintf(row, sizeof(row),
                     "{\"tick\":%d,\"side\":%u,\"slot\":%u,\"x\":%.9g,\"y\":%.9g,\"ball_x\":%.9g,\"ball_y\":%.9g}\n",
                     tick, side, slot, p[0], p[1], ball[0], ball[1]);
            line += row;
        }
    }
    // One write per tick: cheap, and the tail survives finish()'s _exit() or a crash.
    if (!line.empty() && fwrite(line.data(), 1, line.size(), file)) fflush(file);
#else
    (void)match; (void)tick;
#endif
}
