// FM27 Tactics Lab: macOS native match host (x86_64 slice, runs under Rosetta on Apple Silicon).
// Mac counterpart of native/desktop_host.cpp's core pipeline: it loads the unchanged, user-owned
// game_plugin from the FM27 install with dlopen, runs the original native bootstrap, deserializes a
// PKM fixture with FM's own reader and steps MATCH::play until the match ends naturally.
// No game file is modified; Steam must be running and logged in (as for the Windows tool).
#include <dlfcn.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <chrono>
#include <new>
#include <malloc/malloc.h>
#include <mach/mach.h>
#include <mach/mach_vm.h>
#include "fm27_mac_x86_64.h"
#include <array>
#include <algorithm>
#include <mach-o/dyld.h>
#include <fstream>
#include <CommonCrypto/CommonDigest.h>

using namespace fm27mac;

static FILE* log_file = stderr;
static unsigned char* base = nullptr;
static void* engine_handle = nullptr;
static std::string game_root;     // .../game_plugin.bundle/Contents/Resources
static std::string fixture, output;
static bool seed_override = false;
static uint32_t requested_seed = 0;
static int tick_step = 1;

template <class T = void*> static T at(uintptr_t rva) { return (T)(base + rva); }
#define LOG(...) do { fprintf(log_file, __VA_ARGS__); fputc('\n', log_file); fflush(log_file); } while (0)

static bool (*exit_cleanup)() = nullptr;
static bool image_uuid_verified = false;
static std::string cancel_file, worker_manifest;
static bool worker_mode = false;
[[noreturn]] static void finish(int code) {
    if (exit_cleanup && !exit_cleanup() && !code) code = 180;
    LOG("{\"event\":\"host_exit\",\"code\":%d}", code);
    fflush(log_file);
    _exit(code);
}

static bool in_image(const void* p, uintptr_t lo, uintptr_t hi) {
    auto a = (uintptr_t)p;
    return base && a >= (uintptr_t)base + lo && a < (uintptr_t)base + hi;
}

// ---- crash containment (Windows: vectored exception handler) ----
static void on_fault(int sig, siginfo_t* info, void* uctx) {
    auto mc = ((ucontext_t*)uctx)->uc_mcontext;
    uintptr_t pc = mc->__ss.__rip;
    fprintf(log_file, "{\"event\":\"exception\",\"signal\":%d,\"fault\":\"0x%llx\",\"pc\":\"0x%llx\",\"engine_rva\":\"0x%llx\"}\n",
            sig, (unsigned long long)(uintptr_t)info->si_addr, (unsigned long long)pc,
            (unsigned long long)(base && pc >= (uintptr_t)base ? pc - (uintptr_t)base : 0));
    // frame-pointer walk (engine is built with frame pointers on macOS)
    auto fp = (uintptr_t*)mc->__ss.__rbp;
    for (int depth = 0; depth < 24 && fp; depth++) {
        uintptr_t ret = fp[1];
        fprintf(log_file, "{\"event\":\"native_av_frame\",\"depth\":%d,\"pc\":\"0x%llx\",\"engine_rva\":\"0x%llx\"}\n", depth,
                (unsigned long long)ret, (unsigned long long)(base && ret >= (uintptr_t)base ? ret - (uintptr_t)base : 0));
        auto next = (uintptr_t*)fp[0];
        if (next <= fp || (uintptr_t)next - (uintptr_t)fp > 0x100000) break;
        fp = next;
    }
    fflush(log_file);
    _exit(120 + sig);
}

static void install_fault_handler() {
    static std::vector<char> alt(1 << 16);
    stack_t ss{};
    ss.ss_sp = alt.data(); ss.ss_size = alt.size();
    sigaltstack(&ss, nullptr);
    struct sigaction sa{};
    sa.sa_sigaction = on_fault;
    sa.sa_flags = SA_SIGINFO | SA_ONSTACK;
    for (int s : {SIGSEGV, SIGBUS, SIGILL, SIGFPE, SIGABRT}) sigaction(s, &sa, nullptr);
}

// ---- image identity (Windows: PE layout + byte ranges; Mac: LC_UUID of the loaded slice) ----
static bool known_image(const mach_header_64* mh) {
    if (mh->cputype != CPU_TYPE_X86_64) return false;
    auto cmd = (const load_command*)(mh + 1);
    for (uint32_t i = 0; i < mh->ncmds; i++) {
        if (cmd->cmd == LC_UUID) {
            auto u = (const uuid_command*)cmd;
            bool ok = !memcmp(u->uuid, kUuid, 16);
            LOG("{\"event\":\"native_engine_compatibility\",\"profile\":\"fm27-" FM27_MAC_GAME_VERSION "-macos-x86_64\",\"compatible\":%s}",
                ok ? "true" : "false");
            return ok;
        }
        cmd = (const load_command*)((const char*)cmd + cmd->cmdsize);
    }
    return false;
}

struct EngineString { uintptr_t p[4] = {}; };

// Copy memory without faulting (layout calibration on unverified pointers).
static bool safe_copy(const void* src, void* dst, size_t n) {
    mach_vm_size_t got = 0;
    return mach_vm_read_overwrite(mach_task_self(), (mach_vm_address_t)src, n, (mach_vm_address_t)dst, &got) == KERN_SUCCESS && got == n;
}   // engine string handle (8 bytes used on Mac)

static void release_ref(void*& value) {
    if (!value) return;
    auto p = value; value = nullptr;
    if (__atomic_sub_fetch((int*)((unsigned char*)p + 8), 1, __ATOMIC_SEQ_CST) == 0)
        ((void (*)(void*))(*(void***)p)[vslot_release])(p);
}

#include "fm27_mac_scenario.h"
#include "fm27_mac_results.h"
#include "fm27_mac_fmf.h"
#include "fm27_mac_presets.h"
#include "fm27_mac_episode.h"
#include "fm27_mac_execution.h"
#include "fm27_mac_dump.h"

static void check_cancel() {
    if (!cancel_file.empty() && access(cancel_file.c_str(), F_OK) == 0) {
        LOG("{\"event\":\"native_match_cancelled\",\"full_match_completed\":false}");
        finish(86);
    }
}

static bool bootstrapped = false;
static void bootstrap_engine() {
    if (bootstrapped) { LOG("{\"event\":\"native_worker_bootstrap_reused\"}"); return; }
    bootstrapped = true;
    if (chdir(game_root.c_str()) != 0) finish(94);
    auto platform = ((unsigned long (*)(int))at(fn_platform_init))(3);
    LOG("{\"event\":\"native_platform_initialized\",\"accepted\":%s}", platform & 1 ? "true" : "false");
    if (!(platform & 1)) finish(94);

    // ICU common data: the game supplies it through its file manager; the host maps the original file.
    auto set_data = (void (*)(const void*, int*))dlsym(engine_handle, "udata_setCommonData_65");
    auto icu_init = (void (*)(int*))dlsym(engine_handle, "u_init_65");
    if (!set_data || !icu_init) finish(103);
    int fd = open((game_root + "/icudt65l.dat").c_str(), O_RDONLY);
    struct stat st{};
    if (fd < 0 || fstat(fd, &st) || st.st_size < 32) finish(103);
    void* icu = mmap(nullptr, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    if (icu == MAP_FAILED) finish(103);
    int status = 0;
    set_data(icu, &status); icu_init(&status);
    LOG("{\"event\":\"host_icu_data_initialized\",\"status\":%d}", status);
    if (status > 0) finish(103);

    if (!*at<void**>(g_resources)) {
        void* m = ::operator new(resources_size);
        ((void* (*)(void*))at(fn_resources_ctor))(m);
        *at<void**>(g_resources) = m;
    }
    if (!*at<void**>(g_structured)) {
        void* m = ::operator new(0x10);
        ((void* (*)(void*))at(fn_structured_ctor))(m);
        *at<void**>(g_structured) = m;
        ((void (*)())at(fn_structured_post))();
    }
    auto resources = *at<unsigned char**>(g_resources);
    ((void (*)(void*, void*))at(fn_resource_types))(resources, at(g_default_types));
    ((void (*)(void*, void*))at(fn_resource_json_type))(resources, at(g_json_type_key));
    coach_preset_resource_types(resources);
    ((void (*)(void*))at(fn_resources_finalise))(resources);

    for (const char* relative : {"shared/data/simatch.fmf", "shared/data/simatchshared.fmf"}) {
        std::string path = game_root + "/" + relative;
        EngineString name;
        ((void* (*)(void*, const char*, int))at(fn_string_from_c))(&name, path.c_str(), -1);
        void* file = nullptr; void* folder = nullptr;
        ((void* (*)(void*, void*, void*))at(fn_file_open))(&file, &name, resources + res_filesystem);
        ((void* (*)(void*, void*, uintptr_t))at(fn_folder_open))(&folder, &file, *at<uintptr_t*>(g_folder_key));
        LOG("{\"event\":\"native_archive_opened\",\"path\":\"%s\",\"success\":%s}", relative, folder ? "true" : "false");
        if (!folder) continue;
        if (!strcmp(relative, "shared/data/simatch.fmf")) simatch_folder = folder;
        EngineString folder_path;
        ((void* (*)(void*, void*))(*(void***)folder)[vslot_folder_path])(&folder_path, folder);
        ((void (*)(void*, void*, void*))at(fn_register_root))(resources, &folder_path, at(g_updates_folder_sym));
    }
    fmf_probe(resources);
    auto rb = *(unsigned char**)(resources + res_roots_begin), re = *(unsigned char**)(resources + res_roots_end);
    LOG("{\"event\":\"native_asset_roots_registered\",\"count\":%llu}", (unsigned long long)((re - rb) / 0x30));
    int scan = ((int (*)(void*))at(fn_resources_scan))(resources);
    LOG("{\"event\":\"native_resource_index_built\",\"status\":%d}", scan);
    uintptr_t query[2] = {}, folder_list[3] = {};
    ((void* (*)(void*, void*))at(fn_folder_query_ctor))(query, at(g_xg_query_key));
    auto found = ((unsigned char (*)(void*, void*, void*))at(fn_folder_lookup))(resources, query, folder_list);
    LOG("{\"event\":\"native_xg_folder_probe\",\"found\":%s,\"entries\":%llu}", found ? "true" : "false",
        (unsigned long long)((folder_list[1] - folder_list[0]) / 8));
    if (scan || !found || folder_list[0] == folder_list[1]) finish(95);

    static unsigned char init_input[0x88];
    memcpy(init_input, at(g_bootstrap_table), sizeof(init_input));
    auto ok = ((unsigned char (*)(void*, void*))at(fn_bootstrap))(init_input, nullptr);
    LOG("{\"event\":\"native_engine_bootstrap_returned\",\"accepted\":%s}", ok ? "true" : "false");
    if (!ok) finish(93);
}

static void log_xg_models() {   // every job, as on Windows
    auto stats = *at<uintptr_t**>(g_xg_models);
    size_t versions = stats ? (stats[2] - stats[1]) / 32 : 0, models = 0;
    for (auto p = stats ? stats[1] : 0; stats && p < stats[2]; p += 32) { auto row = (uintptr_t*)p; models += (row[2] - row[1]) / 32; }
    LOG("{\"event\":\"native_xg_models_parsed\",\"version_groups\":%zu,\"model_records\":%zu}", versions, models);
    if (const char* spec = getenv("FM27_MAC_XG_KEY")) {   // research: "old=new" renames one xG model group key (data write, this process)
        // "a=b" renames group a to b; "a<>b" swaps the two groups' keys
        unsigned long long from = 0, to = 0; bool swap = strstr(spec, "<>") != nullptr;
        if (sscanf(spec, swap ? "%lli<>%lli" : "%lli=%lli", &from, &to) != 2) finish(79);
        static bool done = false;
        if (!done) for (int v = 1; v < 10; v += 3) {   // three parallel tables keyed by the same version words (32-byte rows)
            uint64_t *a = nullptr, *b = nullptr;
            for (auto p = stats[v]; p < stats[v + 1]; p += 32) { if (*(uint64_t*)p == from) a = (uint64_t*)p; if (*(uint64_t*)p == to) b = (uint64_t*)p; }
            if (a) { *a = to; if (swap && b) *b = from; done = true; }
        }
        LOG("{\"event\":\"research_xg_group_key\",\"from\":%llu,\"to\":%llu,\"swap\":%s,\"renamed\":%s}", from, to, swap ? "true" : "false", done ? "true" : "false");
    }
    if (auto path = getenv("FM27_MAC_XG_DUMP")) {   // research: model store layout (groups of 32-byte rows, models of 32 bytes)
        FILE* f = fopen(path, "w"); if (!f) finish(105);
        auto hex = [&](const void* p, size_t n) { std::vector<unsigned char> b(n); bool ok = safe_copy(p, b.data(), n); fputc('"', f); if (ok) for (auto c : b) fprintf(f, "%02x", c); fputc('"', f); };
        fputs("{\"store\":", f); hex(stats, 0x50);
        fputs(",\"vectors\":[", f);
        for (int v = 1; v + 1 < 10; v += 3) { if (v > 1) fputc(',', f); auto b = stats[v], e = stats[v + 1]; hex((void*)b, e > b && e - b < 0x4000 ? e - b : 0); }
        fputs("],\"groups\":[", f);
        for (auto p = stats[1]; p < stats[2]; p += 32) {
            auto row = (uintptr_t*)p; fprintf(f, "%s{\"row\":", p == stats[1] ? "" : ","); hex(row, 32); fputs(",\"models\":[", f);
            for (auto m = row[1]; m < row[2]; m += 32) {
                fputs(m == row[1] ? "{\"model\":" : ",{\"model\":", f); hex((void*)m, 32);
                fputs(",\"targets\":[", f);
                for (int q = 0; q < 4; q++) { auto t = ((uintptr_t*)m)[q]; if (q) fputc(',', f); if (t > 0x100000000ull) hex((void*)t, 256); else fputs("null", f); }
                fputs("]}", f);
            }
            fputs("]}", f);
        }
        fputs("]}\n", f); fclose(f);
    }
    if (!versions || !models) finish(96);
}

static int native_match() {
    using clock = std::chrono::steady_clock;
    auto t0 = clock::now();
    scenario_edits.clear(); memset(original_roster, 0, sizeof(original_roster));
    bootstrap_engine();
    log_xg_models();
    auto resources = *at<unsigned char**>(g_resources);
    void* interface_object = *at<void**>(g_interface);

    EngineString recording_path;
    ((void* (*)(void*, const char*, int))at(fn_string_from_c))(&recording_path, fixture.c_str(), -1);
    void* recording_file = nullptr; void* stream = nullptr; void* reader_extra = nullptr;
    ((void* (*)(void*, void*, void*))at(fn_file_open))(&recording_file, &recording_path, resources + res_filesystem);
    struct Ret16 { uint64_t a, b; };
    ((Ret16 (*)(void*, void*, uintptr_t, void*))at(fn_reader_factory))(&stream, &recording_file, 0, &reader_extra);
    LOG("{\"event\":\"native_recording_stream_opened\",\"success\":%s}", stream ? "true" : "false");
    if (!stream) finish(104);
    __atomic_add_fetch((int*)((unsigned char*)stream + 8), 1, __ATOMIC_SEQ_CST);
    void* reference = stream;

    auto match = (unsigned char*)calloc(1, match_size);
    ((void* (*)(void*))at(fn_match_ctor))(match);
    *(void**)match = at(vt_benchmark_match);
    match[m_benchmark_flag] = 0;
    LOG("{\"event\":\"native_match_constructed\"}");

    struct { void* match; uint64_t flags; } ctx = {match, 0};
    auto tlv = at(tlv_match_context);
    auto slot = ((void** (*)(void*))(*(void**)tlv))(tlv);
    *slot = &ctx;

    auto accepted = ((unsigned char (*)(void*, void*, void*, unsigned))at(fn_match_deserialize))(match, &reference, interface_object, 0);
    LOG("{\"event\":\"native_fixture_deserialized\",\"accepted\":%s,\"input_adapter\":\"original_native\"}", accepted ? "true" : "false");
    if (!accepted) finish(88);
    if (getenv("FM27_MAC_PKM_INCIDENTS")) desktop_final_incidents(match);   // research: what a saved match carries in
    if (auto path = getenv("FM27_MAC_PLAYER_DUMP")) {   // research: loaded roster objects plus pointer targets (runs/, git-ignored)
        FILE* f = fopen(path, "w");
        if (!f) finish(105);
        std::vector<unsigned char> buf(0x2000);
        for (unsigned side = 0; side < 2; side++) for (unsigned i = 0; i < 26; i++) {
            auto p = roster_at(team_of(match, side), i);
            if (!p || !safe_copy(p, buf.data(), 0x2000)) continue;
            fprintf(f, "{\"side\":%u,\"index\":%u,\"object\":\"", side, i);
            for (auto b : buf) fprintf(f, "%02x", b);
            fputs("\",\"targets\":{", f);
            bool first = true;
            for (unsigned off = 0; off < 0x2000; off += 8) {
                void* q = *(void**)(buf.data() + off); unsigned char t[0x100];
                if ((uintptr_t)q < 0x100000000ull || !safe_copy(q, t, sizeof t)) continue;
                fprintf(f, "%s\"%u\":\"", first ? "" : ",", off); first = false;
                for (auto b : t) fprintf(f, "%02x", b);
                fputc('"', f);
            }
            fputs("}}\n", f);
        }
        fclose(f);
        LOG("{\"event\":\"player_dump_written\"}");
    }
    if (auto path = getenv("FM27_MAC_FAMILIARITY_DUMP")) {   // research: per-player lists at +0xa58 (6) and +0xb30, full contents
        FILE* f = fopen(path, "w"); if (!f) finish(105);
        for (unsigned side = 0; side < 2; side++) for (unsigned i = 0; i < team_of(match, side)[t_count]; i++) {
            auto p = roster_at(team_of(match, side), i);
            fprintf(f, "{\"side\":%u,\"index\":%u,\"lists\":[", side, i);
            for (unsigned k = 0; k < 7; k++) {
                auto v = p + (k < 6 ? 0xa58 + 32 * k : 0xb30);
                auto b = *(unsigned char**)v, e = *(unsigned char**)(v + 8);
                fputs(k ? ",\"" : "\"", f);
                if (b && e > b && e - b < 65536) for (auto q = b; q < e; q++) fprintf(f, "%02x", *q);
                fputc('"', f);
            }
            fputs("]}\n", f);
        }
        fclose(f);
    }
    release_ref(reference); release_ref(stream);
    export_coach_presets();
    import_tac(match);
    import_setpiece(match);

    if (!load_scenario() || !apply_scenario(match)) {
        LOG("{\"event\":\"scenario_rejected\",\"stage\":\"%s\",\"kind\":%u,\"side\":%u,\"a\":%u,\"b\":%u,\"value\":%u}", scenario_stage,
            current_scenario_edit.kind, current_scenario_edit.side, current_scenario_edit.a, current_scenario_edit.b, current_scenario_edit.value);
        finish(108);
    }
    if (scenario_file.empty())   // input roster order for slot-addressed research writes
        for (unsigned side = 0; side < 2; side++) for (unsigned i = 0; i < 26; i++) original_roster[side][i] = roster_at(team_of(match, side), i);
    if (scenario_file.empty()) research_attributes_apply(match);
    dump_match_input(match);
    if (inspect_fixture_only) { LOG("{\"event\":\"native_fixture_inspected\",\"simulation_ticks_executed\":0}"); finish(0); }
    export_tac(match);
    if (getenv("FM27_MAC_STAFF_PROBE")) {   // research: match-side staff objects and their vtables
        for (unsigned side = 0; side < 2; side++) {
            auto team = team_of(match, side);
            {
                auto m = manager_of(team), person = m + 8;
                fprintf(log_file, "{\"event\":\"staff_fields\",\"side\":%u,\"person_bytes_61_6a\":[", side);
                for (unsigned o = 0x61; o <= 0x6a; o++) fprintf(log_file, "%s%u", o > 0x61 ? "," : "", person[o]);
                fputs("],\"person_u32_44_58\":[", log_file);
                for (unsigned o = 0x44; o <= 0x58; o += 4) fprintf(log_file, "%s%u", o > 0x44 ? "," : "", *(uint32_t*)(person + o));
                fputs("],\"mgr_pairs\":[", log_file);
                for (unsigned o = 0x3218; o <= 0x32c0; o += 0x10) fprintf(log_file, "%s[%u,%llu]", o > 0x3218 ? "," : "", *(uint32_t*)(m + o), (unsigned long long)*(uint64_t*)(m + o + 8));
                fputs("],\"mgr_u32\":{", log_file);
                bool first = true;
                for (unsigned o : {0x34b4u, 0x34bcu, 0x34c0u, 0x34c4u, 0x34ccu, 0x34d0u, 0x34f0u, 0x34fcu, 0x3500u, 0x3504u}) { fprintf(log_file, "%s\"0x%x\":%u", first ? "" : ",", o, *(uint32_t*)(m + o)); first = false; }
                fprintf(log_file, "},\"mgr_bytes\":{\"0x3523\":%u,\"0x3524\":%u,\"0x3526\":%u,\"0x3528\":%u}}\n", m[0x3523], m[0x3524], m[0x3526], m[0x3528]);
            }
            for (unsigned off : {0x630u, 0x640u}) {
                auto obj = *(unsigned char**)(team + off); if (!obj) continue;
                auto vt = *(void***)obj;
                fprintf(log_file, "{\"event\":\"staff_probe\",\"side\":%u,\"team_offset\":\"0x%x\",\"vt\":\"0x%llx\",\"slots\":[", side, off, (unsigned long long)((unsigned char*)vt - base));
                for (unsigned i = 0; i < 12; i++) fprintf(log_file, "%s\"0x%llx\"", i ? "," : "", (unsigned long long)((unsigned char*)vt[i] - base));
                fputs("]}\n", log_file);
            }
        }
        fflush(log_file);
    }
    episode_init();
    if (episode.enabled || getenv("FM27_MAC_RESTART_PROBE")) {
        for (unsigned side = 0; side < 2; side++) {
            auto manager = manager_of(team_of(match, side));
            LOG("{\"event\":\"layout_check\",\"field\":\"selected_setpiece_variants\",\"side\":%u,\"active_is_manager_like\":%s}", side,
                *(unsigned char**)(manager + mg_active_manager) ? "true" : "false");
        }
    }
    if (getenv("FM27_MAC_ROUTINE_PROBE")) {   // calibration: set-piece routine object layout
        auto manager = manager_of(team_of(match, 0));
        for (unsigned type = 0; type < 10; type++) {
            uint64_t vec[2] = {}; safe_copy(manager + mg_routines + 0xd00 + 0, vec, 0);
            for (unsigned variant = 0; variant < 3; variant++) {
                auto obj = ((unsigned char* (*)(void*, unsigned, size_t))at(fn_routine))(manager + mg_routines, type, variant);
                if (!obj) continue;
                fprintf(log_file, "{\"event\":\"routine_probe\",\"type\":%u,\"variant\":%u,\"vt\":\"0x%llx\",\"q\":[", type, variant,
                        (unsigned long long)((unsigned char*)*(void**)obj - base));
                for (unsigned i = 0; i < 0x158 / 8; i++) fprintf(log_file, "%s\"%llx\"", i ? "," : "", (unsigned long long)((uint64_t*)obj)[i]);
                fputs("]}\n", log_file);
                auto vt = *(void***)obj;
                fprintf(log_file, "{\"event\":\"routine_vt\",\"type\":%u,\"slots\":[", type);
                for (unsigned i = 0; i < 26; i++) fprintf(log_file, "%s\"0x%llx\"", i ? "," : "", (unsigned long long)((unsigned char*)vt[i] - base));
                fprintf(log_file, "],\"v19\":%u,\"v20\":%u,\"v15_g0\":%u,\"v15_g1\":%u}\n",
                        ((unsigned char (*)(void*))vt[19])(obj), ((unsigned char (*)(void*))vt[20])(obj),
                        ((unsigned (*)(void*, unsigned char))vt[15])(obj, 0), ((unsigned (*)(void*, unsigned char))vt[15])(obj, 1));
            }
        }
        fflush(log_file);
    }
    auto fixture_seed = *(uint32_t*)(match + m_seed);
    if (seed_override) *(uint32_t*)(match + m_seed) = requested_seed;
    LOG("{\"event\":\"native_input_seed\",\"fixture_seed\":%u,\"effective_seed\":%u,\"override\":%s}", fixture_seed,
        *(uint32_t*)(match + m_seed), seed_override ? "true" : "false");

    log_engine_version(match, "before_preparation");
    engine_path_install(match);
    execution_install(match);
    if (const char* spec = getenv("FM27_MAC_STAFF_SET")) {   // research only: "side:offset=value,..." on the match-manager person block
        std::string all(spec); size_t at_ = 0;
        while (at_ < all.size()) {
            auto end = all.find(',', at_); auto item = all.substr(at_, end == std::string::npos ? std::string::npos : end - at_);
            unsigned side = 0, offset = 0, value = 0; float fvalue = 0;
            if (sscanf(item.c_str(), "%u:p%x=%u", &side, &offset, &value) == 3 && side < 2 && offset >= 0x61 && offset <= 0x6a && value < 256) {
                auto person = manager_of(team_of(match, side)) + 8;   // match-manager person block, byte field
                LOG("{\"event\":\"research_staff_override\",\"side\":%u,\"field\":\"person+0x%x\",\"before\":%u,\"after\":%u}", side, offset, person[offset], value);
                person[offset] = (unsigned char)value;
            } else if (sscanf(item.c_str(), "%u:f%x=%f", &side, &offset, &fvalue) == 3 && side < 2 && (offset == 0x34fc || offset == 0x3504)) {
                auto field = (float*)(manager_of(team_of(match, side)) + offset);   // match-manager float fields
                LOG("{\"event\":\"research_staff_override\",\"side\":%u,\"field\":\"manager+0x%x\",\"before\":%g,\"after\":%g}", side, offset, *field, fvalue);
                *field = fvalue;
            } else finish(79);
            if (end == std::string::npos) break; at_ = end + 1;
        }
    }
    auto t_prepare = clock::now();
    ((void (*)(void*))at(fn_match_prepare))(match);
    auto t_ready = clock::now();
    for (const auto& edit : scenario_edits) if (edit.kind == 17) {
        auto team = team_of(match, edit.side);
        if (edit.value < 11 || edit.value > team[t_count]) finish(108);
        auto original = team[t_count]; team[t_count] = (unsigned char)edit.value;
        LOG("{\"event\":\"native_match_roster_committed\",\"side\":%u,\"carrier_count\":%u,\"participants\":%u,\"after_original_preparation\":true}", edit.side, original, edit.value);
    }
    if (!verify_scenario(match)) { LOG("{\"event\":\"scenario_readback_mismatch\"}"); finish(109); }
    research_attributes_verify(match);
    in_match_management_apply(match);
    if (getenv("FM27_MAC_LIVE_AFTER_PREP")) for (unsigned side = 0; side < 2; side++) {   // research: manual-input flag cleared after preparation
        auto flags = (uint32_t*)(manager_of(team_of(match, side)) + mg_input_flags);
        LOG("{\"event\":\"research_input_flag_cleared\",\"side\":%u,\"before\":%u}", side, *flags);
        *flags &= ~1u;
    }
    if (const char* v = getenv("FM27_MAC_INPUT_FLAGS_AFTER_PREP")) {   // research: "home,away" input-flag words after preparation (-1 keeps)
        long w[2] = {-1, -1}; sscanf(v, "%li,%li", &w[0], &w[1]);
        for (unsigned side = 0; side < 2; side++) if (w[side] >= 0) {
            auto flags = (uint32_t*)(manager_of(team_of(match, side)) + mg_input_flags);
            LOG("{\"event\":\"research_input_flags_set\",\"side\":%u,\"before\":%u,\"after\":%ld}", side, *flags, w[side]);
            *flags = (uint32_t)w[side];
        }
    }
    unsigned char start_mentality[2] = {manager_of(team_of(match, 0))[mg_creator_live + 0x25], manager_of(team_of(match, 1))[mg_creator_live + 0x25]};
    LOG("{\"event\":\"native_preparation_returned\",\"gates\":[%u,%u,%u]}", match[m_gate_a], match[m_gate_b], match[m_gate_c]);
    if (match[m_gate_a] != 1 || match[m_gate_b] != 1 || match[m_gate_c] == 0) finish(89);
    log_engine_version(match, "after_preparation");
    execution_prepared(match);
    record_summary(match, "prepared");
    execution_apply(match, false);

    if (auto raw = getenv("FM27_MAC_RAW_DUMP")) {   // layout calibration only; output stays local (runs/, git-ignored)
        FILE* f = fopen(raw, "w");
        if (!f) { LOG("{\"event\":\"raw_layout_dump_failed\"}"); finish(105); }
        std::vector<unsigned char> buf;
        auto hex = [&](const void* p, size_t n) {
            buf.assign(n, 0); bool ok = safe_copy(p, buf.data(), n);
            fputc('"', f); if (ok) for (size_t i = 0; i < n; i++) fprintf(f, "%02x", buf[i]); fputc('"', f);
        };
        fputs("{\"match\":", f); hex(match, match_size); fputs(",\"teams\":[", f);
        for (unsigned side = 0; side < 2; side++) {
            auto team = *(unsigned char**)(match + m_teams + 8 * side);
            unsigned char* manager = nullptr; safe_copy(team + 0x640, &manager, 8);
            fprintf(f, "%s{\"team\":", side ? "," : ""); hex(team, 0x900);
            fputs(",\"manager\":", f); hex(manager, 0x3600);
            fputs(",\"targets\":{", f);   // first 0x2000 bytes behind every readable pointer slot of the team
            bool first = true;
            for (unsigned off = 0; off < 0x900; off += 8) {
                void* p = nullptr; unsigned char probe;
                if (!safe_copy(team + off, &p, 8) || !p || !safe_copy(p, &probe, 1)) continue;
                std::vector<unsigned char> tmp(0x2000); size_t n = safe_copy(p, tmp.data(), 0x2000) ? 0x2000 : 0x200;
                fprintf(f, "%s\"%u\":", first ? "" : ",", off); first = false; hex(p, n);
            }
            fputs("}}", f);
        }
        fputs("]}\n", f); fclose(f);
        LOG("{\"event\":\"raw_layout_dump_written\"}");
    }
    // Runtime layout checks for offsets derived from the -0x10 shift (see manual_map.json).
    if (getenv("FM27_MAC_LAYOUT_DUMP"))
        for (uintptr_t off = 0x15340; off < 0x153a0; off += 8) {
            auto p = *(void**)(match + off);
            LOG("{\"event\":\"layout_dump\",\"offset\":\"0x%lx\",\"value\":\"%p\",\"heap_size\":%zu}", (unsigned long)off, p,
                p && (uintptr_t)p > 0x100000000ull ? malloc_size(p) : (size_t)0);
        }
    {   // teams: two distinct engine-pool objects (offset from 225/238 displacement votes)
        auto t0 = *(unsigned char**)(match + m_teams), t1 = *(unsigned char**)(match + m_teams + 8);
        bool ok = t0 && t1 && t0 != t1;
        LOG("{\"event\":\"layout_check\",\"field\":\"teams\",\"ok\":%s,\"spacing\":%lld}", ok ? "true" : "false", (long long)(t1 - t0));
        if (!ok) finish(110);
    }
    auto score_context = *(unsigned char**)(match + m_score_context);
    void* result = score_context ? *(void**)(score_context + score_result) : nullptr;
    bool result_ok = result && in_image(*(void**)result, seg_data_const_begin, seg_data_const_end);
    LOG("{\"event\":\"layout_check\",\"field\":\"score_result\",\"vtable_in_image\":%s}", result_ok ? "true" : "false");
    if (!result_ok) finish(111);
    auto score = (unsigned char* (*)(void*, unsigned))(*(void***)result)[vslot_score];
    if (!desktop_events_start()) finish(181);

    int prev_home = *score(result, 0), prev_away = *score(result, 1);
    LOG("{\"event\":\"native_score_before_simulation\",\"score\":[%d,%d]}", prev_home, prev_away);
    if (prev_home || prev_away) finish(97);

    for (unsigned iteration = 0; iteration < 100000; iteration++) {
        int tick = *(int*)(match + m_tick);
        unsigned flags = *(unsigned*)(match + m_flags);
        int home = *score(result, 0), away = *score(result, 1);
        if (home != prev_home || away != prev_away) {
            LOG("{\"event\":\"observed_score_change\",\"tick\":%d,\"clock\":%d,\"score\":[%d,%d],\"observation_step\":%d}", tick,
                *(int*)(match + m_clock), home, away, tick_step);
            prev_home = home; prev_away = away;
        }
        if (!event_details_disabled) log_setpiece_selection(match, tick);
        check_cancel();
        episode_step(match);
        if (flags & 4) {
            if (auto probe = getenv("FM27_MAC_STATS_PROBE")) {   // layout calibration only (runs/, git-ignored)
                FILE* f = fopen(probe, "w");
                if (f) {
                    std::vector<unsigned char> buf;
                    auto hex = [&](const void* p, size_t n) { buf.assign(n, 0); bool ok = safe_copy(p, buf.data(), n); fputc('"', f); if (ok) for (auto b : buf) fprintf(f, "%02x", b); fputc('"', f); };
                    auto score_context = *(unsigned char**)(match + m_score_context);
                    fprintf(f, "{\"score\":[%d,%d],\"tick\":%d,\"context\":", home, away, tick); hex(score_context, 0x200);
                    fputs(",\"context_targets\":{", f); bool first = true;
                    for (unsigned off = 0; off < 0x200; off += 8) {
                        void* p = nullptr; unsigned char b; if (!safe_copy(score_context + off, &p, 8) || !p || !safe_copy(p, &b, 1)) continue;
                        fprintf(f, "%s\"%u\":", first ? "" : ",", off); first = false; hex(p, 0x400);
                    }
                    fputs("},\"teams\":[", f);
                    for (unsigned side = 0; side < 2; side++) {
                        auto team = *(unsigned char**)(match + m_teams + 8 * side); fprintf(f, "%s{", side ? "," : ""); first = true;
                        for (unsigned off = 0x600; off < 0x760; off += 8) {
                            void* p = nullptr; unsigned char b; if (!safe_copy(team + off, &p, 8) || !p || !safe_copy(p, &b, 1)) continue;
                            fprintf(f, "%s\"%u\":", first ? "" : ",", off); first = false; hex(p, 0x400);
                        }
                        fputs("}", f);
                    }
                    fputs("],\"keys\":[", f);
                    auto iface = *at<void**>(g_interface); auto vt = *(void***)iface;
                    for (unsigned side = 0; side < 2; side++) {
                        auto team = *(unsigned char**)(match + m_teams + 8 * side); fprintf(f, "%s[", side ? "," : "");
                        for (unsigned i = 0; i < team[0x73d]; i++) {
                            auto player = *(unsigned char**)(team + 0x140 + 8 * i); uint32_t k20 = 0xffffffff, k28 = 0xffffffff;
                            k20 = ((uint32_t (*)(void*, void*))vt[63])(iface, player + 0x20);
                            k28 = 0;
                            fprintf(f, "%s[%u,%u,%u]", i ? "," : "", *(uint32_t*)(player + 0x48), k20, k28);
                        }
                        fputs("]", f);
                    }
                    fputs("],\"totals\":[", f);
                    for (unsigned side = 0; side < 2; side++) {
                        auto totals = *(unsigned char**)(score_context + 0x68 + 8 * side);
                        auto b = *(unsigned char***)(totals + 0x250), e = *(unsigned char***)(totals + 0x258);
                        fprintf(f, "%s[", side ? "," : "");
                        for (auto it = b; it != e; it++) { fputs(it != b ? "," : "", f); hex(*it, 0xc0); }
                        fputs("]", f);
                    }
                    fputs("]}\n", f); fclose(f);
                }
            }
            auto now = clock::now();
            auto ms = [](auto a, auto b) { return (long long)std::chrono::duration_cast<std::chrono::milliseconds>(b - a).count(); };
            LOG("{\"event\":\"native_timings\",\"input_bootstrap_ms\":%lld,\"preparation_ms\":%lld,\"simulation_ms\":%lld,\"total_ms\":%lld}",
                ms(t0, t_prepare), ms(t_prepare, t_ready), ms(t_ready, now), ms(t0, now));
            execution_snapshot(match, "finished");
            record_summary(match, "finished");
            desktop_match_statistics(match);
            desktop_player_totals(match);
            for (unsigned side = 0; side < 2; side++)
                LOG("{\"event\":\"native_mentality_span\",\"side\":%u,\"kickoff\":%u,\"full_time\":%u,\"input_flag\":%u}", side, start_mentality[side],
                    manager_of(team_of(match, side))[mg_creator_live + 0x25], *(uint32_t*)(manager_of(team_of(match, side)) + mg_input_flags) & 1u);
            LOG("{\"event\":\"natural_match_finished\",\"full_match_completed\":true,\"runtime\":\"native_library_host_macos\",\"extracted_engine\":false,\"tick\":%d,\"clock\":%d,\"score\":[%d,%d]}",
                tick, *(int*)(match + m_clock), home, away);
            if (!desktop_events_stop()) finish(181);
            if (!worker_mode) finish(0);
            LOG("{\"event\":\"original_match_release_started\"}");
            void* iface = *at<void**>(g_interface);
            ((void (*)(void*))(*(void***)iface)[vslot_interface_release])(iface);
            ((void (*)(void*))at(fn_match_dtor))(match);
            free(match);
            if (*slot == &ctx) *slot = nullptr;
            LOG("{\"event\":\"original_match_release_completed\",\"tls_context_cleared\":%s,\"match_storage\":\"host_heap\"}", *slot == nullptr ? "true" : "false");
            return 0;
        }
        check_cancel();
        if (tick >= 47995) { LOG("{\"event\":\"watchdog_boundary_rejected\"}"); finish(90); }
        int target = std::min(tick + tick_step, 47995);
        execution_apply(match, true);
        ((void (*)(void*, unsigned, int))at(fn_match_step))(match, 1, target);
        {   // in-match tactical changes by the match's managers: mentality and the 22 role/position cells, logged when they change
            static unsigned char last_m[2]; static uint32_t last_pos[2][32]; static uint64_t last_role[2][32]; static void* last_match = nullptr;
            for (unsigned side = 0; side < 2; side++) {
                auto manager = manager_of(team_of(match, side));
                unsigned char m = manager[mg_creator_live + 0x25];
                std::string diff;
                for (unsigned e = 0; e < 32; e++) if (e % 16 < 11) {
                    auto c = tactic_cell(manager, e); uint32_t pos = *(uint32_t*)c; uint64_t role = *(uint64_t*)(c + cell_role);
                    if (last_match == match && (pos != last_pos[side][e] || role != last_role[side][e])) {
                        char item[160]; snprintf(item, sizeof item, "%s[%u,%u,%u,\"%llu\",\"%llu\"]", diff.empty() ? "" : ",", e, last_pos[side][e], pos, (unsigned long long)last_role[side][e], (unsigned long long)role);
                        diff += item;
                    }
                    last_pos[side][e] = pos; last_role[side][e] = role;
                }
                if (last_match == match && (m != last_m[side] || !diff.empty()))
                    LOG("{\"event\":\"native_tactic_change\",\"side\":%u,\"mentality\":[%u,%u],\"cells\":[%s],\"clock\":%d}", side, last_m[side], m, diff.c_str(), *(int*)(match + m_clock));
                last_m[side] = m;
            }
            last_match = match;
        }
        {   // substitutions: on-pitch flag (+0x1e26 == 1) per input roster player; lineup slot at +0x1e51 (255 = off)
            static int on_last[2][26]; static bool on_init = false;
            static void* on_match = nullptr; static int on_tick = 0; int now = *(int*)(match + m_tick);
            if (!on_init || on_match != match || now < on_tick) { for (auto& s : on_last) for (auto& v : s) v = -1; on_init = true; on_match = match; }   // new match (worker mode)
            on_tick = now;
            bool first = on_last[0][0] < 0 && on_last[1][0] < 0;
            for (unsigned side = 0; side < 2; side++) for (unsigned j = 0; j < 26; j++) {
                auto p = original_roster[side][j]; if (!p) continue;
                int on = p[p_on_pitch] == 1;
                if (on_last[side][j] >= 0 && on != on_last[side][j])
                    LOG("{\"event\":\"native_on_pitch_change\",\"side\":%u,\"roster_index\":%u,\"on\":%s,\"slot\":%u,\"clock\":%d,\"tick\":%d}",
                        side, j, on ? "true" : "false", p[p_lineup_slot], *(int*)(match + m_clock), *(int*)(match + m_tick));
                on_last[side][j] = on;
            }
            if (first)   // who is on the pitch after the first step (input roster indices), as the base for minutes played
                for (unsigned side = 0; side < 2; side++) {
                    std::string list;
                    for (unsigned j = 0; j < 26; j++) if (on_last[side][j] == 1) list += (list.empty() ? "" : ",") + std::to_string(j);
                    LOG("{\"event\":\"native_on_pitch_initial\",\"side\":%u,\"roster_indices\":[%s],\"clock\":%d}", side, list.c_str(), *(int*)(match + m_clock));
                }
        }
        if (auto trace = getenv("FM27_MAC_ROSTER_TRACE")) {   // research: roster order changes + periodic player snapshots
            static unsigned char* last[2][26] = {}; static FILE* snap = nullptr; static int next_clock = 0;
            int clock = *(int*)(match + m_clock);
            for (unsigned side = 0; side < 2; side++) {
                auto team = team_of(match, side); bool changed = false;
                for (unsigned i = 0; i < 26; i++) if (roster_at(team, i) != last[side][i]) changed = true;
                if (!changed) continue;
                fprintf(log_file, "{\"event\":\"roster_order\",\"side\":%u,\"clock\":%d,\"tick\":%d,\"count\":%u,\"order\":[", side, clock,
                        *(int*)(match + m_tick), team[t_count]);
                for (unsigned i = 0; i < 26; i++) {
                    auto p = roster_at(team, i); int orig = -1;
                    for (unsigned j = 0; j < 26; j++) if (original_roster[side][j] == p) orig = (int)j;
                    fprintf(log_file, "%s%d", i ? "," : "", orig); last[side][i] = p;
                }
                fputs("]}\n", log_file); fflush(log_file);
            }
            if (clock >= next_clock) {
                if (!snap) snap = fopen(trace, "w");
                for (unsigned side = 0; side < 2 && snap; side++) for (unsigned j = 0; j < 26; j++) {
                    auto p = original_roster[side][j]; std::vector<unsigned char> b(0x2000);
                    if (!p || !safe_copy(p, b.data(), b.size())) continue;
                    fprintf(snap, "{\"clock\":%d,\"side\":%u,\"index\":%u,\"object\":\"", clock, side, j);
                    for (auto c : b) fprintf(snap, "%02x", c);
                    fputs("\"}\n", snap);
                }
                if (snap) fflush(snap);
                next_clock = clock + 1200;
            }
        }
        int after = *(int*)(match + m_tick);
        if (iteration % 4096 == 0) LOG("{\"event\":\"native_match_progress\",\"tick\":%d,\"clock\":%d}", after, *(int*)(match + m_clock));
        if (after == tick) { LOG("{\"event\":\"native_match_stalled\",\"tick\":%d}", tick); finish(91); }
    }
    finish(92);
}

static std::string default_game_root() {
    const char* home = getenv("HOME");
    return std::string(home ? home : "") +
           "/Library/Application Support/Steam/steamapps/common/Football Manager 27/fm.app/Contents/PlugIns/game_plugin.bundle/Contents/Resources";
}

static std::string sha256_file(const std::string& path) {
    std::ifstream f(path, std::ios::binary); CC_SHA256_CTX c; CC_SHA256_Init(&c);
    std::vector<char> block(1 << 20);
    while (f) { f.read(block.data(), block.size()); if (f.gcount()) CC_SHA256_Update(&c, block.data(), (CC_LONG)f.gcount()); }
    unsigned char d[32]; CC_SHA256_Final(d, &c);
    char hex[65]; for (int i = 0; i < 32; i++) snprintf(hex + 2 * i, 3, "%02x", d[i]);
    return hex;
}

// Same as the Windows host's --policy-audit: the game's own role-mask and player-instruction policy functions, for
// every role/position/duty and engine version word, so the server's policy table can be built for a new build.
static int audit_policies() {
    std::vector<uint32_t> positions;
    for (auto row : fm27_role_positions) if (std::find(positions.begin(), positions.end(), row.position) == positions.end()) positions.push_back(row.position);
    for (auto position : positions) for (unsigned phase = 0; phase < 2; phase++) for (unsigned cb = 0; cb <= 11; cb++) for (unsigned dm = 0; dm <= 11; dm++) {
        auto mask = ((uint64_t (*)(const uint32_t*, unsigned))at(phase ? fn_role_mask_oop : fn_role_mask_ip))(&position, cb);
        if (phase && (position & 128) && dm == 1) mask &= ~0x20000ULL;
        LOG("{\"event\":\"role_policy\",\"phase\":%u,\"position\":%u,\"cb\":%u,\"dm\":%u,\"mask\":\"%llu\"}", phase, position, cb, dm, (unsigned long long)mask);
    }
    const uint64_t duties[] = {0, 2097152, 4194304, 8388608, 33554432, 67108864, 17179869184ULL};
    std::vector<uint32_t> versions = {0x1a080000u, 0x1b000000u};
    if (kFm27EngineVersion != 0x1b000000u) versions.push_back(kFm27EngineVersion);
    for (auto row : fm27_role_positions) for (auto duty : duties) for (uint32_t version : versions) {
        char statuses[44] = {}; statuses[0] = '0'; uint64_t editable = 0;
        for (unsigned option = 1; option <= 42; option++) {
            uint32_t status = 0, position = row.position;
            auto ok = ((unsigned char (*)(unsigned, const uint32_t*, uint64_t, const uint32_t*, uint32_t*))at(row.phase ? fn_policy_oop : fn_policy_ip))(option, &position, row.role | duty, &version, &status);
            if (status > 3) return 112;
            statuses[option] = '0' + status; if (ok) editable |= 1ULL << option;
        }
        LOG("{\"event\":\"pi_policy\",\"phase\":%u,\"position\":%u,\"role\":\"%llu\",\"duty\":\"%llu\",\"version\":%u,\"statuses\":\"%s\",\"editable\":\"%llu\"}",
            row.phase, row.position, (unsigned long long)row.role, (unsigned long long)duty, version, statuses, (unsigned long long)editable);
    }
    return 0;
}

// Same manifest as the Windows host: "FM27DW1" then 5 lines per job (fixture, scenario, output, seed, dump|-).
static int worker_loop() {
    std::ifstream manifest(worker_manifest); std::string line;
    if (!std::getline(manifest, line) || line != "FM27DW1") return 184;
    FILE* session_log = log_file; unsigned index = 0;
    while (std::getline(manifest, line)) {
        if (line.empty()) continue;
        check_cancel();
        if (++index > 64) return 184;
        std::string fields[5]; fields[0] = line;
        for (unsigned i = 1; i < 5; i++) if (!std::getline(manifest, fields[i])) return 184;
        fixture = fields[0]; scenario_file = fields[1]; output = fields[2]; dump_input_path = fields[4] == "-" ? std::string() : fields[4];
        char* end = nullptr; auto seed = strtoull(fields[3].c_str(), &end, 10);
        if (fields[3].empty() || *end || seed > UINT32_MAX) return 184;
        requested_seed = (uint32_t)seed; seed_override = true;
        if (access(output.c_str(), F_OK) == 0 || access((output + ".worker_done").c_str(), F_OK) == 0) return 187;
        FILE* next = fopen(output.c_str(), "w"); if (!next) return 98;
        log_file = next;
        LOG("{\"event\":\"native_worker_job_started\",\"index\":%u,\"pid\":%d,\"bootstrap_reused\":%s}", index, getpid(), bootstrapped ? "true" : "false");
        int result = native_match(); if (result) return result;
        log_file = session_log;
        if (fclose(next)) return 186;
        FILE* ack = fopen((output + ".worker_done").c_str(), "wb"); if (!ack) return 185;
        fprintf(ack, "{\"index\":%u,\"pid\":%d,\"released\":true,\"exit_code\":0}\n", index, getpid()); fclose(ack);
    }
    LOG("{\"event\":\"native_worker_completed\",\"jobs\":%u}", index);
    return index ? 0 : 184;
}

int main(int argc, char** argv) {
    game_root = getenv("FM27_GAME_ROOT") && *getenv("FM27_GAME_ROOT") ? getenv("FM27_GAME_ROOT") : default_game_root();
    {   // defaults next to the executable, as on Windows
        char exe[PATH_MAX]; uint32_t n = sizeof exe; char rp[PATH_MAX];
        std::string dir = _NSGetExecutablePath(exe, &n) == 0 && realpath(exe, rp) ? std::string(rp) : std::string(".");
        dir = dir.substr(0, dir.rfind('/') == std::string::npos ? 0 : dir.rfind('/'));
        fixture = dir + "/fixtures/match.pkm"; output = dir + "/last_match.jsonl";
    }
    auto absolute = [](const std::string& v) { char rp[PATH_MAX]; if (realpath(v.c_str(), rp)) return std::string(rp);
        if (!v.empty() && v[0] == '/') return v; char cwd[PATH_MAX]; return std::string(getcwd(cwd, sizeof cwd) ? cwd : ".") + "/" + v; };
    std::string check_image, option_bits; bool policy_audit = false;
    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        auto next = [&]() -> std::string { if (i + 1 >= argc) { fputs("missing value\n", stderr); exit(79); } return argv[++i]; };
        if (a == "--fixture") fixture = absolute(next());
        else if (a == "--output") output = absolute(next());
        else if (a == "--game-root") game_root = next();
        else if (a == "--scenario-file") scenario_file = absolute(next());
        else if (a == "--worker-manifest") { worker_manifest = absolute(next()); worker_mode = true; }
        else if (a == "--cancel-file" || a == "--cancel-event") cancel_file = absolute(next());   // macOS: a file whose existence cancels
        else if (a == "--check-image") check_image = next();
        else if (a == "--seed") { auto v = next(); char* e = nullptr; auto n = strtoull(v.c_str(), &e, 10); if (v.empty() || *e || n > UINT32_MAX) return 79; seed_override = true; requested_seed = (uint32_t)n; }
        else if (a == "--tick-step") { auto n = atoi(next().c_str()); if (n < 1 || n > 256) return 79; tick_step = n; }
        else if (a == "--policy-audit") policy_audit = true;
        else if (a == "--option-bits") option_bits = absolute(next());
        else if (a == "--dump-input") dump_input_path = absolute(next());
        else if (a == "--inspect-fixture") inspect_fixture_only = true;
        else if (a == "--child" || a == "--match") {}
        else if (a == "--help") { puts("fm27_mac_host [--fixture INPUT.pkm] [--seed UINT32] [--output RUN.jsonl] [--tick-step 1..256] [--scenario-file CFG]\n"
                                      "              [--worker-manifest FILE] [--cancel-file PATH] [--game-root DIR] [--check-image]\n"
                                      "              [--dump-input SNAPSHOT.json] [--inspect-fixture] [--policy-audit] [--option-bits IDS.txt]\n"
                                      "Runs the original FM27 native simulation from the user's macOS install (Steam must be running)."); return 0; }
        else { fputs("Unknown or incomplete argument\n", stderr); return 79; }
    }
    std::string image = game_root + "/../MacOS/game_plugin";
    log_file = check_image.empty() ? fopen(output.c_str(), "w") : stdout;
    if (!log_file) return 98;
    install_fault_handler();
    // No window: the host never creates an NSApplication or window-server connection (Windows: private desktop).
    LOG("{\"event\":\"simulator_started\",\"platform\":\"macos\",\"isolated_desktop\":true,\"isolation\":\"macos_headless_process\",\"full_match_completed\":false,\"extracted_engine\":false}");
    LOG("{\"event\":\"native_image_fingerprint\",\"sha256\":\"%s\"}", sha256_file(image).c_str());
    if (const char* expected = getenv("FM27_EXPECTED_DLL_SHA256")) if (sha256_file(image) != expected) { LOG("{\"event\":\"engine_changed_within_session\"}"); return 99; }
    // Installation app metadata, as on Windows; Steam itself must be running and logged in.
    setenv("SteamAppId", "4530370", 1);
    setenv("SteamGameId", "4530370", 1);
    setenv("SteamNoOverlayUI", "1", 1);
    if (!check_image.empty()) {
        // Identity check without running engine code: read LC_UUID of the x86_64 slice from the file.
        std::ifstream f(image, std::ios::binary); std::vector<unsigned char> d((std::istreambuf_iterator<char>(f)), {});
        bool ok = false;
        for (size_t i = 0; i + 16 <= d.size() && !ok; i += 4) if (!memcmp(&d[i], kUuid, 16)) ok = true;
        LOG("{\"event\":\"native_engine_compatibility\",\"profile\":\"fm27-" FM27_MAC_GAME_VERSION "-macos-x86_64\",\"compatible\":%s,\"method\":\"lc_uuid_in_file\"}", ok ? "true" : "false");
        return ok ? 0 : 99;
    }
    void* h = dlopen(image.c_str(), RTLD_NOW | RTLD_LOCAL);
    LOG("{\"event\":\"macos_load_returned\",\"success\":%s}", h ? "true" : "false");
    engine_handle = h;
    if (!h) { LOG("{\"event\":\"dlopen_error\",\"text\":\"%s\"}", dlerror()); return 81; }
    for (uint32_t i = 0; i < _dyld_image_count(); i++)
        if (strstr(_dyld_get_image_name(i), "/game_plugin.bundle/Contents/MacOS/game_plugin"))
            base = (unsigned char*)_dyld_get_image_header(i);
    if (!base || !known_image((const mach_header_64*)base)) { LOG("{\"event\":\"unsupported_engine_compatibility\"}"); return 99; }
    image_uuid_verified = true;
    exit_cleanup = desktop_steam_cleanup;
    bool runtime_absent = true;
    for (uint32_t i = 0; i < _dyld_image_count(); i++) {
        const char* n = _dyld_get_image_name(i);
        if (strstr(n, "UnityPlayer.dylib") || strstr(n, "GameAssembly.dylib") || strstr(n, "/Contents/MacOS/Football Manager 27")) runtime_absent = false;
    }
    LOG("{\"event\":\"runtime_dependencies_checked\",\"fm_exe_unity_player_game_assembly_absent\":%s}", runtime_absent ? "true" : "false");
    if (!runtime_absent) finish(100);
    if (policy_audit) finish(audit_policies());
    if (!option_bits.empty()) {   // the game's own team-instruction resolver (value -> engine bit) for a list of option IDs
        std::ifstream ids(option_bits); std::string line; unsigned count = 0;
        while (std::getline(ids, line)) {
            if (line.empty()) continue;
            char* e = nullptr; auto v = strtoull(line.c_str(), &e, 10); if (*e || v > UINT32_MAX) finish(79);
            unsigned bit = ((unsigned (*)(unsigned))at(fn_option_bit))((unsigned)v);
            LOG("{\"event\":\"option_bit\",\"value\":%llu,\"bit\":%u}", v, bit); count++;
        }
        finish(count ? 0 : 79);
    }
    if (const char* n = getenv("FM27_MAC_EXEC_ACCESSOR_TEST")) {   // research (27.0.1): the record accessor on random records
#if FM27_MAC_BUILD == 2494769
        auto accessor = (uint16_t (*)(const unsigned char*, unsigned char))at(0x4e49020);   // port/REPORT.md, record layout
        srand(12345);
        for (int k = 0, total = atoi(n); k < total; k++) {
            unsigned char rec[48] = {}; for (auto& b : rec) b = (unsigned char)(rand() & 0xff);
            rec[0x21] = (unsigned char)(rand() % 5);
            unsigned char idx = (unsigned char)(rand() % 10);
            unsigned value = accessor(rec, idx);
            fprintf(log_file, "{\"event\":\"exec_accessor\",\"idx\":%u,\"value\":%u,\"record\":\"", idx, value);
            for (unsigned i = 0; i < 0x22; i++) fprintf(log_file, "%02x", rec[i]);
            fputs("\"}\n", log_file);
        }
        finish(0);
#else
        finish(79);
#endif
    }
    // The Windows host waits for an activation word here; the macOS build has no equivalent.
    LOG("{\"event\":\"native_activation_completed\",\"windows_activation\":\"not_present_on_macos\"}");

    void* object = ::operator new(interface_size);
    memset(object, 0, interface_size);
    ((void* (*)(void*))at(fn_interface_ctor))(object);
    *at<void**>(g_interface) = object;
    LOG("{\"event\":\"native_interface_created\",\"vtable_rva\":\"0x%llx\"}", (unsigned long long)((unsigned char*)*(void**)object - base));
    finish(worker_mode ? worker_loop() : native_match());
}
