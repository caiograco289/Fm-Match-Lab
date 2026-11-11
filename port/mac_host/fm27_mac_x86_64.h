// macOS game_plugin x86_64 slice. Values below are FM27 27.0.0+2493426 (LC_UUID 0981AB31-AC3B-3D93-944F-47FE4B59CD9E);
// other builds take their code/data RVAs from a generated header (port/map/update_rvas.py + write_build_header.py),
// selected at compile time by FM27_MAC_BUILD (scripts/build_native_mac.py reads the installed LC_UUID).
// Struct offsets are shared: checked unchanged in 27.0.1 (match constructor, deserializer and step use the same fields).
// Mac twins of the Windows RVAs/offsets used by native/desktop_host.cpp.
// Sources and evidence: port/map/manual_map.json, port/map/rva_map.json, port/REPORT.md.
// Addresses and offsets only; no game bytes.
#pragma once
#include <stdint.h>

#ifndef FM27_MAC_BUILD
#define FM27_MAC_BUILD 2493426
#endif
#if FM27_MAC_BUILD == 2493426
#define FM27_RVA(name, value) value
#define FM27_MAC_UUID 0x09,0x81,0xAB,0x31,0xAC,0x3B,0x3D,0x93,0x94,0x4F,0x47,0xFE,0x4B,0x59,0xCD,0x9E
#define FM27_MAC_ENGINE_VERSION 0x1b000000u   // match constructor (0x49868a0) writes it at +0xa2c
#define FM27_MAC_GAME_VERSION "27.0.0+2493426"
#elif FM27_MAC_BUILD == 2494769
#include "fm27_mac_x86_64_2494769.h"
#else
#error "unknown FM27_MAC_BUILD"
#endif

namespace fm27mac {
static const uint8_t kUuid[16] = {FM27_MAC_UUID};
constexpr uint32_t kFm27EngineVersion = FM27_MAC_ENGINE_VERSION;   // the word the build's own match constructor writes

// ---- functions (Windows RVA in comments) ----
enum : uintptr_t {
    fn_interface_ctor      = FM27_RVA(fn_interface_ctor, 0x50b0fe0),  // 0x496aa30 (protected), object 0x60 on Mac (0x48 on Windows)
    fn_platform_init       = FM27_RVA(fn_platform_init, 0x48a3d70),  // 0x9e1d80  unsigned long(int)
    fn_resources_ctor      = FM27_RVA(fn_resources_ctor, 0x4861420),  // 0xc51e60  object 0x1c0 (0x110 on Windows)
    fn_structured_ctor     = FM27_RVA(fn_structured_ctor, 0x48d7fa0),  // 0xe06b60  object 0x10
    fn_structured_post     = FM27_RVA(fn_structured_post, 0x48b3f10),  // 0x33dfcc0
    fn_resource_types      = FM27_RVA(fn_resource_types, 0x48622c0),  // 0xc53400 (protected)
    fn_resource_json_type  = FM27_RVA(fn_resource_json_type, 0x4862810),  // 0xc53910
    fn_resources_finalise  = FM27_RVA(fn_resources_finalise, 0x4862890),  // 0xc539b0
    fn_string_from_c       = FM27_RVA(fn_string_from_c, 0x4884ba0),  // 0x15a640  (out, cstr, -1)
    fn_file_open           = FM27_RVA(fn_file_open, 0x4803b50),  // 0x38477b0 (out, name, fs)
    fn_folder_open         = FM27_RVA(fn_folder_open, 0x4805c50),  // 0x14590b0 (out, file, key)
    fn_register_root       = FM27_RVA(fn_register_root, 0x4863340),  // 0xc54920  (resources, path, symbol*)
    fn_resources_scan      = FM27_RVA(fn_resources_scan, 0x48639f0),  // 0xc55000 (protected); Mac returns int status
    fn_folder_query_ctor   = FM27_RVA(fn_folder_query_ctor, 0x485fbd0),  // 0x15a380
    fn_folder_lookup       = FM27_RVA(fn_folder_lookup, 0x48654b0),  // 0x15a3b0 (protected)
    fn_bootstrap           = FM27_RVA(fn_bootstrap, 0x50ab010),  // 0x4969df0
    fn_reader_factory      = FM27_RVA(fn_reader_factory, 0x4817a80),  // 0x14264d0; Mac has no hidden 16-byte return buffer
    fn_match_ctor          = FM27_RVA(fn_match_ctor, 0x49868a0),  // 0x184400
    fn_match_deserialize   = FM27_RVA(fn_match_deserialize, 0x5044810),  // 0x4973930
    fn_match_prepare       = FM27_RVA(fn_match_prepare, 0x5040990),  // 0x4962660 (protected)
    fn_match_step          = FM27_RVA(fn_match_step, 0x498afc0),
    fn_exec_build          = FM27_RVA(fn_exec_build, 0x4dd5f80),  // 0xd85a0 (reference only; not called or patched)
    fn_exec_sample         = FM27_RVA(fn_exec_sample, 0x4ad49c0),  // 0x41a50 (reference only; not called or patched)  // 0x4520bd0
    fn_option_bit          = FM27_RVA(fn_option_bit, 0x55afb0),   // 0x64fe90 (runtime-verified 103/103)
};

// ---- data ----
enum : uintptr_t {
    g_interface            = FM27_RVA(g_interface, 0x5cd7e58),  // 0x5701a70
    g_resources            = FM27_RVA(g_resources, 0x5c5ca00),  // 0x56f3b00
    g_structured           = FM27_RVA(g_structured, 0x5c5cd70),  // 0x56f3c28
    g_default_types        = FM27_RVA(g_default_types, 0x5c8c210),  // 0x5703660
    g_json_type_key        = FM27_RVA(g_json_type_key, 0x5c8c168),  // 0x5716528
    g_folder_key           = FM27_RVA(g_folder_key, 0x5c8bd58),  // 0x5709c50
    g_updates_folder_sym   = FM27_RVA(g_updates_folder_sym, 0x5c8c838),  // 0x5716928
    g_xg_query_key         = FM27_RVA(g_xg_query_key, 0x5cf2db0),  // 0x5719098
    g_bootstrap_table      = FM27_RVA(g_bootstrap_table, 0x5cd7c80),  // 0x57064f0 (0x88 bytes)
    g_xg_models            = FM27_RVA(g_xg_models, 0x5c79e88),  // 0x5706578
    vt_benchmark_match     = FM27_RVA(vt_benchmark_match, 0x5b93210),  // 0x4c8c878
    tlv_match_context      = FM27_RVA(tlv_match_context, 0x5c7a748),  // Windows TLS block +0x838
    g_deadball_types       = FM27_RVA(g_deadball_types, 0x59ba738),  // 0x4e38a90 dead-ball code -> attacking routine type (13 bytes)
    seg_data_const_begin   = FM27_RVA(seg_data_const_begin, 0x5a69000),
    seg_data_const_end     = FM27_RVA(seg_data_const_end, 0x5c5c000),
    image_text_end         = FM27_RVA(image_text_end, 0x5a69000),
};

// ---- struct sizes / offsets ----
enum : uintptr_t {
    interface_size         = 0x60,
    resources_size         = 0x1c0,
    res_roots_begin        = 0x118,      // Windows 0x78
    res_roots_end          = 0x120,      // Windows 0x80
    res_filesystem         = 0x160,      // Windows 0xc0
    match_size             = 0x15590,    // Windows 0x155b0
    m_seed                 = 0x18,       // Windows 0x20; same PCG seeding expression in both deserializers
    m_benchmark_flag       = 0x15588,    // Windows 0x155a0
    m_score_context        = 0x14e90,    // Windows 0x14ea0 (-0x10 region; runtime-checked)
    m_teams                = 0x15370,    // Windows 0x15380 (-0x10 region; runtime-checked)
    m_clock                = 0x15454,    // Windows 0x15464
    m_tick                 = 0x154dc,    // Windows 0x154ec
    m_flags                = 0x154f0,
    m_engine_version       = 0xa2c,      // Windows 0xa3a (decompiled pair 0xe0b00/0x4a23470; votes 172/180)
    m_deadball             = 0x12d60,    // Windows 0x12d70 (decompiled pair 0xddc70/0x4d09e20; votes 19/22)
    m_restart_team         = 0x12d40,    // Windows 0x12d50 (votes 26/28; runtime: one of the two teams)
    mg_active_manager      = 0x298,      // same (manager-layout object holding the selected set-piece variants)
    av_attacking           = 0x334a,     // Windows 0x331a (+0x30 for the whole block in the decompiled pair)    // Windows 0x15500
    m_gate_a               = 0x15560,    // Windows 0x15570
    m_gate_b               = 0x1555e,    // Windows 0x1556e
    m_gate_c               = 0x15565,    // Windows 0x15575
    score_result           = 0x18,       // score context -> result object (runtime-checked)
    vslot_score            = 6,          // Windows vtable[5]; Itanium has 2 destructor slots
    vslot_release          = 1,          // Windows vtable[0](p,1) scalar deleting destructor
    vslot_folder_path      = 5,          // Windows methods[4](this,&out); Mac (&out,this)
};

// ---- scenario editor layout (Windows offset in comments; evidence in port/REPORT.md "Phase 3") ----
// D = data alignment against upstream's Windows dump of the same fixture; V = displacement votes;
// C = decompiled caller pairs; P = prediction from the block model confirmed in data.
enum : uintptr_t {
    t_manager              = 0x640,      // 0x630   V(209/260) C
    t_roster               = 0x140,      // 0x138   D(team header +8 from 0x80)
    t_count                = 0x73d,      // 0x72d   V(10/10) D(23,26)
    t_adjustment           = 0x129,      // 0x121   D
    p_height               = 0x64,       // 0x6c    D(prefix -8 over 0x4c..0x78)
    p_field2               = 0x6a,       // 0x72 (fields 2..8 consecutive)
    p_age                  = 0x71,       // 0x79
    p_field19              = 0x68,       // 0x70
    p_attributes           = 0x478,      // 0x480   D(25/25, 28/28 players)
    p_cell_ip              = 0xcd8,      // 0xce0   V(209/224)
    p_cell_oop             = 0xdb0,      // 0xdb8   V(218/237)
    p_slot                 = 0x1e27,
    p_on_pitch             = 0x1e26,     // 1 while on the pitch (found by snapshot search, 27.0.1; runtime: 11 per side)
    p_lineup_slot          = 0x1e51,     // lineup slot while on the pitch, 255 off
    p_ca                   = 0xc90,      // Windows 0xc98 (u16; builder argument 10 in both decompiled callers)
    p_exec_record          = 0xcb2,      // Windows 0xcba: 33-byte tactical-effectiveness record (builder 0x4dd5f80)
    exec_record_size       = 33,
    exec_raw_ability       = 0x1c,       // record offsets, same on both (builder writes +0x1c..+0x20)
    exec_role_suitability  = 0x1d,
    exec_overall           = 0x1e,
    exec_buy_in            = 0x1f,
    exec_next_match        = 0x20,     // 0x1e27  C(effective-OI caller pair)
    mg_routines            = 0x8e8,      // 0x8f0   C(2 caller pairs) D
    mg_selection           = 0x6e0,      // 0x6e8   selection object: lists, captain (+0x200), routines (+0x208)
    mg_captain_slot        = 0x3521,     // 0x34e5  captain's XI slot after preparation (V 16/16; runtime-checked)
    mg_captain_key         = 0x8e0,      // 0x8e8   D
    mg_throw_flags         = 0x16d8,     // 0x16f0  D(block -0x18)
    mg_oi                  = 0x16e0,     // 0x16f8  D C
    mg_oi_pos_count        = 0x1730,     // 0x1748  D
    mg_oi_pos_rows         = 0x1734,     // 0x174c  D
    mg_cells_live          = 0x1808,     // 0x1818  D(cells at -0x10)
    mg_creator_live        = 0x18e0,     // 0x18f8  D
    mg_version             = 0x18f0,     // 0x1908  D(reads 0x1a080000)
    mg_map_live            = 0x1fb4,     // 0x1fb4  D (plan+0x79c)
    mg_creator_mid         = 0x20a0,     // 0x20a0  D
    mg_cells_canon         = 0x2788,     // 0x2768  D(cells at +0x20)
    mg_creator_input       = 0x2860,     // 0x2848  D
    mg_map_canon           = 0x2f34,     // 0x2f04  P+D
    mg_input_flags         = 0x30d0,     // 0x30a0  V(55/57) D(0x24000 vs 0x24001: bit 0 set by edit kind 10)
    cell_ip_offset         = 0x118,      // same
    cell_oop_offset        = 0x438,      // same
    cell_stride            = 0x48,       // same
    cell_role              = 0x40,       // same
};
enum : uintptr_t {
    fn_effective_oi        = FM27_RVA(fn_effective_oi, 0x4d60a30),  // 0x46fdbd0; Mac returns the 3 packed bytes in EAX (no out pointer)
    fn_instruction_insert  = FM27_RVA(fn_instruction_insert, 0x4f34a80),  // 0x135530  vector insert (vec, where, value) -> entry
    fn_policy_ip           = FM27_RVA(fn_policy_ip, 0x4f2f620),  // 0x46c0fe0
    fn_policy_oop          = FM27_RVA(fn_policy_oop, 0x4f32600),  // 0x8d540
    fn_role_mask_ip        = FM27_RVA(fn_role_mask_ip, 0x4ed5f00),  // 0x16d7b80
    fn_role_mask_oop       = FM27_RVA(fn_role_mask_oop, 0x4ed6020),  // 0xbb5b0 (Windows stub -> 0xbb5c0(pos,1,count); clang specialised (pos,count);
                                         //  5 shared mask constants, called by all 3 twin callers, adjacent to 0x4ed5f00)
    fn_oi_row              = FM27_RVA(fn_oi_row, 0x506bad0),  // 0x4a39350
    fn_routine             = FM27_RVA(fn_routine, 0x4d75590),  // 0xea590
    fn_throw_preset        = FM27_RVA(fn_throw_preset, 0x4da07d0),  // 0x49b8660
    fn_task_valid          = FM27_RVA(fn_task_valid, 0x4da4250),  // 0x4a22db0 (group, task); called first by the Mac setter
    fn_task_set            = FM27_RVA(fn_task_set, 0x4da4390),  // 0xe43e0 (routine, group, task, 0xff, 0); 10/10 caller votes
    fn_pool_get            = FM27_RVA(fn_pool_get, 0x48516d0),  // engine pool (&0x5c785d0; = *0x5c5cb90)
    fn_pool_alloc          = FM27_RVA(fn_pool_alloc, 0x48511b0),  // (pool, bytes); Windows 0xb6430(0x5700ef0, bytes)
    fn_pool_free           = FM27_RVA(fn_pool_free, 0x4851620),  // (pool, ptr, bytes): sized free used by the routine destructors
    fn_priority_list       = FM27_RVA(fn_priority_list, 0x507acc0),  // 0x4a204f0 (identical bodies)
    fn_priority_insert     = FM27_RVA(fn_priority_insert, 0x4dc1290),  // 0x4a1e230 (list, where, keys, count); decompiled pair
    fn_tac_write           = FM27_RVA(fn_tac_write, 0x507c550),  // 0x49a9ab0 (plan, &stream, 1); 15/15 caller votes, decompiled pair
    fn_tac_parse           = FM27_RVA(fn_tac_parse, 0x4de9870),  // 0x16fca0  (plan, &stream, 1); 6/6 caller votes, decompiled pair
};

// ---- FMF tactic import (port/mac_host/fm27_mac_fmf.h) ----
enum : uintptr_t {
    mg_plan                = 0x1800,     // Windows manager+0x1818: parser base. Mac parser fields: bits +0xe0 (=mg_creator_live),
                                         //  version +0xf0 (=mg_version), cells +0x120 (=mg_cells_live+0x118), map +0x7b4 (=mg_map_live)
    plan_title             = 0x790,      // Windows plan+0x778 (first string read/written by the TAC parser/writer)
    fmf_folder_dirs        = 0x30,       // runtime dump: same as Windows
    fmf_folder_files       = 0x38,
    fmf_node_title         = 0x18,
    fmf_node_size          = 0x38,
    vslot_node_open_raw    = 22,         // Windows vtable[21](node,&raw,0); Mac (&raw,node,0)
    vslot_stream_tell      = 3,          // Windows 2 (decompiled parser pair: +0x10 vs +0x18)
    vslot_stream_seek      = 4,          // Windows 3 (+0x18 vs +0x20), no hidden return on Mac
    vslot_routine_read     = 6,          // Windows routine vtable[5](obj, &stream, revision)
    vslot_stream_read      = 6,          // Windows 5 (+0x28 vs +0x30)
};

// ---- installed coach preset export (port/mac_host/fm27_mac_presets.h) ----
enum : uintptr_t {
    g_xml_record_type      = FM27_RVA(g_xml_record_type, 0x5c8c2c0),  // 0x57169e0: same argument of the decompiled pair 0xc5f7d0 / 0x486b230
    fn_symbol_make         = FM27_RVA(fn_symbol_make, 0x4889b80),  // 0x9bc480  (out, text, fourcc, 0); 77/77 caller votes
    g_file_manager         = FM27_RVA(g_file_manager, 0x5c5cf40),  // 0x56f3af8 (map tree at +0x18 -> +8; FUN_04dcd1e0)
    g_match_folder_sym     = FM27_RVA(g_match_folder_sym, 0x5cd7d08),  // 0x5712d38 "match_folder" (static initialiser 0x4e9ae20)
    fn_match_folder_open   = FM27_RVA(fn_match_folder_open, 0x4dcd1e0),  // engine accessor: map lookup + subfolder open; (sret out)
    fn_style_symbols       = FM27_RVA(fn_style_symbols, 0x4f38e50),  // registers "tactical_style_id" (stID) etc.; read by style ctor 0x4f37980
    fn_preset_loader       = FM27_RVA(fn_preset_loader, 0x2c9a0),    // 0x1d4bd0
    g_preset_loader        = FM27_RVA(g_preset_loader, 0x5c60430),  // 0x56f3bb8
    fn_preset_load         = FM27_RVA(fn_preset_load, 0x4dcd340),  // 0x49929c0 ("tactics/styles", "xml_resource_record_data")
    fn_formation_valid     = FM27_RVA(fn_formation_valid, 0x50c8c20),  // 0x4a1f1a0 (27/31 caller votes)
    fn_plan_ctor           = FM27_RVA(fn_plan_ctor, 0xd2900),    // 0x160930 (plan, defaults, 1): decompiled loader pair
    g_plan_defaults        = FM27_RVA(g_plan_defaults, 0x58d1718),  // 0x4aff5b9: same argument of that call
    fn_plan_set_formation  = FM27_RVA(fn_plan_set_formation, 0x4ddc670),  // 0xf1650 (callseq 17/18)
    fn_plan_dtor           = FM27_RVA(fn_plan_dtor, 0x49ee960),  // 0xd0340: failure path after the parser in both loaders
    plan_size              = 0x7c0,      // 0x7a8 (operator new size in the Mac loader)
    pp_bits                = 0xe0,       // plan = TAC parser base (manager+mg_plan); same on Windows
    pp_name                = 0xf8,       // Windows 0xf8 (checked at runtime: UTF-8 names)
    pp_style               = 0x100,      // Windows 0x100 (Mac loader writes +0x100 after the parse)
    pp_cells               = 0x120,      // Windows 0x118
    pp_map                 = 0x7b4,      // Windows 0x79c
};
}  // namespace fm27mac
