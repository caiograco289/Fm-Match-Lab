// Installed coach preset export for the macOS host: the Mac twin of native/native_coach_presets.h.
// Version-bound export of the original installation presets and formation codes; never generates an AI plan.
// Evidence for every address: port/REPORT.md "Coach preset export".
#pragma once

static void* simatch_folder = nullptr;   // the installation's simatch.fmf folder object (opened in bootstrap)

static bool coach_presets_requested() { return getenv("FM27_COACH_PRESET_EXPORT") != nullptr; }

static void coach_preset_resource_types(unsigned char* resources) {
    if (!coach_presets_requested()) return;
    // Windows also calls protected 0x16c921e0 first; it builds the XML record type descriptor, which the Mac static
    // initialisers have already built at dlopen (checked here rather than assumed).
    auto descriptor = at<uint64_t*>(g_xml_record_type);
    LOG("{\"event\":\"coach_preset_resource_type\",\"descriptor_initialised\":%s}", descriptor[0] ? "true" : "false");
    if (!descriptor[0]) finish(248);
    ((void (*)(void*, void*))at(fn_resource_json_type))(resources, descriptor);
    uintptr_t key[4] = {};
    auto symbol = (void* (*)(void*, const char*, unsigned, unsigned))at(fn_symbol_make);
    symbol(key, "folder", 0x666f6c64, 0); symbol(key, "text", 0x74657874, 0);
    symbol(key, "hint", 0x68696e74, 0);   symbol(key, "id", 0x69642020, 0);
    // Style record attribute symbols (tactical_style_id/stID, ...): registered by the game's startup (0x296c0), which
    // this host does not run; call the game's own registration function.
    ((void (*)())at(fn_style_symbols))();
}

// libc++ std::map node: __left_ +0, __right_ +8, __parent_ +0x10, __is_black_ +0x18; key +0x20, value +0x28.
// The tree object: __begin_node_ +0, __end_node_.__left_ (root) +8, size +0x10 (see FUN_04dcd1e0's inlined lookup).
struct RbNode { RbNode* left; RbNode* right; RbNode* parent; bool black; uint8_t pad[7]; uint64_t key; void* value; };
static_assert(sizeof(RbNode) == 0x30, "libc++ map<uint64_t, ptr> node");
static bool rb_is_left(RbNode* x) { return x == x->parent->left; }
static void rb_rotate_left(RbNode* x) {
    RbNode* y = x->right; x->right = y->left; if (x->right) x->right->parent = x;
    y->parent = x->parent; if (rb_is_left(x)) x->parent->left = y; else x->parent->right = y;
    y->left = x; x->parent = y;
}
static void rb_rotate_right(RbNode* x) {
    RbNode* y = x->left; x->left = y->right; if (x->left) x->left->parent = x;
    y->parent = x->parent; if (rb_is_left(x)) x->parent->left = y; else x->parent->right = y;
    y->right = x; x->parent = y;
}
static void rb_balance_after_insert(RbNode* root, RbNode* x) {   // libc++ __tree_balance_after_insert
    x->black = x == root;
    while (x != root && !x->parent->black) {
        if (rb_is_left(x->parent)) {
            RbNode* y = x->parent->parent->right;
            if (y && !y->black) { x = x->parent; x->black = true; x = x->parent; x->black = x == root; y->black = true; }
            else {
                if (!rb_is_left(x)) { x = x->parent; rb_rotate_left(x); }
                x = x->parent; x->black = true; x = x->parent; x->black = false; rb_rotate_right(x); break;
            }
        } else {
            RbNode* y = x->parent->parent->left;
            if (y && !y->black) { x = x->parent; x->black = true; x = x->parent; x->black = x == root; y->black = true; }
            else {
                if (rb_is_left(x)) { x = x->parent; rb_rotate_right(x); }
                x = x->parent; x->black = true; x = x->parent; x->black = false; rb_rotate_left(x); break;
            }
        }
    }
}
static RbNode* rb_find(unsigned char* tree, uint64_t key) {
    auto end = (RbNode*)(tree + 8);
    for (RbNode* n = end->left; n;) { if (key < n->key) n = n->left; else if (n->key < key) n = n->right; else return n; }
    return nullptr;
}
static bool rb_insert(unsigned char* tree, uint64_t key, void* value) {
    auto end = (RbNode*)(tree + 8);
    RbNode* parent = end; RbNode** child = &end->left;
    for (RbNode* n = end->left; n;) {
        parent = n;
        if (key < n->key) { child = &n->left; n = n->left; }
        else if (n->key < key) { child = &n->right; n = n->right; }
        else return false;
    }
    auto node = (RbNode*)::operator new(sizeof(RbNode));
    *node = RbNode{nullptr, nullptr, parent, false, {}, key, value};
    *child = node;
    auto& begin = *(RbNode**)tree;
    if (begin->left) begin = begin->left;
    rb_balance_after_insert(end->left, node);
    ++*(uint64_t*)(tree + 0x10);
    return true;
}

static void export_coach_presets() {
    if (!coach_presets_requested()) return;
    // Bind the match_folder symbol (special folders.xml) to the installation's simatch.fmf, as on Windows.
    auto fm = *at<unsigned char**>(g_file_manager);
    if (!fm) finish(248);
    auto tree = *(unsigned char**)(*(unsigned char**)(fm + 0x18) + 8);
    uint64_t key = *at<uint64_t*>(g_match_folder_sym);
    auto existing = rb_find(tree, key);
    LOG("{\"event\":\"match_folder_binding_before\",\"present\":%s}", existing && existing->value ? "true" : "false");
    if (!existing || !existing->value) {
        if (!simatch_folder || !key) finish(248);
        __atomic_add_fetch((int*)((unsigned char*)simatch_folder + 8), 1, __ATOMIC_SEQ_CST);
        if (existing) existing->value = simatch_folder; else if (!rb_insert(tree, key, simatch_folder)) finish(248);
        auto found = rb_find(tree, key);
        if (!found || found->value != simatch_folder) finish(248);
        // The game's own match-folder accessor (inlined lookup + subfolder open) must now succeed.
        void* match_dir = nullptr;
        ((void* (*)(void*))at(fn_match_folder_open))(&match_dir);
        LOG("{\"event\":\"match_folder_bound\",\"source\":\"installation_FMF\",\"engine_accessor\":%s}", match_dir ? "true" : "false");
        if (!match_dir) finish(248);
    }

    auto loader = ((unsigned char* (*)())at(fn_preset_loader))();
    if (!loader || loader != *at<unsigned char**>(g_preset_loader)) finish(248);
    ((void (*)(void*, unsigned))at(fn_preset_load))(loader, 0);
    auto sb = *(unsigned char***)(loader + 8), se = *(unsigned char***)(loader + 0x10);
    if (se < sb || se - sb > 128) finish(248);
    for (auto p = sb; p != se; p++)
        LOG("{\"event\":\"coach_preset_style\",\"id\":%u,\"style_code\":%u}", (*p)[0xc8], *(uint32_t*)(*p + 4));
    // Read the already-loaded original TAC objects; do not generate a plan.
    auto begin = *(unsigned char***)(loader + 0x20), end = *(unsigned char***)(loader + 0x28);
    if (end < begin || end - begin > 512) finish(248);
    for (auto entry = begin; entry != end; entry++) {
        auto plan = *entry;   // parsed by fn_tac_parse: same layout as the live plan at manager+mg_plan
        auto name = *(unsigned char**)(plan + pp_name);
        unsigned size = name ? *(unsigned*)name : 0;
        if (size > 1024) finish(248);
        fprintf(log_file, "{\"event\":\"installed_tactic_preset\",\"index\":%u,\"style_code\":%u,\"name_utf8_hex\":\"",
                (unsigned)(entry - begin), *(uint32_t*)(plan + pp_style));
        for (unsigned i = 0; i < size; i++) fprintf(log_file, "%02x", name[4 + i]);
        fprintf(log_file, "\",\"mentality\":%u,\"team_bits\":\"", plan[pp_bits + 0x25]);
        for (unsigned i = 0; i < 16; i++) fprintf(log_file, "%02x", plan[pp_bits + i]);
        fputs("\",\"mapping\":[", log_file);
        for (unsigned i = 0; i < 11; i++) fprintf(log_file, "%s%u", i ? "," : "", plan[pp_map + i]);
        fputs("],\"phases\":[", log_file);
        for (unsigned phase = 0; phase < 2; phase++) {
            fprintf(log_file, "%s[", phase ? "," : "");
            for (unsigned i = 0; i < 11; i++) {
                auto cell = plan + pp_cells + (phase ? cell_oop_offset - cell_ip_offset : 0) + cell_stride * i;
                auto pi = instruction_entry(cell, false);
                fprintf(log_file, "%s{\"position\":%u,\"role_flags\":\"%llu\",\"pi_flags\":\"%llu\",\"target_player\":%u,\"target_position\":%u}",
                        i ? "," : "", *(uint32_t*)cell, (unsigned long long)*(uint64_t*)(cell + cell_role), pi ? (unsigned long long)pi[1] : 0,
                        pi ? ((unsigned char*)pi)[20] : 255, pi ? *(uint32_t*)((unsigned char*)pi + 16) : 0);
            }
            fputs("]", log_file);
        }
        fputs("]}\n", log_file); fflush(log_file);
    }

    unsigned formations = 0;
    for (unsigned code = 0; code <= 64; code++) {
        if (!((unsigned char (*)(unsigned))at(fn_formation_valid))(code)) continue;
        auto plan = (unsigned char*)::operator new(plan_size);
        memset(plan, 0, plan_size);
        ((void* (*)(void*, void*, unsigned char))at(fn_plan_ctor))(plan, at(g_plan_defaults), 1);
        ((void (*)(void*, unsigned, unsigned char, unsigned char, unsigned char))at(fn_plan_set_formation))(plan, code, 0, 1, 1);
        fprintf(log_file, "{\"event\":\"coach_preset_formation\",\"code\":%u,\"positions\":[", code);
        for (unsigned j = 0; j < 11; j++) fprintf(log_file, "%s%u", j ? "," : "", *(uint32_t*)(plan + pp_cells + cell_stride * j));
        fputs("]}\n", log_file); fflush(log_file);
        formations++;
        ((void (*)(void*))at(fn_plan_dtor))(plan);
        ::operator delete(plan);
    }
    LOG("{\"event\":\"coach_preset_export_complete\",\"styles\":%u,\"templates\":%u,\"formations\":%u}",
        (unsigned)(se - sb), (unsigned)(end - begin), formations);
    finish(0);
}
