// Match results for the macOS host: ports of native_statistics.h (team statistics), the final incident registry
// and player totals from native_match_events.h, the Steam session cleanup and the per-match release.
// Layout evidence (Mac x86_64): team statistics record behind team+0x6a0 (Windows 0x690) with unchanged internal
// offsets (3-3 probe: xG 0.96/1.91, passes 562/503 and 622/564, shots 10/6 and 10/5); score context is -8 after
// +0x18 (player totals +0x68/+0x70, registry +0x38); totals records keep +0x18 person key and +0x8b goals
// (keys matched 20/20 per side; goals summed to the score).
#pragma once
enum : uintptr_t {
    t_statistics       = 0x6a0,      // 0x690
    t_registered       = 0x73e,      // 0x72e (registered match roster; team count region +0x10)
    ctx_registry       = 0x38,       // 0x40
    ctx_totals         = 0x68,       // 0x70
    totals_records     = 0x250,      // same
    p_native_id        = 0x48,       // 0x50
    p_identity         = 0x20,       // 0x28 (person-key argument)
    vslot_person_key   = 63,         // Windows 0x1f0/8 = 62; Itanium: key = f(this, identity) returned in EAX
    vslot_interface_release = 2,     // Windows vtable[1]
    fn_match_dtor      = FM27_RVA(fn_match_dtor, 0x49875d0),  // 0x4968820 (from Mac release helper 0x3186590)
};

static uint32_t person_key(unsigned char* player) {
    void* iface = *at<void**>(g_interface);
    return ((uint32_t (*)(void*, void*))(*(void***)iface)[vslot_person_key])(iface, player + p_identity);
}

static void desktop_match_statistics(unsigned char* match) {
    unsigned char* records[2] = {}; unsigned ticks[2] = {};
    for (unsigned side = 0; side < 2; side++) {
        records[side] = *(unsigned char**)(team_of(match, side) + t_statistics);
        ticks[side] = *(unsigned*)(records[side] + 0x7c);
    }
    unsigned total = ticks[0] + ticks[1];
    fprintf(log_file, "{\"event\":\"native_match_statistics\",\"schema\":1,\"source\":\"original_team_statistics\",\"teams\":[");
    for (unsigned side = 0; side < 2; side++) {
        auto s = records[side];
        fprintf(log_file, "%s{\"side\":%u,\"possession_ticks\":%u,\"possession\":", side ? "," : "", side, ticks[side]);
        if (total) fprintf(log_file, "%.9g", (double)ticks[side] / total); else fputs("null", log_file);
        fprintf(log_file, ",\"xg\":%.9g,\"shots\":%u,\"shots_on_target\":%u,\"passes\":%u,\"completed_passes\":%u}", *(float*)(s + 0x60), s[0x16f], s[0x170],
                *(unsigned short*)(s + 0xd8), *(unsigned short*)(s + 0xda));
    }
    fputs("]}\n", log_file); fflush(log_file);
}

static void event_person(unsigned char* match, unsigned side, unsigned index) {
    if (side > 1) { fputs("null", log_file); return; }
    auto team = team_of(match, side);
    if (index >= team[t_count]) { fputs("null", log_file); return; }
    auto actor = roster_at(team, index);
    if (!actor) { fputs("null", log_file); return; }
    fprintf(log_file, "{\"side\":%u,\"roster_index\":%u,\"native_id\":%u,\"ip_position\":%u,\"oop_position\":%u}", side, index,
            *(unsigned*)(actor + p_native_id), *(unsigned*)(actor + p_cell_ip), *(unsigned*)(actor + p_cell_oop));
}

static bool event_details_disabled = false;

static void desktop_final_incidents(unsigned char* match) {
    uintptr_t context = 0, bounds[2] = {}; const char* error = nullptr;
    if (!safe_copy(match + m_score_context, &context, 8) || !safe_copy((void*)(context + ctx_registry), bounds, sizeof(bounds))) error = "registry_header_unreadable";
    if (!error && (bounds[1] < bounds[0] || bounds[1] - bounds[0] > 32768 || (bounds[1] - bounds[0]) % 8)) error = "registry_bounds_invalid";
    std::vector<uintptr_t> pointers; std::vector<std::array<unsigned char, 0x28>> records;
    if (!error) {
        pointers.resize((bounds[1] - bounds[0]) / 8); records.resize(pointers.size());
        if (!pointers.empty() && !safe_copy((void*)bounds[0], pointers.data(), pointers.size() * 8)) error = "registry_index_unreadable";
        for (size_t i = 0; !error && i < pointers.size(); i++) if (!safe_copy((void*)pointers[i], records[i].data(), 0x28)) error = "registry_record_unreadable";
    }
    if (error) { fprintf(log_file, "{\"event\":\"native_final_incident_registry\",\"valid\":false,\"error\":\"%s\",\"incidents\":[]}\n", error); return; }
    fputs("{\"event\":\"native_final_incident_registry\",\"schema\":1,\"valid\":true,\"incidents\":[", log_file);
    for (size_t i = 0; i < records.size(); i++) {
        auto p = records[i].data(); uint32_t tick = 0; memcpy(&tick, p + 0x18, 4);
        fprintf(log_file, "%s{\"index\":%zu,\"native_type\":%u,\"side\":%u,\"roster_index\":%u,\"other_side\":%u,\"other_index\":%u,\"nominal_minute\":%u,\"added_minute\":%u,\"native_tick\":%u,\"person\":",
                i ? "," : "", i, p[0x1f], p[0x1d], p[0x1e], p[0x21], p[0x22], p[0x1c], p[0x20], tick);
        event_person(match, p[0x1d], p[0x1e]); fputs(",\"other_person\":", log_file); event_person(match, p[0x21], p[0x22]);
        fputs(",\"raw\":\"", log_file); for (auto v : records[i]) fprintf(log_file, "%02x", v); fputs("\"}", log_file);
    }
    fputs("]}\n", log_file);
}

static void desktop_player_totals(unsigned char* match) {
    if (event_details_disabled) return;
    desktop_final_incidents(match);
    fputs("{\"event\":\"native_player_match_totals\",\"players\":[", log_file); bool comma = false;
    unsigned checked = 0; bool identity_ok = true;
    for (unsigned side = 0; side < 2; side++) {
        auto team = team_of(match, side);
        auto context = *(unsigned char**)(match + m_score_context), totals = *(unsigned char**)(context + ctx_totals + 8 * side);
        auto begin = *(unsigned char***)(totals + totals_records), end = *(unsigned char***)(totals + totals_records + 8);
        if (end < begin || end - begin < 11 || end - begin > 26 || end - begin != team[t_registered]) { identity_ok = false; continue; }
        for (auto item = begin; item != end; item++) {
            auto stats = *item; unsigned char* actor = nullptr; unsigned index = 0, matches = 0;
            for (unsigned i = 0; i < team[t_count]; i++) {
                auto candidate = roster_at(team, i);
                if (person_key(candidate) == *(uint32_t*)(stats + 0x18)) { actor = candidate; index = i; matches++; }
            }
            if (matches != 1) { identity_ok = false; continue; }
            checked++;
            fprintf(log_file, "%s{\"side\":%u,\"roster_index\":%u,\"native_id\":%u,\"goals\":%u,\"yellow_cards\":%u,\"red_cards\":%u,\"ip_position\":%u,\"oop_position\":%u}",
                    comma ? "," : "", side, index, *(unsigned*)(actor + p_native_id), stats[0x8b], stats[0xa6], stats[0xa7], *(unsigned*)(actor + p_cell_ip),
                    *(unsigned*)(actor + p_cell_oop));
            comma = true;
        }
    }
    // macOS: no hardware-breakpoint queue observer (x86 debug registers are unavailable under Rosetta); goals and
    // cards come from the engine's final incident registry, which the Python collector checks against these totals.
    fprintf(log_file, "],\"queue_observations\":0,\"observer_installed\":false,\"nonzero_packet_padding_observations\":0}\n");
    fprintf(log_file, "{\"event\":\"native_player_statistics_identity_verified\",\"verified\":%s,\"canonical_records\":%u}\n", identity_ok ? "true" : "false", checked);
    fflush(log_file);
}

static bool desktop_events_start() {
    event_details_disabled = getenv("FM27_SKIP_EVENT_DETAILS") != nullptr;
    if (event_details_disabled) LOG("{\"event\":\"native_event_details_disabled\",\"observer_installed\":false}");
    else LOG("{\"event\":\"native_event_observer_mode\",\"platform\":\"macos\",\"queue_observer\":false,\"source\":\"original_final_incident_registry\"}");
    return true;
}
static bool desktop_events_stop() {
    if (event_details_disabled) LOG("{\"event\":\"native_event_observer_stopped\",\"details_disabled\":true,\"debug_registers_untouched\":true}");
    else LOG("{\"event\":\"native_event_observer_stopped\",\"queue_observer\":false,\"debug_registers_untouched\":true}");
    event_details_disabled = false;
    return true;
}

// Orderly release of this process's own Steamworks session (never another process's).
static bool steam_cleanup_done = false, steam_cleanup_ok = true;
static bool desktop_steam_cleanup() {
    if (steam_cleanup_done) return steam_cleanup_ok;
    steam_cleanup_done = true;
    void* steam = dlopen((game_root + "/../Frameworks/libsteam_api.dylib").c_str(), RTLD_NOLOAD | RTLD_LAZY);
    if (!steam) { LOG("{\"event\":\"steam_session_cleanup\",\"module_loaded\":false,\"ok\":true}"); return true; }
    auto shutdown = (void (*)())dlsym(steam, "SteamAPI_Shutdown");
    auto pipe = (int (*)())dlsym(steam, "SteamAPI_GetHSteamPipe");
    auto user = (int (*)())dlsym(steam, "SteamAPI_GetHSteamUser");
    auto release = (void (*)())dlsym(steam, "SteamAPI_ReleaseCurrentThreadMemory");
    int bp = pipe ? pipe() : -1, bu = user ? user() : -1;
    if (release) release();
    if (shutdown) shutdown();
    int ap = pipe ? pipe() : -1, au = user ? user() : -1;
    steam_cleanup_ok = shutdown && pipe && user && ap == 0 && au == 0;
    LOG("{\"event\":\"steam_session_cleanup\",\"module_loaded\":true,\"shutdown_called\":%s,\"pipe_before\":%d,\"pipe_after\":%d,\"user_before\":%d,\"user_after\":%d,\"fault\":0,\"ok\":%s}",
        shutdown ? "true" : "false", bp, ap, bu, au, steam_cleanup_ok ? "true" : "false");
    dlclose(steam);
    return steam_cleanup_ok;
}
