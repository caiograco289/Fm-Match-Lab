"""Actual local engine identity, static compatibility and stable batch inputs."""
import desktop_platform
import hashlib
import json
import os
from pathlib import Path
import subprocess

LEASES = []


def close_leases():
    for stream in LEASES:
        stream.close()
    LEASES.clear()


def require_available(status):
    if not status.get('can_simulate'):
        raise ValueError('Cannot simulate yet: '+status.get('message','Set the game folder and check the diagnostics'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def lease(path):
    LEASES.append(desktop_platform.FileLease(path))


def initialize(root):
    close_leases()
    os.environ.pop('FM27_EXPECTED_DLL_SHA256', None)
    native = root / 'fm27_native'
    selected = os.environ.get('FM27_GAME_ROOT')
    game = desktop_platform.mac_resources(selected) if selected else desktop_platform.find_game_root()
    if game is None:
        return {'policy':'graded-adapter-compatibility-v2','compatible':False,'can_simulate':False,'disposition':'blocked',
                'reason':'missing_resources','message':'Choose the Football Manager 27 install (Steam game folder or fm.app)',
                'selected_game_root':selected}
    os.environ['FM27_GAME_ROOT'] = str(game)
    files, dll = desktop_platform.engine_files(game)
    return _initialize_files(root, native, game, files, dll)


def _initialize_files(root, native, game, files, dll):
    status={'policy':'graded-adapter-compatibility-v2','compatible':False,'can_simulate':False,
            'disposition':'blocked','selected_game_root':str(game.resolve()),
            'actual_dll_sha256':None,'resource_fingerprint':None,
            'whole_file_sha_is_admission_gate':False,'whole_engine_behavior_equivalence_proven':False}
    try:
        missing=[name for name,path in files.items() if not path.is_file()]
        if missing:
            return {**status,'reason':'missing_resources','missing_files':missing,
                    'message':'Choose the complete game install folder; missing: '+', '.join(missing)}
        for path in files.values():
            lease(path)
        env = os.environ.copy()
        env.pop('FM27_EXPECTED_DLL_SHA256', None)
        diagnostic_error=None
        try:
            checked = subprocess.run([str(desktop_platform.host_path(native)),'--check-image',str(dll)],
                                     env=env, capture_output=True, timeout=30)
            rows=[]
            for line in checked.stdout.decode('utf8',errors='replace').splitlines():
                try: rows.append(json.loads(line))
                except ValueError: pass
            diagnostic_error=checked.stderr.decode('utf8',errors='replace')[:2000]
        except (OSError,subprocess.TimeoutExpired) as error:
            rows=[];diagnostic_error=str(error)
        validation = next((r for r in rows if r.get('event')=='native_engine_compatibility'),None)
        if validation and not (validation.get('compatible') or validation.get('trial_allowed')):
            close_leases()
            if validation.get('method')=='lc_uuid_in_file':   # FM27 was updated since the host was built
                built=str(validation.get('profile','')).removeprefix('fm27-').removesuffix('-macos-x86_64')
                return {**status,'reason':'game_build_changed','diagnostics':rows,
                        'message':f'FM27 has been updated since the set-up (the engine host was built for {built}). Close FM27 and run '
                                  '.venv/bin/python scripts/setup.py again. If it reports an unsupported build, this version of the '
                                  'tool does not know the new FM27 build yet: update the repository (docs/MACOS.md lists the supported builds).'}
            return {**status,'reason':validation.get('reason'),'diagnostics':rows,
                    'message':'Key interface or layout mismatch: '+str(validation.get('reason'))+', at '+hex(validation.get('rva',0))}
        actual = sha(dll)
        entries = [{'path':name,'sha256':actual if name=='game_plugin.dll' else sha(path)} for name,path in sorted(files.items())]
        fingerprint = hashlib.sha256(json.dumps(entries,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        profile = json.loads((native/'engine_compat_profile.json').read_text(encoding='utf8'))
        os.environ['FM27_EXPECTED_DLL_SHA256'] = actual
        verified=bool(validation and validation.get('compatible'))
        return {**status,'profile':validation.get('profile') if validation else None,
                'compatible':verified,'can_simulate':True,'trial_allowed':not verified,
                'disposition':'verified' if verified else 'unverified',
                'reason':validation.get('reason') if validation else 'preflight_unavailable',
                'message':'Engine key interfaces check passed' if verified else 'This version has not been verified; trial runs allowed, and every match must still pass native full-time, score and statistics checks.',
                'diagnostics':rows,'diagnostic_error':diagnostic_error,
                'actual_dll_sha256':actual,'resource_fingerprint':fingerprint,
                'reference_dll_sha256':profile['reference_sha256'],
                'original_build_verified':actual==profile['reference_sha256'],
                'whole_file_sha_is_admission_gate':False,'selected_game_root':str(game.resolve()),
                'files':entries,'whole_engine_behavior_equivalence_proven':False}
    except (OSError,ValueError) as error:
        close_leases()
        return {**status,'reason':'resource_access_failed','message':'Cannot read game resources: '+str(error)}
