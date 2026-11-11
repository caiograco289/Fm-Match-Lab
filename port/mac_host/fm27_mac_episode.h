// Set-piece episodes and set-piece selection logging: Mac twin of native/native_setpiece_episode.h and the
// native_setpiece_selected block of native/desktop_host.cpp.
// Dead-ball code match+0x12d60 (Windows 0x12d70; decompiled pair 0xddc70/0x4d09e20), code -> attacking routine type via
// the game's table 0x59ba738 (Windows 0x4e38a90; identical on every entry the game's own mask 0x1f99 admits), restart
// team match+0x12d40 (Windows 0x12d50; displacement votes 26/28, runtime-checked to be one of the two teams).
// Selected variant per type: byte in *(manager+0x298) at 0x334a+(t-5)*2 (attacking) / 0x334b+2t (defending), Windows
// 0x331a/0x331b (same pair: every byte in that block sits +0x30 on Mac).
#pragma once

static unsigned deadball_type(unsigned char* match, unsigned* code_out = nullptr) {
    unsigned code = match[m_deadball];
    if (code_out) *code_out = code;
    if (code < 1 || code > 13 || !((0x1f99u >> (code - 1)) & 1u)) return 0;
    return at<unsigned char*>(g_deadball_types)[code - 1];
}
static int selected_variant(unsigned char* manager, unsigned type) {
    auto active = *(unsigned char**)(manager + mg_active_manager);
    if (!active || type > 9) return -1;
    return (signed char)active[type >= 5 ? av_attacking + (type - 5) * 2 : av_attacking + 1 + type * 2];
}

static int observed_setpiece[2] = {-1, -1};
static void log_setpiece_selection(unsigned char* match, int tick) {
    unsigned code = 0;
    unsigned attacking_type = deadball_type(match, &code);
    if (!attacking_type) { observed_setpiece[0] = observed_setpiece[1] = -1; return; }
    auto taking = *(unsigned char**)(match + m_restart_team);
    for (unsigned side = 0; side < 2; side++) {
        auto team = team_of(match, side); auto manager = manager_of(team);
        unsigned type = attacking_type - (team == taking ? 0 : 5);
        int variant = selected_variant(manager, type);
        if (variant < 0 || variant >= 3) continue;
        auto obj = routine(manager, type * 16 + variant); if (!obj) continue;
        int key = (int)(code * 256 + type * 16 + variant);
        if (key == observed_setpiece[side]) continue;
        observed_setpiece[side] = key; auto vt = *(void***)obj;
        LOG("{\"event\":\"native_setpiece_selected\",\"side\":%u,\"deadball\":%u,\"type\":%u,\"variant\":%d,\"frequency\":%u,\"strategy\":%u,\"swing\":%u,\"tick\":%d}",
            side, code, type, variant, obj[0x14], ((unsigned char (*)(void*))vt[19])(obj), ((unsigned char (*)(void*))vt[20])(obj), tick);
    }
}

struct EpisodeStats { uint32_t possession; float xg; unsigned shots, on_target, passes, completed; };
static EpisodeStats episode_stats(unsigned char* match, unsigned side) {
    auto s = *(unsigned char**)(team_of(match, side) + t_statistics);
    return {*(uint32_t*)(s + 0x7c), *(float*)(s + 0x60), s[0x16f], s[0x170], *(unsigned short*)(s + 0xd8), *(unsigned short*)(s + 0xda)};
}
static struct {
    bool enabled = false, found = false, window_closed = false; unsigned type = 5, side = 0, seconds = 30;
    int start_tick = 0, start_clock = 0, delivery_tick = 0, delivery_clock = 0, window_end_tick = 0, window_end_clock = 0;
    int goals[2] = {}; EpisodeStats stats[2], window_stats[2];
} episode;
static void episode_init() {
    episode = {};
    const char* text = getenv("FM27_EPISODE_TYPE"); if (!text) return;
    episode.enabled = true; episode.type = (unsigned)strtoul(text, nullptr, 10);
    if (episode.type < 5 || episode.type > 9) finish(178);
    if ((text = getenv("FM27_EPISODE_SIDE"))) episode.side = (unsigned)strtoul(text, nullptr, 10);
    if (episode.side > 1) finish(178);
    if ((text = getenv("FM27_EPISODE_SECONDS"))) episode.seconds = (unsigned)strtoul(text, nullptr, 10);
    if (episode.seconds < 5 || episode.seconds > 120) finish(178);
}
static unsigned episode_score(unsigned char* match, unsigned side) {
    auto result = *(void**)(*(unsigned char**)(match + m_score_context) + score_result);
    return *((unsigned char* (*)(void*, unsigned))(*(void***)result)[vslot_score])(result, side);
}
[[noreturn]] static void episode_finish(unsigned char* match, bool valid, const char* reason) {
    int goals[2] = {};
    for (unsigned side = 0; side < 2; side++) goals[side] = episode.found ? (int)episode_score(match, side) - episode.goals[side] : 0;
    LOG("{\"event\":\"native_setpiece_episode_finished\",\"full_match_completed\":false,\"found\":%s,\"reason\":\"%s\",\"type\":%u,\"attacking_side\":%u,\"start_tick\":%d,\"start_clock\":%d,\"delivery_tick\":%d,\"end_tick\":%d,\"clock\":%d,\"window_end_tick\":%d,\"window_end_clock\":%d,\"window_seconds\":%u,\"context_goals_delta\":[%d,%d]}",
        valid ? "true" : "false", reason, episode.type, episode.side, episode.start_tick, episode.start_clock, episode.delivery_tick,
        *(int*)(match + m_tick), *(int*)(match + m_clock), episode.window_end_tick, episode.window_end_clock, episode.seconds, goals[0], goals[1]);
    if (valid) {
        EpisodeStats delta[2];
        for (unsigned side = 0; side < 2; side++) {
            auto now = episode.window_stats[side], old = episode.stats[side];
            delta[side] = {now.possession - old.possession, now.xg - old.xg, now.shots - old.shots, now.on_target - old.on_target, now.passes - old.passes, now.completed - old.completed};
        }
        double total = (double)delta[0].possession + delta[1].possession;
        fputs("{\"event\":\"native_episode_statistics\",\"source\":\"original_team_statistics_window_delta\",\"teams\":[", log_file);
        for (unsigned side = 0; side < 2; side++) {
            auto d = delta[side];
            fprintf(log_file, "%s{\"side\":%u,\"possession_ticks\":%u,\"possession\":%.9g,\"xg\":%.9g,\"shots\":%u,\"shots_on_target\":%u,\"passes\":%u,\"completed_passes\":%u}",
                    side ? "," : "", side, d.possession, total ? d.possession / total : 0, d.xg, d.shots, d.on_target, d.passes, d.completed);
        }
        fputs("]}\n", log_file); fflush(log_file);
    }
    desktop_player_totals(match);
    desktop_events_stop();
    finish(0);
}
static void episode_step(unsigned char* match) {
    if (!episode.enabled) return;
    int tick = *(int*)(match + m_tick), clock = *(int*)(match + m_clock);
    unsigned type = deadball_type(match);
    auto taking = *(unsigned char**)(match + m_restart_team);
    auto requested = team_of(match, episode.side);
    if (!episode.found && type == episode.type && taking == requested) {
        episode.found = true; episode.start_tick = tick; episode.start_clock = clock;
        for (unsigned side = 0; side < 2; side++) { episode.goals[side] = episode_score(match, side); episode.stats[side] = episode_stats(match, side); }
        LOG("{\"event\":\"native_setpiece_episode_started\",\"tick\":%d,\"clock\":%d,\"deadball\":%u,\"type\":%u,\"attacking_side\":%u}", tick, clock, match[m_deadball], type, episode.side);
    }
    if (episode.found) {
        if (!episode.delivery_tick && (type != episode.type || taking != requested)) { episode.delivery_tick = tick; episode.delivery_clock = clock; }
        if (!episode.window_closed && episode.delivery_tick && clock - episode.delivery_clock >= (int)episode.seconds * 4) {
            episode.window_closed = true; episode.window_end_tick = tick; episode.window_end_clock = clock;
            for (unsigned side = 0; side < 2; side++) episode.window_stats[side] = episode_stats(match, side);
        }
        if (episode.window_closed && clock - episode.window_end_clock >= 240) episode_finish(match, true, "window_and_settlement_completed");
        if (!episode.window_closed && clock - episode.start_clock > 720) episode_finish(match, false, "restart_not_completed");
    }
    if (*(unsigned*)(match + m_flags) & 4)
        episode_finish(match, episode.window_closed, episode.window_closed ? "window_completed_before_full_time" : "no_qualified_episode_before_full_time");
}
