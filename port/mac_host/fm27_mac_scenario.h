// Scenario editor for the macOS host: port of apply_scenario/verify_scenario from native/desktop_host.cpp
// with the Mac x86_64 layout (fm27_mac_x86_64.h). Edit kinds whose Mac offsets are not yet mapped are
// rejected explicitly (scenario_kind_not_ported) instead of writing to guessed offsets.
#pragma once
#include <fstream>
#include <vector>
#include <algorithm>
#include "fm27_tactic_bindings.h"

struct ScenarioEdit { uint32_t kind, side, a, b, value; };
static std::vector<ScenarioEdit> scenario_edits;
static std::string scenario_file;
static ScenarioEdit current_scenario_edit = {};
static const char* scenario_stage = "initial";
static unsigned char* original_roster[2][26] = {};
static bool game_constraints[2] = {false, false};

static unsigned char* team_of(unsigned char* match, unsigned side) { return *(unsigned char**)(match + m_teams + 8 * side); }
static unsigned char* manager_of(unsigned char* team) { return *(unsigned char**)(team + t_manager); }
static unsigned char* roster_at(unsigned char* team, unsigned i) { return *(unsigned char**)(team + t_roster + 8 * i); }
static uint32_t packed_oi(const unsigned char* p) { return p[0] | (p[1] << 8) | (p[2] << 16); }
static void set_oi(unsigned char* p, uint32_t v) { p[0] = (unsigned char)v; p[1] = (unsigned char)(v >> 8); p[2] = (unsigned char)(v >> 16); }
static bool valid_oi(uint32_t v) { return !(v & ~0x83f3fu) && (v & 7) <= 2 && ((v >> 3) & 7) <= 2 && ((v >> 8) & 7) <= 3 && ((v >> 11) & 7) <= 3; }

static unsigned char* tactic_cell(unsigned char* manager, unsigned encoded, bool canonical = false) {
    if (encoded / 16 > 1 || encoded % 16 >= 11) return nullptr;
    return manager + (canonical ? mg_cells_canon : mg_cells_live) + (encoded / 16 ? cell_oop_offset : cell_ip_offset) + (encoded % 16) * cell_stride;
}
static uint64_t* instruction_entry(unsigned char* cell, bool create) {
    uint64_t key = *(uint64_t*)(cell + cell_role) & 0xfffffffbf91fffffULL;
    auto p = *(uint64_t**)(cell + 8), end = *(uint64_t**)(cell + 16);
    while (p != end && *p < key) p += 3;
    if (p != end && *p == key) return p;
    if (!create) return nullptr;
    uint64_t value[3] = {key, 0, 0xff00000000ULL};
    auto entry = ((uint64_t* (*)(void*, void*, const void*))at(fn_instruction_insert))(cell + 8, p, value);
    if (!entry || *entry != key) { LOG("{\"event\":\"instruction_insert_unexpected\"}"); return nullptr; }
    return entry;
}

static bool profile_value(unsigned char* player, unsigned field, uint32_t value, bool write, unsigned char* owner_team = nullptr) {
    unsigned offset = 0, size = 0, max = 0xffffffff, min = 0;
    if (field == 0) {
        if (value < 140 || value > 220) return false;
        float height = value / 100.0f; uint32_t bits; memcpy(&bits, &height, 4);
        if (write) memcpy(player + p_height, &bits, 4);
        return *(uint32_t*)(player + p_height) == bits;
    }
    // Windows offsets minus 8: the match-player block is uniformly -8 on macOS (data + votes, see REPORT).
    if (field == 1) { offset = p_age; size = 1; min = 14; max = 60; }
    else if (field >= 2 && field <= 8) { offset = p_field2 + field - 2; size = 1; min = 1; max = 20; }
    else if (field == 9 || field == 10) { offset = 0xbb0 + 4 * (field - 9); size = 4; }
    else if (field >= 11 && field <= 18) {
        static const unsigned offsets[] = {0xc90, 0xc84, 0xc8e, 0xc70, 0xc82, 0xc88, 0xc72, 0xc7c};
        offset = offsets[field - 11]; size = 2; max = field == 11 ? 200 : (field == 18 ? 65535 : 10000);
    }
    else if (field == 19) { offset = p_field19; size = 1; min = 40; max = 140; }
    else if (field == 20 || field == 21) { offset = field == 20 ? 0xca0 : 0xc9a; size = 1; max = 100; }
    else if (field == 22) { offset = 0xc9b; size = 1; min = 1; max = 20; }
    else return false;
    if (value < min || value > max) return false;
    if (write && field == 20) {
        if (!owner_team) return false;
        int adjustment = (signed char)owner_team[t_adjustment];
        int input = (int)value * 2 - 50 - adjustment * 5;
        if (input < 0 || input > 100 || abs(input - (int)value) > 25) return false;
        value = (uint32_t)input;
    }
    if (write) memcpy(player + offset, &value, size);
    uint32_t actual = 0; memcpy(&actual, player + offset, size);
    return actual == value;
}

static uint32_t person_key(unsigned char* player);   // fm27_mac_results.h
// Set-piece taker priority lists (kind 30). The manager embeds a selection object (Mac manager+0x6e0, Windows +0x6e8;
// identical internal layout in the decompiled caller pairs 0x5b7ff0/0x4ab480 and 0x5afa10/0x4a2380): lists 2..11 at
// +8 via the getter (0x4a204f0 <-> 0x507acc0, identical bodies), 12..19 at +0xf8, list 0 at +0x1d0, list 1 at +0x1e8,
// captain key at +0x200 (= mg_captain_key), routines at +0x208 (= mg_routines).
static unsigned char* priority_list(unsigned char* manager, unsigned id) {
    if (id == 0) return manager + mg_selection + 0x1d0;
    if (id == 1) return manager + mg_selection + 0x1e8;
    if (id >= 12 && id < 20) return manager + mg_selection + 0xf8 + (id - 12) * 24;
    if (id > 11) return nullptr;
    return ((unsigned char* (*)(void*, unsigned char, signed char))at(fn_priority_list))(manager + mg_selection + 8, 5 + (id - 2) / 2, (id - 2) % 2);
}

// Set-piece routines (kinds 40-45, 47). Routine container at manager+mg_routines (Windows +0x8f0); its per-type vectors
// sit 0x10 lower than on Windows (decompiled getter pair 0xea590/0x4d75590). Routine objects have the Windows field
// layout (runtime-checked against the fixture: key +0x10, frequency +0x14, opaque flags +0x15, 8 task groups at
// +0x18 stride 0x20, priority bytes +0x118, backups (3-byte rows) +0x130). Itanium vtable: Windows slot n>=1 -> n+1
// (getters 19/20 and group count 15 runtime-checked against the fixture for all 10 types; 13 = set backup, decompiled).
// Vectors use the engine pool (alloc 0x48511b0, sized free 0x4851620, pool getter 0x48516d0), as the inlined game code.
static unsigned char* routine_vector(unsigned char* manager, unsigned type) {
    static const unsigned offsets[] = {0xd00, 0xd30, 0xd90, 0xdc0, 0xd60, 0xd18, 0xd48, 0xda8, 0xdd8, 0xd78};
    return type < 10 ? manager + mg_routines + offsets[type] : nullptr;
}
static unsigned char* routine(unsigned char* manager, unsigned encoded) {
    if (encoded / 16 >= 10 || encoded % 16 >= 3) return nullptr;
    return ((unsigned char* (*)(void*, unsigned, size_t))at(fn_routine))(manager + mg_routines, encoded / 16, encoded % 16);
}
static void* engine_pool() { return ((void* (*)())at(fn_pool_get))(); }
static void* pool_alloc(size_t n) { return ((void* (*)(void*, size_t))at(fn_pool_alloc))(engine_pool(), n); }
static void pool_free(void* p, size_t n) { ((void (*)(void*, void*, size_t))at(fn_pool_free))(engine_pool(), p, n); }
static void pool_vector_append(unsigned char* vec, const void* item, size_t elem) {   // libc++ vector: begin, end, cap
    auto& b = *(unsigned char**)vec; auto& e = *(unsigned char**)(vec + 8); auto& c = *(unsigned char**)(vec + 16);
    if (e + elem > c) {
        size_t size = e - b, cap = c - b, want = std::max(cap * 2, size + elem);
        want = (want + elem - 1) / elem * elem;
        auto fresh = (unsigned char*)pool_alloc(want);
        if (size) memcpy(fresh, b, size);
        if (b) pool_free(b, cap);
        b = fresh; e = fresh + size; c = fresh + want;
    }
    memcpy(e, item, elem); e += elem;
}
static size_t routine_size(unsigned type) { return type == 0 || type == 1 || type == 4 || type == 9 ? 0x148 : 0x150; }

static bool not_ported(const ScenarioEdit& e) {
    LOG("{\"event\":\"scenario_kind_not_ported\",\"platform\":\"macos\",\"kind\":%u,\"side\":%u,\"a\":%u,\"b\":%u,\"value\":%u}", e.kind, e.side, e.a, e.b, e.value);
    return false;
}

static bool load_scenario() {
    if (scenario_file.empty()) return true;
    std::ifstream file(scenario_file, std::ios::binary);
    char magic[8] = {}; uint32_t count = 0;
    file.read(magic, 8); file.read((char*)&count, 4);
    if (!file || memcmp(magic, "FM27CFG1", 8) || count > 20000) {
        if (!memcmp(magic, "FM27CFG2", 8)) LOG("{\"event\":\"scenario_source_generation_not_ported\",\"platform\":\"macos\"}");
        return false;
    }
    scenario_edits.resize(count);
    file.read((char*)scenario_edits.data(), count * sizeof(ScenarioEdit));
    if (!file || file.peek() != EOF) return false;
    game_constraints[0] = game_constraints[1] = false;
    for (auto e : scenario_edits) if (e.kind == 13) { if (e.side > 1 || e.value > 1) return false; game_constraints[e.side] = e.value != 0; }
    return true;
}

// In-match management (scenario kind 62, macOS): the manager input-flag word (manager+0x30d0) set after preparation and
// before kick-off. Bit 0 (human in control: set by kind 10 so preparation keeps the edited tactic) also stops all
// in-match decisions for that team: no substitutions, no tactical changes. The words FM27 itself stores for a team
// managed by the assistant (instant result / holiday: 0x25306) and by the AI (0x24000) hand the match over; read
// from saved matches. Assistant: the tactic is kept and the assistant substitutes; AI: the AI re-plans roles at
// kick-off and adjusts during the match. Data write only.
constexpr uint32_t kManageAssistant = 0x25306, kManageAi = 0x24000;
static void in_match_management_apply(unsigned char* match) {
    for (const auto& edit : scenario_edits) if (edit.kind == 62) {
        auto flags = (uint32_t*)(manager_of(team_of(match, edit.side)) + mg_input_flags);
        uint32_t before = *flags; *flags = edit.value;
        LOG("{\"event\":\"native_in_match_management\",\"side\":%u,\"mode\":\"%s\",\"before\":%u,\"after\":%u,\"after_original_preparation\":true}",
            edit.side, edit.value == kManageAssistant ? "assistant" : "ai", before, *flags);
    }
}

static bool apply_scenario(unsigned char* match) {
    if (scenario_file.empty()) return true;
    unsigned char creator[2][0x28]; bool changed[2] = {false, false};
    for (unsigned side = 0; side < 2; side++) {
        auto team = team_of(match, side);
        memcpy(creator[side], manager_of(team) + mg_creator_live, 0x28);
        for (unsigned i = 0; i < 26; i++) original_roster[side][i] = roster_at(team, i);
    }
    unsigned attributes = 0, instructions = 0;
    for (const auto& edit : scenario_edits) {
        current_scenario_edit = edit; scenario_stage = "records";
        if (edit.side > 1) return false;
        auto team = team_of(match, edit.side); auto manager = manager_of(team);
        switch (edit.kind) {
        case 61: if (edit.a || edit.b || edit.value > 100) return false; break;
        case 62: if (edit.a || edit.b || (edit.value != kManageAssistant && edit.value != kManageAi)) return false; break;   // applied after preparation
        case 17: if (edit.value < 11 || edit.value > team[t_count]) return false; break;
        case 1: {
            if (edit.a >= team[t_count] || edit.b >= 69 || edit.value > (edit.b < 15 ? 20u : 100u)) return false;
            if (edit.b >= 15 && !edit.value) return false;
            roster_at(team, edit.a)[p_attributes + edit.b] = (unsigned char)edit.value; attributes++; break;
        }
        case 18: {
            auto cell = tactic_cell(manager, edit.a); if (!cell) return false;
            auto entry = instruction_entry(cell, true); if (!entry) return false;
            entry[1] = 0; *(uint32_t*)((unsigned char*)entry + 16) = 0; ((unsigned char*)entry)[20] = 255; break;
        }
        case 15:
            if (edit.a >= team[t_count] || !profile_value(roster_at(team, edit.a), edit.b, edit.value, true, team)) return false;
            break;
        case 2: {
            const FM27TeamOption* selected = nullptr;
            for (const auto& o : fm27_team_options) if (o.group == edit.a && o.value == edit.value) selected = &o;
            if (!selected) return false;
            unsigned bit = ((unsigned (*)(unsigned))at(fn_option_bit))(edit.value);
            if (bit != selected->bit) return false;
            for (const auto& o : fm27_team_options) if (o.group == edit.a && o.bit) creator[edit.side][o.bit / 8] &= (unsigned char)~(1u << (o.bit % 8));
            if (bit) creator[edit.side][bit / 8] |= (unsigned char)(1u << (bit % 8));
            changed[edit.side] = true; instructions++; break;
        }
        case 60: {
            if (edit.a >= 128 || edit.value > 1) return false;
            for (auto o : fm27_team_options) if (o.bit && o.bit == edit.a) return false;
            creator[edit.side][edit.a / 8] = (creator[edit.side][edit.a / 8] & ~(1u << (edit.a % 8))) | (edit.value << (edit.a % 8));
            changed[edit.side] = true; break;
        }
        case 3: if (edit.value < 1 || edit.value > 7) return false; creator[edit.side][0x25] = (unsigned char)edit.value; changed[edit.side] = true; break;
        case 4: case 5: case 6: case 7: {
            auto cell = tactic_cell(manager, edit.a); if (!cell) return false;
            if (edit.kind == 4) {
                uint64_t role = ((uint64_t)edit.b << 32) | edit.value; bool valid = false;
                for (auto r : fm27_roles) if (r.phase == edit.a / 16 && r.value == role) valid = true;
                if (!valid) return false;
                *(uint64_t*)(cell + cell_role) = role | (*(uint64_t*)(cell + cell_role) & ~0xfffffffbf91fffffULL);
            } else if (edit.kind == 5) {
                bool valid = false; for (auto v : fm27_positions) if (v == edit.value) valid = true;
                if (!valid) return false; *(uint32_t*)cell = edit.value;
            } else if (edit.kind == 6) {
                bool valid = false; uint64_t mask = 0;
                for (auto o : fm27_player_options) if (o.group == edit.b) { if (o.value == edit.value) valid = true; if (o.value) mask |= 1ULL << o.value; }
                if (!valid) return false;
                if (game_constraints[edit.side] && edit.value) {
                    uint32_t status = 0, position = *(uint32_t*)cell; auto version = (uint32_t*)(manager + mg_version);
                    auto policy = (unsigned char (*)(unsigned, uint32_t*, uint64_t, uint32_t*, uint32_t*))at(edit.a / 16 ? fn_policy_oop : fn_policy_ip);
                    if (!policy(edit.value, &position, *(uint64_t*)(cell + cell_role), version, &status) || status != 0) return false;
                }
                auto entry = instruction_entry(cell, true); if (!entry) return false;
                entry[1] = (entry[1] & ~mask) | (edit.value ? 1ULL << edit.value : 0);
            } else {
                if (edit.b == 0) { if (edit.value != 255 && edit.value >= 26) return false; }
                else if (edit.b == 1) { bool valid = edit.value == 0; for (auto p : fm27_positions) if (p == edit.value) valid = true; if (!valid) return false; }
                else return false;
                auto entry = instruction_entry(cell, true); if (!entry) return false;
                if (edit.b == 0) ((unsigned char*)entry)[20] = (unsigned char)edit.value; else *(uint32_t*)((unsigned char*)entry + 16) = edit.value;
            }
            break;
        }
        case 14: {
            auto cell = tactic_cell(manager, edit.a); if (!cell) return false;
            uint64_t duty = ((uint64_t)edit.b << 32) | edit.value;
            if (duty != 0 && duty != 2097152 && duty != 4194304 && duty != 8388608 && duty != 33554432 && duty != 67108864 && duty != 17179869184ULL) return false;
            *(uint64_t*)(cell + cell_role) = (*(uint64_t*)(cell + cell_role) & 0xfffffffbf91fffffULL) | duty; break;
        }
        case 20: case 21: {
            if (!valid_oi(edit.value)) return false;
            if (edit.kind == 20) {
                if (edit.a >= team_of(match, 1 - edit.side)[t_count]) return false;
                set_oi(manager + mg_oi + edit.a * 3, edit.value);
            } else {
                bool valid = false; for (auto p : fm27_positions) if (p == edit.a) valid = true; if (!valid) return false;
                auto row = ((unsigned char* (*)(void*, uint32_t))at(fn_oi_row))(manager + mg_oi_pos_count, edit.a);
                if (!row) return false; set_oi(row, edit.value);
            }
            break;
        }
        case 46: if (edit.a > 2 || edit.value > 1) return false; manager[mg_throw_flags + edit.a] = (unsigned char)edit.value; break;
        case 13: if (edit.value > 1) return false; break;   // read in load_scenario
        case 12: if (edit.a >= 11 || edit.value >= 11) return false; manager[mg_map_live + edit.a] = (unsigned char)edit.value; break;
        case 11: if (edit.a >= 11 || edit.value >= team[t_count]) return false; break;
        case 10: {
            if (edit.value > 1) return false;
            auto flags = (uint32_t*)(manager + mg_input_flags); *flags = (*flags & ~1u) | edit.value; break;
        }
        case 30: {
            auto list = priority_list(manager, edit.a); if (!list) return false;
            if (edit.b == 0xffffffff) { *(void**)(list + 8) = *(void**)list; break; }
            if (edit.value >= team[t_count] || edit.b >= 26) return false;
            uint32_t key = person_key(original_roster[edit.side][edit.value]);
            if ((size_t)(*(uint32_t**)(list + 8) - *(uint32_t**)list) != edit.b) return false;
            ((void (*)(void*, uint32_t, const uint32_t*, char))at(fn_priority_insert))(list, 0xffffffff, &key, 1);
            break;
        }
        case 31:
            if (edit.value != 0xffffffff && edit.value >= team[t_count]) return false;
            *(uint32_t*)(manager + mg_captain_key) = edit.value == 0xffffffff ? 0x4e554c4c : person_key(original_roster[edit.side][edit.value]);
            break;
        case 40: {
            auto vec = routine_vector(manager, edit.a);
            if (!vec || edit.value < 1 || edit.value > 3) return false;
            auto begin = *(unsigned char***)vec, end = *(unsigned char***)(vec + 8);
            if (begin == end) return false;
            while ((size_t)(end - begin) > edit.value) { auto obj = *--end; *(void**)(vec + 8) = end; ((void (*)(void*))(*(void***)obj)[1])(obj); }
            while ((size_t)(end - begin) < edit.value) {
                auto src = begin[0]; size_t size = routine_size(edit.a);
                auto obj = (unsigned char*)pool_alloc(size); memset(obj, 0, size); *(void***)obj = *(void***)src;
                ((void* (*)(void*, void*))(*(void***)obj)[3])(obj, src);
                *(uint32_t*)(obj + 0x10) = 0x4e554c4c;
                pool_vector_append(vec, &obj, 8);
                begin = *(unsigned char***)vec; end = *(unsigned char***)(vec + 8);
            }
            break;
        }
        case 41: case 42: case 43: case 44: case 45: {
            auto obj = routine(manager, edit.a); if (!obj) return false; auto vt = *(void***)obj;
            if (edit.kind == 41) {
                if (edit.b == 0) { if (edit.value > 2) return false; obj[0x14] = (unsigned char)edit.value; }
                else if (edit.b == 1 || edit.b == 2) {
                    auto current = ((unsigned char (*)(void*))vt[19 + edit.b - 1])(obj);
                    bool recorded_strategy = edit.b == 1 && ((edit.a / 16 == 5 && edit.value == 3) || (edit.a / 16 == 7 && edit.value == 6) || (edit.a / 16 == 8 && edit.value == 3));
                    if (current == 255 || (edit.value > (edit.b == 2 ? 1u : 2u) && !recorded_strategy)) return false;
                    ((void (*)(void*, unsigned char))vt[21 + edit.b - 1])(obj, (unsigned char)edit.value);
                } else return false;
            } else if (edit.kind == 42) {
                if (edit.b) return false;
                for (unsigned g = 0; g < 8; g++) { auto entry = obj + 0x18 + g * 0x20; *(void**)(entry + 16) = *(void**)(entry + 8); }
                *(void**)(obj + 0x120) = *(void**)(obj + 0x118); *(void**)(obj + 0x138) = *(void**)(obj + 0x130);
            } else if (edit.kind == 43) {
                if (edit.b >= 8 || edit.value >= 16 || !((unsigned char (*)(unsigned, int))at(fn_task_valid))(edit.b, (int)(signed char)edit.value)) return false;
                ((void (*)(void*, unsigned, unsigned char, unsigned char, unsigned long))at(fn_task_set))(obj, edit.b, (unsigned char)edit.value, 0xff, 0);
            } else if (edit.kind == 44) {
                if (edit.value >= 8 || edit.b >= 4) return false;
                if ((size_t)(*(unsigned char**)(obj + 0x120) - *(unsigned char**)(obj + 0x118)) != edit.b) return false;
                unsigned char value = (unsigned char)edit.value; pool_vector_append(obj + 0x118, &value, 1);
            } else {
                unsigned g = edit.b / 32, index = edit.b % 32; if (g >= 8 || index >= 10 || edit.value >= 16) return false;
                bool found = false;
                for (auto p = *(unsigned char**)(obj + 0x130); p < *(unsigned char**)(obj + 0x138); p += 3) if (p[0] == g && p[1] == index) { found = true; break; }
                if (found) ((void (*)(void*, unsigned char, unsigned char, unsigned char))vt[13])(obj, g, index, edit.value);
                if (!found && edit.value) { unsigned char row[3] = {(unsigned char)g, (unsigned char)index, (unsigned char)edit.value}; pool_vector_append(obj + 0x130, row, 3); }
            }
            break;
        }
        case 47: { auto obj = routine(manager, edit.a); if (!obj || edit.value > 255) return false; obj[0x15] = (unsigned char)edit.value; break; }
        default: return not_ported(edit);
        }
    }
    for (unsigned side = 0; side < 2; side++) if (game_constraints[side]) {
        scenario_stage = "game_constraints";
        auto manager = manager_of(team_of(match, side));
        bool seen[11] = {};
        for (unsigned i = 0; i < 11; i++) { unsigned mapped = manager[mg_map_live + i]; if (mapped == 255) mapped = i; if (mapped >= 11 || seen[mapped]) return false; seen[mapped] = true; }
        uint64_t bits = 0; memcpy(&bits, creator[side], 8);
        if (((bits >> 25 & 1) && (bits & 0x70000000ULL)) || ((bits >> 26 & 1) && (bits & 0x30000000ULL)) || ((bits >> 27 & 1) && (bits & 0x50000000ULL))) return false;
        for (unsigned phase = 0; phase < 2; phase++) for (unsigned i = 0; i < 11; i++) {
            auto cell = tactic_cell(manager, phase * 16 + i); uint32_t position = *(uint32_t*)cell;
            uint64_t role = *(uint64_t*)(cell + cell_role) & 0xfffffffbf91fffffULL;
            unsigned count = 0, dm = 0;
            for (unsigned j = 0; j < 11; j++) { auto pos = *(uint32_t*)tactic_cell(manager, phase * 16 + j); if (pos & 16) count++; if (pos & 128) dm++; }
            auto allowed = ((uint64_t (*)(const uint32_t*, unsigned))at(phase ? fn_role_mask_oop : fn_role_mask_ip))(&position, count);
            if (phase && (position & 128) && dm == 1) allowed &= ~0x20000ULL;
            if (!role || (role & (role - 1)) || !(allowed & role)) {
                LOG("{\"event\":\"invalid_role_context\",\"side\":%u,\"phase\":%u,\"position\":%u,\"role\":\"%llu\",\"allowed\":\"%llu\"}", side, phase, position,
                    (unsigned long long)role, (unsigned long long)allowed);
                return false;
            }
        }
    }
    for (unsigned side = 0; side < 2; side++) {
        scenario_stage = "lineup";
        auto team = team_of(match, side); unsigned lineup[11]; bool requested = false, used[26] = {};
        for (unsigned i = 0; i < 11; i++) lineup[i] = i;
        for (auto e : scenario_edits) if (e.kind == 11 && e.side == side) { lineup[e.a] = e.value; requested = true; }
        if (requested) {
            for (auto i : lineup) { if (used[i]) return false; used[i] = true; }
            unsigned dest = 0;
            for (auto i : lineup) *(unsigned char**)(team + t_roster + 8 * dest++) = original_roster[side][i];
            for (unsigned i = 0; i < team[t_count]; i++) if (!used[i]) *(unsigned char**)(team + t_roster + 8 * dest++) = original_roster[side][i];
        }
    }
    for (unsigned side = 0; side < 2; side++) if (changed[side]) {
        auto manager = manager_of(team_of(match, side));
        for (uintptr_t offset : {mg_creator_live, mg_creator_mid, mg_creator_input}) {
            memcpy(manager + offset, creator[side], 16);
            manager[offset + 0x25] = creator[side][0x25];
        }
    }
    LOG("{\"event\":\"native_scenario_applied\",\"phase\":\"attributes_before_preparation\",\"records\":%zu,\"attributes\":%u,\"team_instructions\":%u}",
        scenario_edits.size(), attributes, instructions);
    return true;
}

static void log_phase_players(unsigned char* team, unsigned phase) {
    fputs("[", log_file);
    for (unsigned i = 0; i < 11; i++) {
        auto cell = roster_at(team, i) + (phase ? p_cell_oop : p_cell_ip);
        auto pi = instruction_entry(cell, false);
        fprintf(log_file, "%s{\"slot\":%u,\"position\":%u,\"role\":\"%llu\",\"instruction_flags\":\"%llu\"}", i ? "," : "", i, *(uint32_t*)cell,
                (unsigned long long)*(uint64_t*)(cell + cell_role), (unsigned long long)(pi ? pi[1] : 0));
    }
    fputs("]", log_file);
}

// Read back what native preparation actually installed. The opposition and player-binding checks compare the
// manager's input plans with engine-derived state, so they also validate the Mac layout itself.
static bool verify_scenario(unsigned char* match) {
    for (const auto& edit : scenario_edits) {
        auto team = team_of(match, edit.side); auto manager = manager_of(team);
        if (edit.kind == 1 && original_roster[edit.side][edit.a][p_attributes + edit.b] != edit.value) {
            LOG("{\"event\":\"scenario_attribute_readback\",\"side\":%u,\"slot\":%u,\"attribute\":%u,\"written\":%u,\"after_preparation\":%u}",
                edit.side, edit.a, edit.b, edit.value, original_roster[edit.side][edit.a][p_attributes + edit.b]);
            return false;
        }
        if (edit.kind == 17 && team[t_count] != edit.value) return false;
        if (edit.kind == 18) {
            auto entry = instruction_entry(tactic_cell(manager, edit.a), false); uint64_t expected = 0;
            for (auto s : scenario_edits) if (s.kind == 6 && s.side == edit.side && s.a == edit.a && s.value) expected |= 1ULL << s.value;
            if (!entry || entry[1] != expected) return false;
        }
        if (edit.kind == 15 && !profile_value(original_roster[edit.side][edit.a], edit.b, edit.value, false, team)) {
            LOG("{\"event\":\"profile_readback_mismatch\",\"side\":%u,\"player\":%u,\"field\":%u}", edit.side, edit.a, edit.b); return false;
        }
        if (edit.kind == 10 && ((*(uint32_t*)(manager + mg_input_flags) & 1) != edit.value)) return false;
        if (edit.kind == 14) for (bool canonical : {false, true}) {
            auto cell = tactic_cell(manager, edit.a, canonical);
            if ((*(uint64_t*)(cell + cell_role) & ~0xfffffffbf91fffffULL) != (((uint64_t)edit.b << 32) | edit.value)) return false;
        }
        if (edit.kind == 20 && packed_oi(manager + mg_oi + edit.a * 3) != edit.value) return false;
        if (edit.kind == 21) {
            bool found = false;
            for (unsigned i = 0; i < manager[mg_oi_pos_count]; i++) { auto row = manager + mg_oi_pos_rows + i * 8; if (*(uint32_t*)row == edit.a && packed_oi(row + 4) == edit.value) found = true; }
            if (!found) return false;
        }
        if (edit.kind == 46) {
            if (manager[mg_throw_flags + edit.a] != edit.value) return false;
            uint32_t expected = edit.a == 2 ? (edit.value ? 0x54464c4f : 0x54465348) : (edit.value ? 0x544f574c : 0x544f5242);
            auto actual = ((uint32_t (*)(void*, unsigned char, unsigned char, size_t))at(fn_throw_preset))(manager + mg_routines, 9, edit.a, 0);
            if (actual != expected) return false;
            LOG("{\"event\":\"native_throw_strategy_verified\",\"side\":%u,\"zone\":%u,\"preset\":%u}", edit.side, edit.a, actual);
        }
        if (edit.kind == 40) { auto vec = routine_vector(manager, edit.a); if (!vec || (size_t)(*(void***)(vec + 8) - *(void***)vec) != edit.value) return false; }
        if (edit.kind >= 41 && edit.kind <= 45) {
            auto obj = routine(manager, edit.a); if (!obj) return false; auto vt = *(void***)obj;
            if (edit.kind == 41) { unsigned actual = edit.b == 0 ? obj[0x14] : ((unsigned char (*)(void*))vt[19 + edit.b - 1])(obj); if (actual != edit.value) return false; }
            if (edit.kind == 42) {
                unsigned total = 0;
                for (unsigned g = 0; g < 8; g++) {
                    std::vector<unsigned char> expected;
                    for (auto e : scenario_edits) if (e.kind == 43 && e.side == edit.side && e.a == edit.a && e.b == g) expected.push_back((unsigned char)e.value);
                    unsigned char* group = nullptr; for (unsigned j = 0; j < 8; j++) if (obj[0x18 + j * 0x20] == g) group = obj + 0x18 + j * 0x20;
                    if (!group) return false;
                    auto begin = *(unsigned char**)(group + 8), end = *(unsigned char**)(group + 16);
                    if ((size_t)(end - begin) != expected.size() || !std::equal(expected.begin(), expected.end(), begin)) return false;
                    total += (unsigned)expected.size();
                    if (((unsigned (*)(void*, unsigned char))vt[15])(obj, (unsigned char)g) != expected.size()) return false;
                }
                std::vector<unsigned char> expected;
                for (auto e : scenario_edits) if (e.kind == 44 && e.side == edit.side && e.a == edit.a) expected.push_back((unsigned char)e.value);
                auto begin = *(unsigned char**)(obj + 0x118), end = *(unsigned char**)(obj + 0x120);
                if ((size_t)(end - begin) != expected.size() || !std::equal(expected.begin(), expected.end(), begin)) return false;
                LOG("{\"event\":\"native_setpiece_routine_verified\",\"side\":%u,\"type\":%u,\"variant\":%u,\"assignments\":%u}", edit.side, edit.a / 16, edit.a % 16, total);
            }
            if (edit.kind == 45) {
                unsigned value = 0;
                for (auto p = *(unsigned char**)(obj + 0x130); p < *(unsigned char**)(obj + 0x138); p += 3) if (p[0] == edit.b / 32 && p[1] == edit.b % 32) { value = p[2]; break; }
                if (value != edit.value) return false;
            }
        }
        if (edit.kind == 47) { auto obj = routine(manager, edit.a); if (!obj || obj[0x15] != edit.value) return false; }
        if (edit.kind == 30) {
            auto list = priority_list(manager, edit.a); if (!list) return false;
            auto begin = *(uint32_t**)list, end = *(uint32_t**)(list + 8);
            if (edit.b != 0xffffffff && ((size_t)(end - begin) <= edit.b || begin[edit.b] != person_key(original_roster[edit.side][edit.value]))) return false;
            if (edit.b == 0xffffffff) {
                unsigned expected = 0;
                for (auto e : scenario_edits) if (e.kind == 30 && e.side == edit.side && e.a == edit.a && e.b != 0xffffffff) expected++;
                if ((size_t)(end - begin) != expected) return false;
                LOG("{\"event\":\"native_priority_list_verified\",\"side\":%u,\"list\":%u,\"count\":%u}", edit.side, edit.a, expected);
            }
        }
        if (edit.kind == 31 && edit.value != 0xffffffff) {
            unsigned slot = manager[mg_captain_slot];
            if (slot >= 11 || roster_at(team, slot) != original_roster[edit.side][edit.value]) return false;
            LOG("{\"event\":\"native_captain_verified\",\"side\":%u,\"player_slot\":%u,\"person_key\":%u}", edit.side, slot, person_key(original_roster[edit.side][edit.value]));
        }
        if (edit.kind == 11 && roster_at(team, edit.a) != original_roster[edit.side][edit.value]) return false;
        if (edit.kind == 12) for (uintptr_t map : {mg_map_live, mg_map_canon}) {
            auto mapped = manager[map + edit.a]; if ((mapped == 255 ? edit.a : mapped) != edit.value) return false;
        }
        if (edit.kind >= 4 && edit.kind <= 7) for (bool canonical : {false, true}) {
            auto cell = tactic_cell(manager, edit.a, canonical);
            if (edit.kind == 4 && (*(uint64_t*)(cell + cell_role) & 0xfffffffbf91fffffULL) != (((uint64_t)edit.b << 32) | edit.value)) return false;
            if (edit.kind == 5 && *(uint32_t*)cell != edit.value) return false;
            if (edit.kind == 6) {
                auto entry = instruction_entry(cell, false); if (!entry) return false;
                for (auto o : fm27_player_options) if (o.group == edit.b && o.value && bool(entry[1] & (1ULL << o.value)) != (o.value == edit.value)) return false;
            }
            if (edit.kind == 7) {
                auto e = instruction_entry(cell, false); if (!e) return false;
                if (edit.b == 0 && ((unsigned char*)e)[20] != edit.value) return false;
                if (edit.b == 1 && *(uint32_t*)((unsigned char*)e + 16) != edit.value) return false;
            }
        }
        if (edit.kind == 60) for (uintptr_t offset : {mg_creator_live, mg_creator_input})
            if (((manager[offset + edit.a / 8] >> (edit.a % 8)) & 1) != edit.value) return false;
        if (edit.kind == 2) {
            unsigned bit = ((unsigned (*)(unsigned))at(fn_option_bit))(edit.value);
            for (const auto& o : fm27_team_options) if (o.group == edit.a && o.bit) {
                bool value = (manager[mg_creator_input + o.bit / 8] >> (o.bit % 8)) & 1;
                bool active = (manager[mg_creator_live + o.bit / 8] >> (o.bit % 8)) & 1;
                if (value != (o.bit == bit) || active != value) {
                    LOG("{\"event\":\"scenario_bit_mismatch\",\"bit\":%u,\"canonical\":%s,\"active\":%s,\"expected\":%s}", o.bit, value ? "true" : "false",
                        active ? "true" : "false", o.bit == bit ? "true" : "false");
                    return false;
                }
            }
        }
        if (edit.kind == 3 && manager[mg_creator_input + 0x25] != edit.value) return false;
    }
    unsigned oi_checks = 0;
    for (unsigned side = 0; side < 2; side++) {
        auto own = team_of(match, side), other = team_of(match, 1 - side); auto manager = manager_of(own);
        for (unsigned i = 0; i < 11; i++) {
            auto player = roster_at(other, i); uint32_t position = *(uint32_t*)(player + p_cell_ip);
            uint32_t got = ((uint32_t (*)(void*, long, uint32_t*))at(fn_effective_oi))(manager + mg_oi, (long)i, &position) & 0xffffff;
            auto expected = manager + mg_oi + i * 3; unsigned char fallback[3] = {0, 0, 8};
            if (!(expected[2] & 8)) {
                expected = fallback;
                for (unsigned j = 0; j < manager[mg_oi_pos_count]; j++) { auto row = manager + mg_oi_pos_rows + j * 8; if (*(uint32_t*)row == position) { expected = row + 4; break; } }
            }
            if (got != packed_oi(expected)) {
                LOG("{\"event\":\"opposition_effective_mismatch\",\"side\":%u,\"slot\":%u,\"engine\":%u,\"expected\":%u}", side, i, got, packed_oi(expected));
                return false;
            }
            oi_checks++;
        }
    }
    LOG("{\"event\":\"native_opposition_effective_verified\",\"players\":%u}", oi_checks);
    for (unsigned side = 0; side < 2; side++) {
        auto team = team_of(match, side); auto manager = manager_of(team);
        for (unsigned i = 0; i < 11; i++) {
            auto player = roster_at(team, i); unsigned mapped = manager[mg_map_live + i]; if (mapped == 255) mapped = i;
            if (mapped >= 11) return false;
            for (unsigned phase = 0; phase < 2; phase++) {
                auto input = tactic_cell(manager, phase * 16 + (phase ? mapped : i)); auto actual = player + (phase ? p_cell_oop : p_cell_ip);
                if (*(uint32_t*)input != *(uint32_t*)actual ||
                    (*(uint64_t*)(input + cell_role) & 0xfffffffbf91fffffULL) != (*(uint64_t*)(actual + cell_role) & 0xfffffffbf91fffffULL)) {
                    LOG("{\"event\":\"player_tactic_binding_mismatch\",\"side\":%u,\"player_slot\":%u,\"phase\":%u,\"input_position\":%u,\"actual_position\":%u}",
                        side, i, phase, *(uint32_t*)input, *(uint32_t*)actual);
                    return false;
                }
                auto src = instruction_entry(input, false), dst = instruction_entry(actual, false);
                if (bool(src) != bool(dst)) return false;
                if (src && (src[1] != dst[1] || *(uint32_t*)((unsigned char*)src + 16) != *(uint32_t*)((unsigned char*)dst + 16) ||
                            ((unsigned char*)src)[20] != ((unsigned char*)dst)[20])) return false;
            }
        }
    }
    for (unsigned side = 0; side < 2; side++) for (unsigned phase = 0; phase < 2; phase++) {
        auto team = team_of(match, side); auto manager = manager_of(team); uint64_t lo = 0, hi = 0;
        for (auto g : fm27_team_instruction_phases) if (g.phase == phase)
            for (auto o : fm27_team_options) if (o.group == g.group && o.bit && (manager[mg_creator_live + o.bit / 8] >> (o.bit % 8) & 1)) {
                if (o.bit < 64) lo |= 1ULL << o.bit; else hi |= 1ULL << (o.bit - 64);
            }
        fprintf(log_file, "{\"event\":\"native_phase_configuration\",\"side\":%u,\"phase\":%u,\"team_flags_low\":\"%llu\",\"team_flags_high\":\"%llu\",\"players\":",
                side, phase, (unsigned long long)lo, (unsigned long long)hi);
        log_phase_players(team, phase); fputs("}\n", log_file);
    }
    unsigned profile_fields = 0; for (auto e : scenario_edits) if (e.kind == 15) profile_fields++;
    LOG("{\"event\":\"native_profile_bindings_verified\",\"fields\":%u}", profile_fields);
    LOG("{\"event\":\"native_player_tactic_bindings_verified\",\"players\":22,\"phases\":2}");
    LOG("{\"event\":\"native_scenario_readback_verified\",\"records\":%zu,\"after_original_preparation\":true}", scenario_edits.size());
    return true;
}
