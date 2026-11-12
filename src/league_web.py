"""The app's League page, server side: start, follow, stop and resume leagues (src/league.py) in the background.

Leagues live in the app's data folder (leagues/<id>/), never in the repository. One league runs at a time.
"""
import base64, json, os, re, sys, threading, time
from pathlib import Path

import league

GAMES = Path.home() / 'Library/Application Support/Sports Interactive/Football Manager 27/games'
STATE = {}   # league id -> {'thread', 'stop' (Event), 'stage', 'error'}
_clubs = {}
_lock = threading.Lock()


def _study(app):
    for p in ('scripts', 'port/validation'):
        if str(league.ROOT / p) not in sys.path: sys.path.insert(0, str(league.ROOT / p))
    import study
    study._app = app   # the running server, not a second copy of it
    return study


def folder(app):
    p = app.RUNS.parent / 'leagues'; p.mkdir(parents=True, exist_ok=True); return p


def fmsave_available():
    try: import fmsave  # noqa: F401
    except ImportError: return False
    return True


def options(app):
    study = _study(app)
    rows = app.SAVED_MATCHES.list()['matches']
    own = [r for r in rows if r.get('path') and '/Other_clubs/' not in r['path']]
    other = [r for r in rows if r.get('path') and '/Other_clubs/' in r['path']]
    pick = lambda r: {'path': r['path'], 'label': f"{r['home']} v {r['away']} ({r['competition']})", 'modified': r['modified']}
    # a neutral template by default: the newest Premier League match between two other clubs, if any were imported
    # (clubs named "Unknown" when fmsave was missing at import: still neutral, used if nothing better)
    neutral = [r for r in other if 'Unknown' not in (r['home'], r['away'])] or other
    ref = league.reference_squads()
    return {'presets': sorted(study.presets(folder(app))),
            'reference': {'tiers': [{'id': k, 'label': v['label']} for k, v in ref['tiers'].items()], 'calibration': ref['calibration']},
            'own_matches': [pick(r) for r in own], 'other_matches': [pick(r) for r in other],
            'default_template': (max(neutral, key=lambda r: r['modified'])['path'] if neutral else
                                 max(own, key=lambda r: r['modified'])['path'] if own else None),
            'fmsave': fmsave_available(),
            'saves': [p.name for p in sorted(GAMES.glob('*.fm'), key=os.path.getmtime, reverse=True)] if GAMES.is_dir() else [],
            'engine': (app.ENGINE_COMPATIBILITY or {}).get('profile'), 'levelled_note': league.LEVELLED_NOTE,
            'workers': app.BATCH_LIMITS.get('recommended', 4), 'max_workers': app.BATCH_LIMITS.get('maximum', 8)}


def clubs(app, save_name):
    if not fmsave_available(): raise ValueError('Reading a save needs fmsave: .venv/bin/pip install fmsave')
    path = GAMES / Path(save_name).name
    if not path.is_file(): raise ValueError('Save not found')
    if path not in _clubs:
        _study(app); import squad_from_save
        _clubs[path] = sorted(c for c, rows in squad_from_save.read_clubs(path).items() if len(rows) >= 16)
    return {'clubs': _clubs[path]}


def _state(lid):
    s = STATE.get(lid)
    if s and s['thread'].is_alive(): return 'stopping' if s['stop'].is_set() else s.get('stage', 'running')
    if s and s.get('error'): return 'error'
    return None


def status(app, lid):
    out = folder(app) / Path(lid).name
    if not (out / 'config.json').is_file(): raise ValueError('League not found')
    cfg = json.loads((out / 'config.json').read_text(encoding='utf8'))
    res = league.table(out) if (out / 'meta.json').is_file() else {'table': [], 'completed': 0, 'total': 0}
    live = _state(lid)
    res['state'] = live or ('complete' if res['total'] and res['completed'] >= res['total'] else 'stopped' if res['total'] else 'not built')
    res['error'] = (STATE.get(lid) or {}).get('error'); res['id'] = lid; res['name'] = cfg.get('name') or lid
    return res


def listing(app):
    rows = []
    for d in sorted(folder(app).iterdir(), reverse=True):
        if not (d / 'config.json').is_file(): continue
        cfg = json.loads((d / 'config.json').read_text(encoding='utf8')); done, total = league.progress(d)
        live = _state(d.name)
        st = STATE.get(d.name) or {}
        rows.append({'id': d.name, 'name': cfg.get('name') or d.name, 'teams': len(cfg['teams']), 'seasons': cfg.get('seasons'),
                     'completed': done, 'total': total, 'created': (d / 'config.json').stat().st_mtime,
                     'built': st.get('built'), 'build_total': st.get('build_total'),
                     'state': ('building' if live.startswith('building') or live == 'starting' else live) if live else
                              ('complete' if total and done >= total else 'stopped')})
    return {'leagues': rows}


def _resolve(app, out, data):
    """The page's request -> a league config (uploaded tactic files written into the league folder)."""
    teams = data.get('teams') or []
    if not 2 <= len(teams) <= 20: raise ValueError('Choose 2 to 20 teams')
    presets = set(_study(app).presets(folder(app)))
    own = {r['path'] for r in options(app)['own_matches'] + options(app)['other_matches']}
    names, out_teams = set(), []
    (out / 'tactics').mkdir(parents=True, exist_ok=True)
    for k, t in enumerate(teams):
        name = str(t.get('name') or '').strip()[:60] or f'Team {k + 1}'
        while name in names: name += ' (2)'
        names.add(name)
        tac = t.get('tactic') or {}
        if tac.get('kind') == 'preset':
            if tac.get('style') not in presets: raise ValueError(f'{name}: unknown preset')
            tactic = {'kind': 'preset', 'style': tac['style']}
        elif tac.get('kind') == 'upload':
            if tac.get('token'):   # uploaded earlier through /api/league/upload
                src = folder(app) / '_uploads' / (re.sub(r'[^0-9a-f]', '', str(tac['token']))[:32] + '.fmf')
                if not src.is_file(): raise ValueError(f'{name}: the tactic file is no longer here; choose it again')
                raw = src.read_bytes()
            else: raw = base64.b64decode(tac.get('file_base64') or '')
            if not raw or len(raw) > 4_000_000: raise ValueError(f'{name}: empty or too large tactic file')
            f = out / 'tactics' / (re.sub(r'[^A-Za-z0-9 ._-]', '_', Path(tac.get('filename') or name).stem)[:80] + '.fmf')
            f.write_bytes(raw); tactic = {'kind': 'fmf', 'path': str(f)}
        else: raise ValueError(f'{name}: choose a tactic')
        sq = t.get('squad') or {'kind': 'reference', 'tier': 'pl-middle'}; kind = sq.get('kind')
        if kind == 'reference':
            if sq.get('tier') not in league.reference_squads()['tiers']: raise ValueError(f'{name}: unknown reference squad')
            squad = {'kind': 'reference', 'tier': sq['tier']}
        elif kind == 'match':
            if sq.get('match') not in own: raise ValueError(f'{name}: choose one of your saved or imported matches')
            squad = {'kind': 'match', 'match': sq['match'], 'side': 1 if int(sq.get('side', 0)) else 0}
        elif kind == 'save':
            if not fmsave_available(): raise ValueError('Squads from a save need fmsave: .venv/bin/pip install fmsave')
            path = GAMES / Path(sq.get('save') or '').name
            if not path.is_file() or not sq.get('club'): raise ValueError(f'{name}: choose a save and a club')
            squad = {'kind': 'save', 'save': str(path), 'club': sq['club']}
        elif kind == 'levelled':
            squad = {'kind': 'levelled', 'value': max(1, min(20, int(sq.get('value', 12))))}
        else: raise ValueError(f'{name}: choose a squad')
        out_teams.append({'name': name, 'tactic': tactic, 'squad': squad, 'familiarity': max(0, min(100, int(t.get('familiarity', data.get('familiarity', 70)))))})
    base = data.get('base_match'); bases = [b for b in (base if isinstance(base, list) else [base]) if b]
    if not bases or any(b not in own for b in bases): raise ValueError('Choose the template match from your saved or imported matches')
    base = bases[0] if len(bases) == 1 else bases
    return {'name': str(data.get('name') or '').strip()[:80], 'teams': out_teams, 'base_match': base,
            'seasons': max(1, min(50, int(data.get('seasons', 2)))), 'familiarity': max(0, min(100, int(data.get('familiarity', 70)))),
            'equal_start': bool(data.get('equal_start', True)), 'home_and_away': True}


def resume_interrupted(app):
    """At start-up: resume the league that was running when the app last stopped (its folder holds a 'running' marker)."""
    for d in sorted(folder(app).iterdir(), reverse=True):
        marker = d / 'running'
        if not marker.is_file(): continue
        try: workers = int(marker.read_text().strip() or 3)
        except ValueError: workers = 3
        try: resume(app, {'id': d.name, 'workers': workers}); print('resumed league', d.name, flush=True)
        except Exception as e: print('could not resume league', d.name, e, flush=True)
        break   # one league at a time


def _run(app, lid, out, cfg, workers, build):
    s = STATE[lid]
    marker = out / 'running'; marker.write_text(str(workers))   # removed when the league finishes or is stopped
    try:
        if build:
            s['stage'] = 'building fixtures'; s['built'] = 0; s['build_total'] = len(cfg['teams'])
            try: league.build(app, cfg, out, say=lambda line: s.update(stage=f'building fixtures: {line}', built=s['built'] + 1), stop=s['stop'].is_set)
            except league.Stopped: return   # stopped while building: resume builds again
        s['stage'] = 'running'
        league.run(out, workers, stop=s['stop'].is_set)
    except Exception as e:
        s['error'] = str(e)[:400]
    finally:   # finished, stopped or failed: not resumed at the next start (a killed app never gets here)
        marker.unlink(missing_ok=True)


def _launch(app, lid, out, cfg, workers, build):
    with _lock:
        if any(v['thread'].is_alive() for v in STATE.values()): raise ValueError('A league is already running')
        app.desktop_engine.require_available(app.ENGINE_COMPATIBILITY)
        STATE[lid] = {'stop': threading.Event(), 'stage': 'starting', 'error': None}
        STATE[lid]['thread'] = threading.Thread(target=_run, args=(app, lid, out, cfg, workers, build), daemon=True)
        STATE[lid]['thread'].start()


def start(app, data):
    _study(app)
    lid = time.strftime('%Y%m%d-%H%M%S'); out = folder(app) / lid
    cfg = _resolve(app, out, data)
    workers = max(1, min(int(data.get('workers', 4)), app.BATCH_LIMITS.get('maximum', 8)))
    _launch(app, lid, out, cfg, workers, build=True)
    return {'id': lid}


def resume(app, data):
    _study(app)   # the league code imports the study helpers (fixtures still to build)
    lid = Path(str(data.get('id'))).name; out = folder(app) / lid
    if not (out / 'config.json').is_file(): raise ValueError('League not found')
    cfg = json.loads((out / 'config.json').read_text(encoding='utf8'))
    workers = max(1, min(int(data.get('workers', 4)), app.BATCH_LIMITS.get('maximum', 8)))
    _launch(app, lid, out, cfg, workers, build=not (out / 'jobs.json').is_file())
    return {'id': lid}


def upload(app, data):
    """One tactic file, stored once in the leagues folder; the page then refers to it by a short token."""
    import hashlib
    raw = base64.b64decode(data.get('file_base64') or '')
    if not raw: raise ValueError('Empty tactic file')
    if len(raw) > 4_000_000: raise ValueError(f'{data.get("filename") or "This file"} is {len(raw) // 1_000_000} MB: too large for an FM27 tactic file')
    token = hashlib.sha256(raw).hexdigest()[:32]
    d = folder(app) / '_uploads'; d.mkdir(exist_ok=True); (d / f'{token}.fmf').write_bytes(raw)
    return {'token': token, 'size': len(raw)}


def delete(app, data):
    lid = Path(str(data.get('id'))).name; out = folder(app) / lid
    if not (out / 'config.json').is_file(): raise ValueError('League not found')
    if _state(lid): raise ValueError('Stop the league first')
    import shutil
    shutil.rmtree(out); STATE.pop(lid, None)
    return {'deleted': lid}


def stop(data):
    s = STATE.get(Path(str(data.get('id'))).name)
    if s: s['stop'].set()
    return {'accepted': bool(s)}


def get(app, path, query):
    """GET /api/league/... -> (value, content type) or None."""
    parts = path.strip('/').split('/')
    if path == '/api/league/options': return options(app), None
    if path == '/api/league/list': return listing(app), None
    if len(parts) == 4 and parts[2] == 'status': return status(app, parts[3]), None
    if len(parts) == 4 and parts[2] == 'csv': return league.to_csv(status(app, parts[3])).encode(), 'text/csv; charset=utf-8'
    return None


def post(app, path, data):
    if path == '/api/league/start': return start(app, data)
    if path == '/api/league/resume': return resume(app, data)
    if path == '/api/league/stop': return stop(data)
    if path == '/api/league/delete': return delete(app, data)
    if path == '/api/league/upload': return upload(app, data)
    if path == '/api/league/clubs': return clubs(app, data.get('save'))
    return None
