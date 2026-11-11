// Match-input snapshot (--dump-input PATH, --inspect-fixture): Mac counterpart of the Windows host's dump_match_input.
//
// Written in the Windows snapshot format the server reads (editor_manual_default.json / editor_advanced_snapshot.json /
// editor_setpieces_default.json), so that any saved .pkm can be the base of the scenario editor. Windows-layout fields
// that the server reads from raw bytes are re-assembled from the Mac offsets:
//   header_hex (team +0..0x138): Mac team bytes, +8 from 0x80 (t_roster 0x140 <-> 0x138, t_adjustment 0x129 <-> 0x121);
//   manager_tactical_hex (Windows manager +0x2e0..+0x2f10): only the mapped blocks are filled (throw styles 0x16f0,
//   opposition 0x16f8, positional opposition 0x1748/0x174c, OOP map 0x1fb4, creator 0x2848); the rest is zero.
// Taken before preparation, after any scenario edits: the state the editor's edits act on. Players are listed in input
// roster order (the slot numbers scenario edits use), with name and the profile fields of scenario kind 15.
// Extra fields (not in the Windows dump): oop_map, players[].name, players[].profile, match.
#pragma once

static std::string dump_input_path;
static bool inspect_fixture_only = false;

static bool profile_read(unsigned char* player, unsigned field, unsigned char* team, double* out) {
    if (field == 0) { float h; memcpy(&h, player + p_height, 4); *out = h * 100.0; return true; }
    unsigned offset = 0, size = 0;
    if (field == 1) { offset = p_age; size = 1; }
    else if (field >= 2 && field <= 8) { offset = p_field2 + field - 2; size = 1; }
    else if (field == 9 || field == 10) { offset = 0xbb0 + 4 * (field - 9); size = 4; }
    else if (field >= 11 && field <= 18) { static const unsigned o[] = {0xc90, 0xc84, 0xc8e, 0xc70, 0xc82, 0xc88, 0xc72, 0xc7c}; offset = o[field - 11]; size = 2; }
    else if (field == 19) { offset = p_field19; size = 1; }
    else if (field == 20 || field == 21) { offset = field == 20 ? 0xca0 : 0xc9a; size = 1; }
    else if (field == 22) { offset = 0xc9b; size = 1; }
    else return false;
    uint32_t v = 0; memcpy(&v, player + offset, size);
    *out = field == 20 ? (v + 50 + 5 * (int)(signed char)team[t_adjustment]) / 2.0 : v;   // stored input -> editor value
    return true;
}

static void dump_match_input(unsigned char* match) {
    if (dump_input_path.empty()) return;
    FILE* f = fopen(dump_input_path.c_str(), "w"); if (!f) finish(105);
    auto hex = [&](const void* p, size_t n) { fputc('"', f); for (size_t i = 0; i < n; i++) fprintf(f, "%02x", ((const unsigned char*)p)[i]); fputc('"', f); };
    auto string = [&](const unsigned char* s) {   // engine string {u32 len, utf8}
        fputc('"', f);
        uint32_t n = 0; if (s && safe_copy(s, &n, 4) && n < 256) {
            std::vector<unsigned char> b(n); if (safe_copy(s + 4, b.data(), n)) for (auto c : b) { if (c == '"' || c == '\\') fputc('\\', f); if (c >= 0x20) fputc(c, f); }
        }
        fputc('"', f);
    };
    fprintf(f, "{\"format\":\"fm27-mac-input-v1\",\"match\":{\"seed\":%u,\"engine_version\":%u},\"objects\":[],\"teams\":[",
            *(uint32_t*)(match + m_seed), *(uint32_t*)(match + m_engine_version));
    for (unsigned side = 0; side < 2; side++) {
        auto team = team_of(match, side); auto manager = manager_of(team);
        unsigned count = team[t_count]; if (count > 26) finish(106);
        unsigned char header[0x138]; memcpy(header, team, 0x80); memcpy(header + 0x80, team + 0x88, 0xb8);
        fprintf(f, "%s{\"side\":%u,\"count\":%u,\"header_hex\":", side ? "," : "", side, count); hex(header, sizeof header);
        fputs(",\"creator_hex\":", f); hex(manager + mg_creator_live, 0x28);
        fprintf(f, ",\"manager_input_flags\":%u", *(uint32_t*)(manager + mg_input_flags));
        std::vector<unsigned char> tactical(0x2c30, 0);
        auto put = [&](unsigned windows, const unsigned char* mac, size_t n) { memcpy(tactical.data() + windows - 0x2e0, mac, n); };
        put(0x16f0, manager + mg_throw_flags, 3);
        put(0x16f8, manager + mg_oi, 26 * 3);
        put(0x1748, manager + mg_oi_pos_count, 4);
        unsigned positional = manager[mg_oi_pos_count]; if (positional > 64) finish(106);
        put(0x174c, manager + mg_oi_pos_rows, positional * 8);
        put(0x1fb4, manager + mg_map_live, 11);
        put(0x2848, manager + mg_creator_live, 0x28);
        fputs(",\"manager_tactical_hex\":", f); hex(tactical.data(), tactical.size());
        fputs(",\"oop_map\":[", f);
        for (unsigned i = 0; i < 11; i++) fprintf(f, "%s%u", i ? "," : "", manager[mg_map_live + i]);
        fputs("],\"tactical_slots\":[", f);
        for (unsigned phase = 0; phase < 2; phase++) {
            fputs(phase ? ",[" : "[", f);
            for (unsigned slot = 0; slot < 11; slot++) {
                unsigned char cell[0x48]; memcpy(cell, tactic_cell(manager, phase * 16 + slot), 0x48);
                memset(cell + 8, 0, 24);   // instruction-map vector pointers: process addresses, not data
                if (slot) fputc(',', f); hex(cell, 0x48);
            }
            fputc(']', f);
        }
        fputs("],\"opposition\":[", f);
        for (unsigned i = 0; i < 26; i++) fprintf(f, "%s%u", i ? "," : "", packed_oi(manager + mg_oi + i * 3));
        fputs("],\"opposition_positions\":[", f);
        for (unsigned i = 0; i < positional; i++) {
            auto e = manager + mg_oi_pos_rows + i * 8;
            fprintf(f, "%s{\"position\":%u,\"packed\":%u}", i ? "," : "", *(uint32_t*)e, packed_oi(e + 4));
        }
        fputs("],\"taker_lists\":[],\"routine_objects\":[],\"routine_variants\":[", f);
        for (unsigned group = 0; group < 10; group++) {
            auto vec = manager + mg_routines + 0xd00 + 24 * group;
            auto begin = *(unsigned char***)vec, end = *(unsigned char***)(vec + 8);
            if (end - begin > 8) finish(106);
            fprintf(f, "%s[", group ? "," : "");
            for (auto ptr = begin; ptr < end; ptr++) {
                auto obj = *ptr; auto vt = *(void***)obj;
                fprintf(f, "%s{\"type\":%u,\"frequency\":%u,\"strategy\":%u,\"swing\":%u,\"opaque_flags\":%u,\"groups\":[", ptr == begin ? "" : ",",
                        ((unsigned char (*)(void*))vt[7])(obj), obj[0x14], ((unsigned char (*)(void*))vt[19])(obj), ((unsigned char (*)(void*))vt[20])(obj), obj[0x15]);
                for (unsigned j = 0; j < 8; j++) {
                    auto entry = obj + 0x18 + j * 0x20; auto a = *(unsigned char**)(entry + 8), b = *(unsigned char**)(entry + 16);
                    fprintf(f, "%s{\"id\":%u,\"values\":[", j ? "," : "", *entry);
                    for (auto p = a; p < b; p++) fprintf(f, "%s%u", p == a ? "" : ",", *p);
                    fputs("]}", f);
                }
                fputs("],\"priority\":[", f);
                for (auto p = *(unsigned char**)(obj + 0x118); p < *(unsigned char**)(obj + 0x120); p++) fprintf(f, "%s%u", p == *(unsigned char**)(obj + 0x118) ? "" : ",", *p);
                fputs("],\"backups\":[", f);
                for (auto p = *(unsigned char**)(obj + 0x130); p < *(unsigned char**)(obj + 0x138); p += 3) fprintf(f, "%s[%u,%u,%u]", p == *(unsigned char**)(obj + 0x130) ? "" : ",", p[0], p[1], p[2]);
                fputs("]}", f);
            }
            fputc(']', f);
        }
        fputs("],\"personal_instructions\":[", f);
        for (unsigned phase = 0; phase < 2; phase++) {
            fputs(phase ? ",[" : "[", f);
            for (unsigned slot = 0; slot < 11; slot++) {
                auto e = instruction_entry(tactic_cell(manager, phase * 16 + slot), false);
                fprintf(f, "%s{\"flags\":\"%llu\",\"target_position\":%u,\"target_player\":%u}", slot ? "," : "", e ? (unsigned long long)e[1] : 0ULL,
                        e ? *(uint32_t*)((unsigned char*)e + 16) : 0, e ? ((unsigned char*)e)[20] : 255);
            }
            fputc(']', f);
        }
        fputs("],\"instructions\":[],\"players\":[", f);
        for (unsigned i = 0; i < count; i++) {
            auto player = original_roster[side][i] ? original_roster[side][i] : roster_at(team, i);
            fprintf(f, "%s{\"index\":%u,\"id\":%u,\"person_key\":%u,\"on_pitch\":%u,\"name\":", i ? "," : "", i, *(uint32_t*)(player + 0x48), person_key(player), player[p_on_pitch]);
            string(*(unsigned char**)(player + 0x28));
            fputs(",\"attributes\":[", f);
            for (unsigned a = 0; a < 69; a++) fprintf(f, "%s%u", a ? "," : "", player[p_attributes + a]);
            fputs("],\"profile\":[", f);
            for (unsigned field = 0; field <= 22; field++) { double v = 0; profile_read(player, field, team, &v); fprintf(f, "%s%.6g", field ? "," : "", v); }
            fputs("]}", f);
        }
        fputs("]}", f);
    }
    fputs("]}\n", f);
    if (fclose(f)) finish(105);
    LOG("{\"event\":\"native_match_input_dumped\",\"stage\":\"before_preparation\"}");
}
