// Opt-in tactical-execution experiment (scenario kind 61): Mac counterpart of native/native_execution_experiment.h.
//
// Windows: d85a0 builds the 33-byte tactical-effectiveness record at MATCH_PLAYER+0xcba; 41a50 consumes it during
// action sampling; upstream redirects both entries with inline code hooks.
// Mac x86_64: builder 0x4dd5f80 (decompiled pair: same 10 arguments ending in the u16 CA, same writes at record
// +0x1c..+0x20; its only caller 0x4d07140 is the matched twin of d85a0's only caller d7340 and passes player+0xcb2),
// consumer 0x4ad49c0 (79/96 shared constants with 41a50; the common callee of the twins of both 41a50 callers; reads
// player+0xcb2..+0xcd3, i.e. the Windows record range -8). Record fields (Windows -> Mac): raw ability +0xcd6 -> +0xcce,
// role suitability +0xcd7 -> +0xccf, overall +0xcd8 -> +0xcd0, buy-in +0xcd9 -> +0xcd1, next-match information
// +0xcda -> +0xcd2. Engine version word match+0xa3a -> match+0xa2c (decompiled pair e0b00/0x4a23470; votes 172/180).
//
// No code is patched on macOS (signed library; code-signing enforcement). The host drives the step loop, so it writes
// the policy value into all 33 bytes of every listed player of both teams after preparation and before every step
// call, and counts how often the engine had rebuilt a record in between. Data writes only.
#pragma once

static int execution_policy[2] = {-1, -1};
static bool execution_enabled = false;
static unsigned long long execution_writes[2] = {}, execution_rebuilds[2] = {}, execution_steps = 0;
static unsigned short execution_input_ca[2][26] = {};
static bool execution_input_seen[2][26] = {};
static unsigned char execution_calculated_overall[2][26] = {};
static bool execution_built_seen[2][26] = {};   // first engine build observed (records are built once play starts)

static void execution_reset() {
    execution_policy[0] = execution_policy[1] = -1; execution_enabled = false;
    memset(execution_writes, 0, sizeof execution_writes); memset(execution_rebuilds, 0, sizeof execution_rebuilds); execution_steps = 0;
    memset(execution_input_ca, 0, sizeof execution_input_ca); memset(execution_input_seen, 0, sizeof execution_input_seen);
    memset(execution_calculated_overall, 0, sizeof execution_calculated_overall); memset(execution_built_seen, 0, sizeof execution_built_seen);
}

// Every run: the engine version word the original preparation will see.
static void log_engine_version(unsigned char* match, const char* stage) {
    LOG("{\"event\":\"native_engine_version_word\",\"stage\":\"%s\",\"value\":%u,\"hex\":\"0x%08x\"}", stage,
        *(uint32_t*)(match + m_engine_version), *(uint32_t*)(match + m_engine_version));
}

// Engine path. Every match the game itself creates starts at its constructor's word (FM27 27.0: 0x1b000000; 27.0.1: 0x1b000100); the bundled
// fixture was captured upstream and deserialises as 0x1a080000 (26.8), which sits below ~400 version branches of the
// engine. The host runs the FM27 path by default; FM27_ENGINE_PATH=fixture keeps the fixture's word (comparison only).
// kFm27EngineVersion: per build, from fm27_mac_x86_64.h (27.0: 0x1b000000, 27.0.1: 0x1b000100).
static void engine_path_install(unsigned char* match) {
    const char* path = getenv("FM27_ENGINE_PATH");
    bool fixture = path && !strcmp(path, "fixture");
    if (path && *path && !fixture && strcmp(path, "fm27")) finish(248);
    uint32_t before = *(uint32_t*)(match + m_engine_version);
    if (!fixture) *(uint32_t*)(match + m_engine_version) = kFm27EngineVersion;
    LOG("{\"event\":\"native_engine_path\",\"path\":\"%s\",\"before\":%u,\"after\":%u}", fixture ? "fixture" : "fm27",
        before, *(uint32_t*)(match + m_engine_version));
}

static void execution_install(unsigned char* match) {
    execution_reset();
    for (const auto& edit : scenario_edits) {
        if (edit.kind != 61) continue;
        if (execution_policy[edit.side] >= 0) finish(244);
        execution_policy[edit.side] = (int)edit.value;
        execution_enabled = true;
    }
    if (const char* v = getenv("FM27_MAC_ENGINE_VERSION")) {   // research only: version switch without a policy
        uint32_t value = (uint32_t)strtoul(v, nullptr, 0);
        LOG("{\"event\":\"research_engine_version_override\",\"before\":%u,\"after\":%u}", *(uint32_t*)(match + m_engine_version), value);
        *(uint32_t*)(match + m_engine_version) = value;
    }
    if (!execution_enabled) return;
    // Gate: only the image whose layout was mapped (x86_64 LC_UUID, checked at load by known_image()).
    char uuid[37]; snprintf(uuid, sizeof uuid, "%02X%02X%02X%02X-%02X%02X-%02X%02X-%02X%02X-%02X%02X%02X%02X%02X%02X",
        kUuid[0], kUuid[1], kUuid[2], kUuid[3], kUuid[4], kUuid[5], kUuid[6], kUuid[7], kUuid[8], kUuid[9], kUuid[10], kUuid[11], kUuid[12], kUuid[13], kUuid[14], kUuid[15]);
    if (!image_uuid_verified) finish(244);
    constexpr uint32_t version = kFm27EngineVersion;
    LOG("{\"event\":\"experimental_engine_version\",\"before\":%u,\"after\":%u,\"production_supported\":false,\"gate\":\"lc_uuid\",\"lc_uuid\":\"%s\",\"method\":\"data_write_between_steps\"}",
        *(uint32_t*)(match + m_engine_version), version, uuid);
    *(uint32_t*)(match + m_engine_version) = version;
}

// After the original preparation: remember what the engine computed, then apply the policy.
static void execution_prepared(unsigned char* match) {
    if (!execution_enabled) return;
    for (unsigned side = 0; side < 2; side++) {
        if (execution_policy[side] < 0) continue;
        auto team = team_of(match, side);
        for (unsigned i = 0; i < team[t_count]; i++) {
            auto player = roster_at(team, i); if (!player) continue;
            for (unsigned j = 0; j < 26; j++) if (original_roster[side][j] == player) {
                execution_input_ca[side][j] = *(uint16_t*)(player + p_ca);
                execution_input_seen[side][j] = true; break;
            }
        }
    }
}

// Research only: hold single record fields ("side[@slot.slot...]:offset=value,...", offsets within the 33-byte record,
// slots = input roster indices; no slot list = every listed player of that side), written like the policy (after
// preparation and before every step). Data writes only.
static int research_field_value[2][33];
static uint32_t research_field_slots[2][33];   // bit mask of input roster slots; 0 = all
static bool research_fields_loaded = false, research_fields_enabled = false;
static void research_fields_apply(unsigned char* match) {
    if (!research_fields_loaded) {
        research_fields_loaded = true;
        for (auto& side : research_field_value) for (auto& v : side) v = -1;
        if (const char* spec = getenv("FM27_MAC_EXEC_FIELDS")) {
            std::string all(spec); size_t at_ = 0;
            while (at_ < all.size()) {
                auto end = all.find(',', at_); auto item = all.substr(at_, end == std::string::npos ? std::string::npos : end - at_);
                unsigned side = 0, offset = 0, value = 0; uint32_t slots = 0;
                auto colon = item.find(':'), at_sign = item.find('@');
                if (colon == std::string::npos) finish(249);
                if (at_sign != std::string::npos && at_sign < colon) {
                    std::string list = item.substr(at_sign + 1, colon - at_sign - 1); size_t p = 0;
                    while (p < list.size()) { auto dot = list.find('.', p); unsigned slot = (unsigned)atoi(list.substr(p, dot - p).c_str()); if (slot >= 26) finish(249); slots |= 1u << slot; if (dot == std::string::npos) break; p = dot + 1; }
                    item = item.substr(0, at_sign) + item.substr(colon);
                }
                if (sscanf(item.c_str(), "%u:%i=%u", &side, &offset, &value) != 3 || side > 1 || offset >= exec_record_size || value > 255) finish(249);
                research_field_value[side][offset] = (int)value; research_field_slots[side][offset] = slots; research_fields_enabled = true;
                if (end == std::string::npos) break; at_ = end + 1;
            }
            LOG("{\"event\":\"research_exec_fields\",\"spec\":\"%s\"}", spec);
        }
    }
    if (!research_fields_enabled) return;
    for (unsigned side = 0; side < 2; side++) {
        auto team = team_of(match, side);
        for (unsigned i = 0; i < team[t_count]; i++) {
            auto player = roster_at(team, i); if (!player) continue;
            unsigned slot = 26;
            for (unsigned j = 0; j < 26; j++) if (original_roster[side][j] == player) { slot = j; break; }
            for (unsigned b = 0; b < exec_record_size; b++) {
                if (research_field_value[side][b] < 0) continue;
                if (research_field_slots[side][b] && (slot >= 26 || !(research_field_slots[side][b] >> slot & 1))) continue;
                player[p_exec_record + b] = (unsigned char)research_field_value[side][b];
            }
        }
    }
}

// Research: attribute changes on a loaded match (real saved matches), FM27_MAC_ATTR="side[@slot.slot...]:attr+delta|attr-delta|attr=value,...".
// attr is the catalog index (0-68), values are stored bytes (1-100 scale; clamped). Written once before preparation,
// like scenario attributes, and read back after preparation (finish(250) on any change).
struct AttrWrite { unsigned side, slot, attr; unsigned char value; };
static std::vector<AttrWrite> attr_writes;
static void research_attributes_apply(unsigned char* match) {
    attr_writes.clear();   // worker mode: one host process plays many matches
    const char* spec = getenv("FM27_MAC_ATTR");
    if (!spec || !*spec) return;
    std::string all(spec); size_t at_ = 0;
    while (at_ < all.size()) {
        auto end = all.find(',', at_); auto item = all.substr(at_, end == std::string::npos ? std::string::npos : end - at_);
        unsigned side = 0, attr = 0; int number = 0; char op = 0; uint32_t slots = 0;
        auto colon = item.find(':'), at_sign = item.find('@');
        if (colon == std::string::npos) finish(250);
        if (at_sign != std::string::npos && at_sign < colon) {
            std::string list = item.substr(at_sign + 1, colon - at_sign - 1); size_t p = 0;
            while (p < list.size()) { auto dot = list.find('.', p); unsigned slot = (unsigned)atoi(list.substr(p, dot - p).c_str()); if (slot >= 26) finish(250); slots |= 1u << slot; if (dot == std::string::npos) break; p = dot + 1; }
            item = item.substr(0, at_sign) + item.substr(colon);
        }
        if (sscanf(item.c_str(), "%u:%u%c%d", &side, &attr, &op, &number) != 4 || side > 1 || attr > 68 || (op != '+' && op != '-' && op != '=')) finish(250);
        auto team = team_of(match, side);
        for (unsigned i = 0; i < 26 && i < team[t_count]; i++) {
            if (slots && !(slots >> i & 1)) continue;
            auto player = roster_at(team, i); if (!player) continue;
            int v = player[p_attributes + attr];
            int nv = op == '=' ? number : op == '+' ? v + number : v - number;
            nv = nv < 1 ? 1 : nv > 100 ? 100 : nv;
            player[p_attributes + attr] = (unsigned char)nv;
            attr_writes.push_back({side, i, attr, (unsigned char)nv});
        }
        if (end == std::string::npos) break; at_ = end + 1;
    }
    LOG("{\"event\":\"research_attributes\",\"spec\":\"%s\",\"writes\":%zu}", spec, attr_writes.size());
}
static void research_attributes_verify(unsigned char* match) {
    if (attr_writes.empty()) return;
    for (auto& w : attr_writes) {
        auto player = original_roster[w.side][w.slot];
        if (!player || player[p_attributes + w.attr] != w.value) { LOG("{\"event\":\"research_attributes_changed\",\"side\":%u,\"slot\":%u,\"attr\":%u}", w.side, w.slot, w.attr); finish(250); }
    }
    LOG("{\"event\":\"research_attributes_verified\",\"writes\":%zu}", attr_writes.size());
}

static void execution_apply(unsigned char* match, bool count_rebuilds) {
    research_fields_apply(match);
    if (!execution_enabled) return;
    for (unsigned side = 0; side < 2; side++) {
        if (execution_policy[side] < 0) continue;
        auto team = team_of(match, side); auto value = (unsigned char)execution_policy[side];
        for (unsigned i = 0; i < team[t_count]; i++) {
            auto player = roster_at(team, i); if (!player) continue;
            auto record = player + p_exec_record;
            bool held = true;
            for (unsigned b = 0; b < exec_record_size; b++) if (record[b] != value) { held = false; break; }
            if (held) continue;
            if (count_rebuilds) {
                execution_rebuilds[side]++;
                for (unsigned j = 0; j < 26; j++) if (original_roster[side][j] == player) {
                    if (!execution_built_seen[side][j]) { execution_built_seen[side][j] = true; execution_calculated_overall[side][j] = record[exec_overall]; }
                    break;
                }
            }
            memset(record, value, exec_record_size);
            execution_writes[side]++;
        }
    }
    if (count_rebuilds) execution_steps++;
}

static void execution_snapshot(unsigned char* match, const char* stage) {
    if (!execution_enabled) return;
    for (unsigned side = 0; side < 2; side++) {
        auto team = team_of(match, side);
        fprintf(log_file, "{\"event\":\"native_execution_probe\",\"stage\":\"%s\",\"side\":%u,\"policy\":%d,\"method\":\"data_write_between_steps\",\"build_calls\":null,\"sample_calls\":null,\"writes\":%llu,\"steps\":%llu,\"engine_rebuilds_overwritten\":%llu,\"players\":[",
                stage, side, execution_policy[side], execution_writes[side], execution_steps, execution_rebuilds[side]);
        for (unsigned i = 0; i < team[t_count]; i++) {
            auto p = roster_at(team, i), r = p + p_exec_record;
            fprintf(log_file, "%s{\"slot\":%u,\"overall\":%u,\"buy_in\":%u,\"next_match_information\":%u,\"raw_ability_component\":%u,\"role_suitability_component\":%u,",
                    i ? "," : "", i, r[exec_overall], r[exec_buy_in], r[exec_next_match], r[exec_raw_ability], r[exec_role_suitability]);
            for (unsigned j = 0; j < 26; j++) if (original_roster[side][j] == p && execution_input_seen[side][j]) {
                fprintf(log_file, "\"input_roster_slot\":%u,\"input_ca\":%u,", j, execution_input_ca[side][j]);
                if (execution_built_seen[side][j]) fprintf(log_file, "\"calculated_overall_before_override\":%u,", execution_calculated_overall[side][j]);
                else fputs("\"calculated_overall_before_override\":null,", log_file);
                break;
            }
            fputs("\"record_hex\":\"", log_file);
            for (unsigned j = 0; j < 34; j++) fprintf(log_file, "%02x", r[j]);
            fputs("\"}", log_file);
        }
        fputs("]}\n", log_file); fflush(log_file);
    }
}

// Research: per-team record summary without any policy (what the engine computed), for staff-value experiments.
static void record_summary(unsigned char* match, const char* stage) {
    if (!getenv("FM27_MAC_RECORD_SUMMARY")) return;
    for (unsigned side = 0; side < 2; side++) {
        auto team = team_of(match, side);
        fprintf(log_file, "{\"event\":\"research_record_summary\",\"stage\":\"%s\",\"side\":%u,\"players\":[", stage, side);
        for (unsigned i = 0; i < team[t_count] && i < 11; i++) {
            auto r = roster_at(team, i) + p_exec_record;
            fprintf(log_file, "%s[%u,%u,%u,%u,%u,%u,\"", i ? "," : "", r[exec_raw_ability], r[exec_role_suitability], r[exec_overall], r[exec_buy_in], r[exec_next_match],
                    *(uint32_t*)(roster_at(team, i) + 0x48));   // + player id and the whole record (34 bytes incl. mode)
            for (unsigned j = 0; j < 34; j++) fprintf(log_file, "%02x", r[j]);
            fputs("\"]", log_file);
        }
        fputs("]}\n", log_file); fflush(log_file);
    }
}
