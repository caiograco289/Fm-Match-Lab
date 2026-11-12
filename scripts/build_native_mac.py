"""Build the macOS native host (x86_64 slice, runs under Rosetta) into private/engine/fm27_native/.

Also writes private/engine/fm27_native/engine_compat_profile.json for the macOS engine: the SHA-256 of the user's
own game_plugin and the LC_UUID the host requires. Nothing derived from game files is committed.
"""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import desktop_platform  # noqa: E402

# x86_64 LC_UUID -> (FM27_MAC_BUILD, game version, engine version word written by the build's match constructor)
BUILDS = {'0981AB31-AC3B-3D93-944F-47FE4B59CD9E': (2493426, '27.0.0+2493426', 0x1b000000),
          '94CDDC80-8474-327A-85E0-E4FF95DC6893': (2494769, '27.0.1+2494769', 0x1b000100),
          'DD0EE157-4C9C-31A7-81DD-0D1122E62FC7': (2503222, '27.0.1+2503222', 0x1b000100)}



def policy_table(host, native, engine_version):
    """Player-instruction policies for this build's engine word, from the game's own policy functions (host
    --policy-audit, as upstream generates its table on Windows). Same keys and rules as the catalog: statuses for the
    options of the instruction's own phase, '1' (unavailable) for the others. Written to the private native folder;
    the server merges it into the catalog. Skipped while FM27 is open."""
    if subprocess.run(['pgrep', '-x', 'Football Manager 27'], capture_output=True).returncode == 0:
        print('FM27 is open: player-instruction policy audit skipped (rebuild with the game closed).'); return
    if not (ROOT / 'private/catalog.json').is_file():
        print('Player-instruction policies: written with the catalogue (scripts/build_catalog.py).'); return
    catalog = json.loads((ROOT / 'private/catalog.json').read_text(encoding='utf8'))
    positions = {p['mask']: p['id'] for p in catalog['positions']}
    roles = {(r['phase'], int(r['flags'])): r['id'] for r in catalog['roles']}
    in_phase = {0: set(), 1: set()}
    for group in catalog['player_instructions']:
        in_phase[group['phase']].update(o['id'] for o in group['options'] if o['id'])
    with tempfile.TemporaryDirectory() as folder:
        log = Path(folder) / 'audit.jsonl'
        code = subprocess.run([str(host), '--policy-audit', '--output', str(log)], capture_output=True).returncode
        if code: raise SystemExit(f'policy audit failed (host exit {code}); is Steam running?')
        rows = {}
        for line in log.read_text(encoding='utf8').splitlines():
            e = json.loads(line)
            if e.get('event') != 'pi_policy': continue
            key = f'{e["phase"]}:{positions[e["position"]]}:{roles[(e["phase"], int(e["role"]))]}:{e["duty"]}'
            statuses = ''.join(s if i == 0 or i in in_phase[e['phase']] else '1' for i, s in enumerate(e['statuses']))
            rows.setdefault(f'{e["version"]:08x}', {})[key] = statuses
    word = f'{engine_version:08x}'
    for version, table in rows.items():   # the audit must reproduce the catalog's own tables exactly
        known = {k: v[version] for k, v in catalog['pi_policies'].items() if version in v}
        if known and known != table: raise SystemExit(f'policy audit disagrees with the catalog for {version}; not written')
    out = native / f'pi_policies_{word}.json'
    out.write_text(json.dumps({'version': word, 'source': 'host --policy-audit', 'pi_policies': rows[word]}) + '\n', encoding='utf8')
    checked = sorted(v for v in rows if any(v in r for r in catalog['pi_policies'].values()))
    print(f'Player-instruction policies for {word}: {len(rows[word])} entries (audit reproduces catalog tables {checked})')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', type=Path, help='FM27 Steam folder, fm.app or game_plugin.bundle/Contents/Resources')
    parser.add_argument('--output', type=Path, help='host path (default private/engine/fm27_native/<host>); the profile is written next to it')
    args = parser.parse_args()
    if not desktop_platform.IS_MAC:
        raise SystemExit('macOS only.')
    game = desktop_platform.mac_resources(args.game_root) if args.game_root else desktop_platform.find_game_root()
    if game is None:
        raise SystemExit('FM27 for macOS not found; pass --game-root.')
    plugin = game / '../MacOS/game_plugin'
    uuids = subprocess.run(['dwarfdump', '--uuid', str(plugin)], capture_output=True, text=True).stdout
    found = [u for u in BUILDS if f'UUID: {u} (x86_64)' in uuids]
    if not found:
        raise SystemExit(f'Unsupported FM27 build (no known x86_64 LC_UUID; see docs/MACOS.md, "Updating after an FM27 patch"):\n{uuids}')
    uuid = found[0]; build, game_version, engine_version = BUILDS[uuid]
    host = (args.output.resolve() if args.output else ROOT / 'private/engine/fm27_native' / desktop_platform.HOST_NAME)
    native = host.parent
    native.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'port/mac_host/fm27_mac_host.cpp'
    subprocess.run(['clang++', '-std=c++17', '-O2', '-g', '-arch', 'x86_64', '-Wall', '-Wno-unused-function',
                    '-Wno-deprecated-declarations', f'-DFM27_MAC_BUILD={build}', '-o', str(host), str(source)], check=True)
    subprocess.run(['codesign', '--force', '--sign', '-', str(host)], check=True)
    digest = hashlib.sha256(plugin.read_bytes()).hexdigest()
    profile = {'platform': 'macos-x86_64', 'reference_sha256': digest, 'lc_uuid_x86_64': uuid,
               'game_version': game_version, 'build': build, 'engine_version': engine_version,
               'note': 'Generated locally from the user\'s own install; not for publication.'}
    (native / 'engine_compat_profile.json').write_text(json.dumps(profile, indent=1) + '\n', encoding='utf8')
    print(f'Built {host} (x86_64, FM27 {game_version}, engine word 0x{engine_version:08x}) for {game}')
    print(f'game_plugin sha256 {digest}')
    policy_table(host, native, engine_version)


if __name__ == '__main__':
    main()
