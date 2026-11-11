// FMF tactic import for the macOS host: the Mac twin of native/native_fmf_probe.h + native/native_tactic_import.h.
// The user's archive is opened by the game's own archive driver and the TAC plan is parsed by the game's own
// parser into the live manager plan; nothing here interprets the TAC format beyond upstream's header checks.
// Archive layout (runtime-dumped on Mac, identical to Windows): folder+0x30 -> vector of directories,
// folder+0x38 -> vector of file nodes; directory+0x38 -> vector of files; node+0x18 title, node+0x38 size.
#pragma once

static std::vector<unsigned char> fmf_payload;
static std::string fmf_tactic_name;
static int fmf_routine_type = -1;
static unsigned fmf_stream_revision = 0;

// Windows node vtable[21](node,&raw,0) (MSVC hidden return) -> Mac vtable[22](&raw,node,0).
static void* fmf_open_raw(unsigned char* node) {
    void* raw = nullptr;
    ((void* (*)(void*, void*, void*))(*(void***)node)[vslot_node_open_raw])(&raw, node, nullptr);
    return raw;
}
// Windows stream vtable[5](s,buf,n) -> Mac vtable[6].
static void fmf_read(void* stream, void* out, size_t n) {
    ((void* (*)(void*, void*, size_t))(*(void***)stream)[vslot_stream_read])(stream, out, n);
}
template <class F> static void fmf_each(uintptr_t* vec, size_t limit, F f) {
    if (!vec) return;
    auto first = (unsigned char**)vec[0], last = (unsigned char**)vec[1];
    if (last < first) return;
    for (auto p = first; p < last && (size_t)(p - first) < limit; p++) f(*p);
}

static void fmf_probe(unsigned char* resources) {
    const char* path = getenv("FM27_IMPORT_FMF");
    if (!path || !*path) return;
    EngineString name;
    ((void* (*)(void*, const char*, int))at(fn_string_from_c))(&name, path, -1);
    void* file = nullptr; void* folder_object = nullptr;
    ((void* (*)(void*, void*, void*))at(fn_file_open))(&file, &name, resources + res_filesystem);
    ((void* (*)(void*, void*, uintptr_t))at(fn_folder_open))(&folder_object, &file, *at<uintptr_t*>(g_folder_key));
    auto folder = (unsigned char*)folder_object;
    if (getenv("FM27_FMF_AUDIT")) LOG("{\"event\":\"native_fmf_archive_open\",\"folder\":%s}", folder ? "true" : "false");
    if (folder) {
        // Set-piece routine archives carry a "details" entry naming their routine handler.
        static const char* handlers[] = {"DEFEND_CORNER_ROUTINE_TYPE_HANDLER", "DEFEND_FREE_KICK_ROUTINE_TYPE_HANDLER",
            "DEFEND_ID_WIDE_FREE_KICK_ROUTINE_TYPE_HANDLER", "DEFEND_ID_DEEP_FREE_KICK_ROUTINE_TYPE_HANDLER",
            "DEFEND_LONG_THROW_IN_ROUTINE_TYPE_HANDLER", "ATTACK_CORNER_ROUTINE_TYPE_HANDLER", "ATTACK_FREE_KICK_ROUTINE_TYPE_HANDLER",
            "ATTACK_ID_WIDE_FREE_KICK_ROUTINE_TYPE_HANDLER", "ATTACK_ID_DEEP_FREE_KICK_ROUTINE_TYPE_HANDLER", "THROW_IN_ROUTINE_TYPE_HANDLER"};
        fmf_each(*(uintptr_t**)(folder + fmf_folder_dirs), 16, [&](unsigned char* dir) {
            fmf_each(*(uintptr_t**)(dir + fmf_folder_files), 16, [&](unsigned char* f) {
                auto title = *(unsigned**)(f + fmf_node_title);
                if (!title || *title != 7 || memcmp(title + 1, "details", 7)) return;
                auto size = *(uint64_t*)(f + fmf_node_size);
                if (size < 12 || size > 65536) return;
                void* raw = fmf_open_raw(f);
                if (!raw) return;
                std::vector<unsigned char> bytes(size);
                fmf_read(raw, bytes.data(), size);
                unsigned n = *(unsigned*)(bytes.data() + 8);
                if (n > 100 || n > size - 12) return;
                std::string handler((char*)bytes.data() + 12, n);
                if (getenv("FM27_FMF_AUDIT")) LOG("{\"event\":\"native_fmf_details\",\"handler\":\"%s\"}", handler.c_str());
                for (int j = 0; j < 10; j++) if (handler == handlers[j]) fmf_routine_type = j;
            });
        });
        bool routine_done = false;
        auto children = *(uintptr_t**)(folder + fmf_folder_files);
        size_t count = children ? (children[1] - children[0]) / 8 : 0;
        if (getenv("FM27_FMF_AUDIT")) LOG("{\"event\":\"native_fmf_children\",\"count\":%zu}", count);
        if (count <= 64) fmf_each(children, 64, [&](unsigned char* node) {
            uint64_t size = *(uint64_t*)(node + fmf_node_size);
            if (getenv("FM27_FMF_AUDIT")) LOG("{\"event\":\"native_fmf_entry_size\",\"size\":%llu}", (unsigned long long)size);
            if (size < 8 || size > 1024 * 1024) return;
            auto title = *(unsigned**)(node + fmf_node_title);
            void* entry_file = node; void* stream = nullptr; void* extra = nullptr;
            struct Ret16 { uint64_t a, b; };
            ((Ret16 (*)(void*, void*, uintptr_t, void*))at(fn_reader_factory))(&stream, &entry_file, 0, &extra);
            if (!stream) return;
            // The native adapter has consumed the eight-byte standalone TAC stream header.
            std::vector<unsigned char> bytes((size_t)size - 8);
            if (bytes.size() < 8) return;
            fmf_read(stream, bytes.data(), bytes.size());
            if (fmf_routine_type >= 0) {   // set-piece routine: the payload is this entry's stream (revision 60)
                if (routine_done || !title || (*title == 5 && !memcmp(title + 1, "image", 5))) return;
                void* raw = fmf_open_raw(node);
                unsigned char header[8] = {};
                if (!raw) return;
                fmf_read(raw, header, 8);
                fmf_stream_revision = *(unsigned short*)(header + 6);
                if (fmf_stream_revision != 60) return;
                fmf_tactic_name.assign((char*)(title + 1), *title);
                fmf_payload = std::move(bytes); routine_done = true;
                return;
            }
            if (getenv("FM27_FMF_AUDIT")) LOG("{\"event\":\"native_fmf_entry\",\"size\":%llu,\"prefix\":\"%02x%02x%02x%02x\"}",
                                              (unsigned long long)size, bytes[0], bytes[1], bytes[2], bytes[3]);
            // TAC plan marker, supported plan revision, FM27 engine major.
            unsigned short revision = (unsigned short)(bytes[1] | bytes[2] << 8);
            if (bytes[0] != 0x22 || revision < 60 || revision > 68 || bytes[3] != 27) return;
            if (!fmf_payload.empty()) { LOG("{\"event\":\"native_fmf_error\",\"reason\":\"multiple_tactic_entries\"}"); finish(171); }
            if (title && *title < 4096) fmf_tactic_name.assign((char*)(title + 1), *title);
            fmf_payload = std::move(bytes);
        });
    }
    fprintf(log_file, "{\"event\":\"native_fmf_decoded\",\"accepted\":%s,\"bytes\":%llu,\"name_utf8_hex\":\"",
            fmf_payload.empty() ? "false" : "true", (unsigned long long)fmf_payload.size());
    for (unsigned char c : fmf_tactic_name) fprintf(log_file, "%02x", c);
    fprintf(log_file, "\",\"setpiece_type\":%d,\"stream_revision\":%u}\n", fmf_routine_type, fmf_stream_revision);
    fflush(log_file);
    if (fmf_payload.empty()) finish(171);
}

// The original TAC plan parser consumes a bounded, read-only memory stream.
// Mac stream vtable (Itanium, two destructor slots): [3] tell() -> pos, [4] seek(pos) -> 8-byte result in RAX,
// [6] read(out, n) -> self; the parser checks the int error flag at +0x10 (same as Windows).
struct MacTacticStream { void** methods; uint64_t reserved; uint32_t error, padding; const unsigned char* data; size_t size, cursor; };
static void* mac_tac_read(void* self, void* output, size_t n) {
    auto s = (MacTacticStream*)self;
    if (n > s->size || s->cursor > s->size - n) { s->error = 1; return self; }
    memcpy(output, s->data + s->cursor, n); s->cursor += n; return self;
}
static uint64_t mac_tac_tell(void* self) { return ((MacTacticStream*)self)->cursor; }
static uint64_t mac_tac_seek(void* self, uint64_t position) {
    auto s = (MacTacticStream*)self;
    if (position > s->size) s->error = 1; else s->cursor = (size_t)position;
    return 0;
}

static void import_tac(unsigned char* match) {
    if (fmf_routine_type >= 0) return;
    const char* direct = getenv("FM27_IMPORT_TAC");
    if ((!direct || !*direct) && fmf_payload.empty()) return;
    std::vector<unsigned char> bytes = fmf_payload;
    if (direct && *direct) { std::ifstream file(direct, std::ios::binary); bytes.assign((std::istreambuf_iterator<char>(file)), {}); }
    if (bytes.size() < 8 || bytes.size() > 1024 * 1024) finish(172);
    void* methods[8] = {};
    methods[vslot_stream_tell] = (void*)mac_tac_tell; methods[vslot_stream_seek] = (void*)mac_tac_seek; methods[vslot_stream_read] = (void*)mac_tac_read;
    MacTacticStream reader = {methods, 0, 0, 0, bytes.data(), bytes.size(), 0};
    void* reference = &reader;
    auto manager = manager_of(team_of(match, 0));
    auto accepted = ((unsigned char (*)(void*, void**, unsigned))at(fn_tac_parse))(manager + mg_plan, &reference, 1);
    fprintf(log_file, "{\"event\":\"native_tactic_file_parsed\",\"accepted\":%s,\"stream_error\":%u,\"consumed\":%llu,\"size\":%llu,\"mentality\":%u,\"team_bits\":\"",
            accepted ? "true" : "false", reader.error, (unsigned long long)reader.cursor, (unsigned long long)reader.size, manager[mg_creator_live + 0x25]);
    for (unsigned j = 0; j < 16; j++) fprintf(log_file, "%02x", manager[mg_creator_live + j]);
    fputs("\",\"mapping\":[", log_file);
    for (unsigned j = 0; j < 11; j++) fprintf(log_file, "%s%u", j ? "," : "", manager[mg_map_live + j]);
    fputs("],\"phases\":[", log_file);
    for (unsigned phase = 0; phase < 2; phase++) {
        fprintf(log_file, "%s[", phase ? "," : "");
        for (unsigned i = 0; i < 11; i++) {
            auto cell = manager + mg_cells_live + (phase ? cell_oop_offset : cell_ip_offset) + i * cell_stride;
            auto pi = instruction_entry(cell, false);
            fprintf(log_file, "%s{\"position\":%u,\"role_flags\":\"%llu\",\"pi_flags\":\"%llu\",\"target_player\":%u,\"target_position\":%u}",
                    i ? "," : "", *(unsigned*)cell, (unsigned long long)*(uint64_t*)(cell + cell_role),
                    pi ? (unsigned long long)pi[1] : 0, pi ? ((unsigned char*)pi)[20] : 255, pi ? *(uint32_t*)((unsigned char*)pi + 16) : 0);
        }
        fputs("]", log_file);
    }
    fputs("]}\n", log_file); fflush(log_file);
    bool tail = reader.cursor == reader.size ||
                (reader.size - reader.cursor == 8 && std::all_of(bytes.begin() + reader.cursor, bytes.end(), [](unsigned char c) { return c == 0; }));
    finish(accepted && !reader.error && tail ? 0 : 173);
}

// Original FM27 tactical-plan writer (Windows 0x49a9ab0 <-> Mac 0x507c550, 15/15 caller votes; decompiled pair: same
// field order, title string at plan+0x790 = Windows +0x778), with a bounded output stream (write = vtable slot 6).
struct MacTacticWriter { void** methods; uint64_t reserved; uint32_t error, padding; std::vector<unsigned char>* data; size_t cursor; };
static void* mac_tac_write(void* self, void* source, size_t n) {
    auto w = (MacTacticWriter*)self;
    if (n > 4 * 1024 * 1024 || w->cursor > 4 * 1024 * 1024 - n) { w->error = 1; return self; }
    if (w->data->size() < w->cursor + n) w->data->resize(w->cursor + n);
    memcpy(w->data->data() + w->cursor, source, n); w->cursor += n; return self;
}
static uint64_t mac_write_tell(void* self) { return ((MacTacticWriter*)self)->cursor; }
static uint64_t mac_write_seek(void* self, uint64_t position) {
    auto w = (MacTacticWriter*)self;
    if (position > 4 * 1024 * 1024) w->error = 1; else w->cursor = (size_t)position;
    return 0;
}
static void export_tac(unsigned char* match) {
    const char* path = getenv("FM27_EXPORT_TAC");
    if (!path || !*path) return;
    const char* side_text = getenv("FM27_EXPORT_SIDE");
    unsigned side = side_text ? (unsigned)strtoul(side_text, nullptr, 10) : 0;
    if (side > 1) finish(174);
    auto plan = manager_of(team_of(match, side)) + mg_plan;
    if (const char* title = getenv("FM27_EXPORT_TITLE"))
        ((void* (*)(void*, const char*, int))at(fn_string_from_c))(plan + plan_title, title, -1);
    std::vector<unsigned char> bytes;
    void* methods[8] = {};
    methods[vslot_stream_tell] = (void*)mac_write_tell; methods[vslot_stream_seek] = (void*)mac_write_seek; methods[vslot_stream_read] = (void*)mac_tac_write;
    MacTacticWriter writer = {methods, 0, 0, 0, &bytes, 0};
    void* reference = &writer;
    unsigned char accepted = ((unsigned char (*)(void*, void**, unsigned))at(fn_tac_write))(plan, &reference, 1);
    if (accepted && !writer.error) {
        std::ofstream file(path, std::ios::binary);
        file.write((char*)bytes.data(), bytes.size()); file.flush();
        if (!file) writer.error = 1;
    }
    LOG("{\"event\":\"native_tactic_file_written\",\"accepted\":%s,\"stream_error\":%u,\"size\":%llu,\"side\":%u}",
        accepted ? "true" : "false", writer.error, (unsigned long long)bytes.size(), side);
    finish(accepted && !writer.error ? 0 : 175);
}

// Set-piece routine archives: the routine object deserialises itself (Windows vtable[5](obj, &stream, revision) ->
// Mac slot 6), into the home team's first routine of that type.
static void import_setpiece(unsigned char* match) {
    if (getenv("FM27_SETPIECE_FLAGS_AUDIT")) {
        fputs("{\"event\":\"native_setpiece_default_flags\",\"teams\":[", log_file);
        for (unsigned side = 0; side < 2; side++) {
            if (side) fputc(',', log_file); fputc('[', log_file);
            auto manager = manager_of(team_of(match, side));
            for (unsigned kind = 0; kind < 10; kind++) fprintf(log_file, "%s%u", kind ? "," : "", routine(manager, kind * 16)[0x15]);
            fputc(']', log_file);
        }
        fputs("]}\n", log_file); fflush(log_file); finish(0);
    }
    if (fmf_routine_type < 0) return;
    auto obj = routine(manager_of(team_of(match, 0)), fmf_routine_type * 16);
    if (!obj) finish(176);
    void* methods[8] = {};
    methods[vslot_stream_tell] = (void*)mac_tac_tell; methods[vslot_stream_seek] = (void*)mac_tac_seek; methods[vslot_stream_read] = (void*)mac_tac_read;
    MacTacticStream reader = {methods, 0, 0, 0, fmf_payload.data(), fmf_payload.size(), 0};
    void* reference = &reader;
    auto vt = *(void***)obj;
    bool accepted = ((unsigned char (*)(void*, void**, unsigned short))vt[vslot_routine_read])(obj, &reference, (unsigned short)fmf_stream_revision) != 0;
    fprintf(log_file, "{\"event\":\"native_setpiece_file_parsed\",\"accepted\":%s,\"stream_error\":%u,\"consumed\":%llu,\"size\":%llu,\"type\":%d,\"frequency\":%u,\"strategy\":%u,\"swing\":%u,\"opaque_flags\":%u,\"groups\":[",
            accepted ? "true" : "false", reader.error, (unsigned long long)reader.cursor, (unsigned long long)reader.size, fmf_routine_type, obj[0x14],
            ((unsigned char (*)(void*))vt[19])(obj), ((unsigned char (*)(void*))vt[20])(obj), obj[0x15]);
    for (unsigned g = 0; g < 8; g++) {
        if (g) fputc(',', log_file); fputc('[', log_file);
        auto begin = *(unsigned char**)(obj + 0x20 + g * 0x20), end = *(unsigned char**)(obj + 0x28 + g * 0x20);
        for (auto p = begin; p < end; p++) fprintf(log_file, "%s%u", p == begin ? "" : ",", *p);
        fputc(']', log_file);
    }
    fputs("],\"priority\":[", log_file);
    auto begin = *(unsigned char**)(obj + 0x118), end = *(unsigned char**)(obj + 0x120);
    for (auto p = begin; p < end; p++) fprintf(log_file, "%s%u", p == begin ? "" : ",", *p);
    fputs("],\"backups\":[", log_file);
    begin = *(unsigned char**)(obj + 0x130); end = *(unsigned char**)(obj + 0x138);
    for (auto p = begin; p < end; p += 3) fprintf(log_file, "%s[%u,%u,%u]", p == begin ? "" : ",", p[0], p[1], p[2]);
    fputs("]}\n", log_file); fflush(log_file);
    finish(accepted && !reader.error && reader.cursor == reader.size ? 0 : 177);
}
