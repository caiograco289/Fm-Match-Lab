"""Attribute values by position from random configurations: every match measures every attribute in every position.

In each match every attribute of every starter of the tested side moves by +5 or -5 at random (clamped to 1-20), so
one run estimates all attribute-by-position effects at once, by regression, far more precisely than changing one
attribute at a time for the same number of matches. The goalkeeper is included (with his own attributes).

  python port/validation/random_study.py build OUT [--configs 50000] [--style Gegenpress]
  python port/validation/random_study.py pilot OUT [--workers 7]     # the first 320 configurations, then the checks
  python port/validation/random_study.py run OUT [--workers 7]       # everything (resumable)
  python port/validation/random_study.py report OUT                  # OUT/report.md

Neutral ground as in the roadmap studies: the synthetic Premier League middle-eight squad on both sides, the tested
style against four presets, home and away, on two templates, tactical familiarity held at 80. Each configuration is
played once, on its own seed; the 16 settings (template, opponent, venue) rotate and get their own constant in the
regression. Design: OUT/design.npz (level change per configuration, starter and field, after clamping).
"""
import argparse, copy, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in ('scripts', 'src', 'port/validation'): sys.path.insert(0, str(ROOT / p))

PROFILE = ['pressure', 'professionalism', 'temperament', 'sportsmanship', 'ambition', 'loyalty', 'adaptability']
GK_ONLY = {'Handling', 'AerialReach', 'CommandOfArea', 'Communication', 'Kicking', 'Throwing', 'OneOnOnes', 'Reflexes',
           'RushingOut', 'TendencyToPunch', 'Eccentricity'}
SKIP = {'LeftFoot', 'RightFoot'}
GROUPS = ['GK', 'FB', 'CB', 'DM', 'AM', 'ST']
GROUP_OF = {'GK': 'GK', 'FB': 'FB', 'CB': 'CB', 'DM/CM': 'DM', 'AM/W': 'AM', 'ST': 'ST'}
STEP = 5
LABEL = {'pressure': 'Pressure', 'professionalism': 'Professionalism', 'temperament': 'Temperament', 'sportsmanship': 'Sportsmanship',
         'ambition': 'Ambition', 'loyalty': 'Loyalty', 'adaptability': 'Adaptability'}


def fields():
    """[(name, kind, id)]: kind 'a' = attribute (stored x5, 5-100), 'p' = profile field (1-20)."""
    import study
    a = sorted(((aid, label) for aid, label in study.attribute_ids().values()), key=lambda x: x[0])
    return [(label, 'a', aid) for aid, label in a if label not in SKIP] + [(LABEL[f], 'p', f) for f in PROFILE]


def nice(label):
    import re
    return {'OneOnOnes': 'One on Ones', 'FreeKickTaking': 'Free Kicks', 'LongShots': 'Long Shots', 'OffTheBall': 'Off The Ball'}.get(
        label, re.sub(r'(?<!^)(?=[A-Z])', ' ', label))


def applies(label, group):
    return group == 'GK' or label not in GK_ONLY


def build(a):
    import numpy as np, study, league, neutral_study as ns
    A = study.app(); out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True); (out / 'bins').mkdir(exist_ok=True)
    b = league.Builder(A, out); fam = 80
    env = {'FM27_MAC_EXEC_FIELDS': ','.join(f'{x}:{o}={fam}' for x in (0, 1) for o in league.AREAS) + ',' +
           ','.join(f'{x}:{o}=50' for x in (0, 1) for o in (0x19, 0x1a))}
    F = fields(); rng = np.random.default_rng(a.seed)
    templates = [ns.template_path(t) for t in ns.DEFAULT_TEMPLATES]
    bases, settings = [], []
    for k, path in enumerate(templates):
        base = league.same_squad_size(A.validate_scenario(A.SAVED_MATCHES.open(path).default))
        for opp in ns.PANEL:
            for venue in (0, 1):
                s0 = b.side(copy.deepcopy(base), venue, {'squad': {'kind': 'reference', 'tier': 'pl-middle'}, 'tactic': {'kind': 'preset', 'style': a.style}})
                s0 = b.side(s0, 1 - venue, {'squad': {'kind': 'reference', 'tier': 'pl-middle'}, 'tactic': {'kind': 'preset', 'style': opp}})
                league.equalise(s0); bases.append(A.validate_scenario(s0)); settings.append({'template': Path(path).name, 'path': path, 'opponent': opp, 'venue': venue})
    t0 = bases[0]['teams'][settings[0]['venue']]
    xi = [(slot, GROUP_OF[ns.position_group(ip)], ip) for slot, (i, ip, oop) in enumerate(ns.starters(t0))]
    for s, st in zip(bases, settings):   # every setting must have the same XI in the same order
        assert [ns.position_group(ip) for _, ip, _ in ns.starters(s['teams'][st['venue']])] == [ns.position_group(ip) for _, _, ip in xi]
    n = a.configs
    X = np.zeros((n, len(xi), len(F)), dtype=np.int8)
    jobs, problems = [], []
    for c in range(n):
        k = c % len(bases); st = settings[k]; seed = c // len(bases) + 1
        s = copy.deepcopy(bases[k]); team = s['teams'][st['venue']]
        signs = rng.choice((-1, 1), size=(len(xi), len(F))).tolist()
        for j, (i, ip, oop) in enumerate(ns.starters(team)):
            p = team['players'][i]; g = xi[j][1]
            for f, (label, kind, key) in enumerate(F):
                if not applies(label, g): continue
                if kind == 'a':
                    old = p['attributes'][key]; new = min(100, max(5, old + signs[j][f] * STEP * 5)); p['attributes'][key] = new
                    X[c, j, f] = round((new - old) / 5)
                else:
                    old = p['native_profile'][key]; new = min(20, max(1, old + signs[j][f] * STEP)); p['native_profile'][key] = new
                    X[c, j, f] = new - old
        v = A.validate_scenario(s)
        if c < 50:   # the validator must keep every change
            vt = v['teams'][st['venue']]
            for j, (i, ip, oop) in enumerate(ns.starters(vt)):
                want, got = team['players'][i], vt['players'][i]
                if want['attributes'] != got['attributes'] or any(want['native_profile'][f] != got['native_profile'][f] for f in PROFILE):
                    problems.append(f'configuration {c}, starter {j}: the validator changed the edited values')
        f_ = out / 'bins' / f'{c}.bin'; f_.write_bytes(A.encode_scenario(v))
        jobs.append(['R', f'R|{c}|{k}', st['path'], str(f_), env, 1, seed])
        if c % 2000 == 0: print(f'built {c} of {n}', flush=True)
    np.savez_compressed(out / 'design.npz', X=X, setting=np.arange(n) % len(bases))
    (out / 'jobs_all.json').write_text(json.dumps(jobs)); (out / 'jobs.json').write_text(json.dumps(jobs))
    meta = {'title': f'Attribute values by position, random configurations ({a.style})', 'style': a.style, 'configs': n, 'step': STEP,
            'familiarity': fam, 'settings': [{k_: v_ for k_, v_ in st.items() if k_ != 'path'} for st in settings],
            'xi': [{'slot': j, 'group': g, 'position': ip} for j, g, ip in xi], 'fields': [nice(l) for l, _, _ in F],
            'field_kind': [k_ for _, k_, _ in F], 'gk_only': [nice(l) for l in GK_ONLY], 'problems': problems}
    (out / 'meta.json').write_text(json.dumps(meta, indent=1))
    print(f'{n} configurations; {len(problems)} validator problems')
    for p in problems[:10]: print('  PROBLEM', p)


def pilot(a):
    import overnight
    out = Path(a.out).resolve(); jobs = json.loads((out / 'jobs_all.json').read_text())
    (out / 'jobs.json').write_text(json.dumps(jobs[:320])); overnight.run(out, a.workers)
    (out / 'jobs.json').write_text(json.dumps(jobs))
    rows = [json.loads(l) for l in open(out / 'results.jsonl')] if (out / 'results.jsonl').exists() else []
    meta = json.loads((out / 'meta.json').read_text())
    ok = len({r['cond'] for r in rows}) >= 320 and not meta['problems']
    print(f"pilot: {len(rows)} results for 320 configurations; validator problems {len(meta['problems'])}; {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


def run(a):
    import overnight
    out = Path(a.out).resolve(); (out / 'jobs.json').write_text((out / 'jobs_all.json').read_text()); overnight.run(out, a.workers)


# ---- analysis ----
def outcomes(out, meta):
    """{configuration: measures of the tested side}"""
    import league
    res = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); _, c, k = r['cond'].split('|'); me = meta['settings'][int(k)]['venue']; o = 1 - me
        gf, ga = r['score'][me], r['score'][o]
        res[int(c)] = {'xPts': league.xpts(r['xg'][me], r['xg'][o]), 'Pts': 3 if gf > ga else 1 if gf == ga else 0,
                       'GD': gf - ga, 'xGD': r['xg'][me] - r['xg'][o], 'GF': gf, 'GA': ga, 'xGF': r['xg'][me], 'xGA': r['xg'][o]}
    return res


def regress(y, Z, S, nsettings):
    """OLS of y on Z with one constant per setting; returns (beta, se, covariance) for Z's columns."""
    import numpy as np
    D = np.zeros((len(y), nsettings)); D[np.arange(len(y)), S] = 1
    M = np.hstack([Z, D]); XtX = M.T @ M
    beta = np.linalg.solve(XtX, M.T @ y); res = y - M @ beta
    s2 = res @ res / (len(y) - M.shape[1]); cov = np.linalg.inv(XtX) * s2
    k = Z.shape[1]
    return beta[:k], np.sqrt(np.diag(cov))[:k], cov[:k, :k]


def chi2_sf(x, k):
    a = k / 2; x = x / 2
    if x <= 0: return 1.0
    if x < a + 1:
        s = term = 1 / a; n = 1
        while abs(term) > 1e-12: term *= x / (a + n); s += term; n += 1
        return max(0.0, 1 - s * math.exp(-x + a * math.log(x) - math.lgamma(a)))
    b = x + 1 - a; c = 1e300; d = 1 / b; h = d; i = 1
    while True:
        an = -i * (i - a); b += 2; d = an * d + b; c = b + an / c; d = 1 / d; de = d * c; h *= de; i += 1
        if abs(de - 1) < 1e-12: break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def analyse(out):
    """Per measure: by-position and team coefficients (per +1 level for ONE player, per game), split-half confirmation,
    and the heterogeneity test across the five outfield groups."""
    import numpy as np
    out = Path(out); meta = json.loads((out / 'meta.json').read_text())
    d = np.load(out / 'design.npz'); X, S = d['X'].astype(float), d['setting']
    res = outcomes(out, meta); idx = np.array(sorted(res)); X, S = X[idx], S[idx]
    groups = [x['group'] for x in meta['xi']]; F = meta['fields']; gk_only = set(meta['gk_only'])
    cols = [(g, f) for g in GROUPS for f, name in enumerate(F) if g == 'GK' or name not in gk_only]
    Z = np.stack([X[:, [j for j, gg in enumerate(groups) if gg == g], f].sum(1) for g, f in cols], 1)
    outfield = [j for j, g in enumerate(groups) if g != 'GK']
    tcols = [f for f, name in enumerate(F) if name not in gk_only]
    Zt = np.hstack([np.stack([X[:, outfield, f].sum(1) for f in tcols], 1), X[:, [groups.index('GK')], :].reshape(len(idx), -1)])
    halves = [(idx // len(meta["settings"])) % 2 == h for h in (0, 1)]   # by blocks: every setting in both halves
    result = {'n': len(idx), 'cols': [[g, F[f]] for g, f in cols], 'measures': {}}
    for m in ('xPts', 'Pts', 'GD', 'xGD', 'GA', 'GF', 'xGA', 'xGF'):
        y = np.array([res[c][m] for c in idx], float)
        b, se, cov = regress(y, Z, S, len(meta['settings']))
        hb = [regress(y[h], Z[h], S[h], len(meta['settings']))[:2] for h in halves]
        bt, set_, _ = regress(y, Zt, S, len(meta['settings']))
        het = {}
        for f in tcols:   # equality across the five outfield groups (Wald, 4 df)
            ii = [cols.index((g, f)) for g in GROUPS[1:]]
            v = b[ii]; C = cov[np.ix_(ii, ii)]; L = np.hstack([np.ones((4, 1)), -np.eye(4)])
            w = float((L @ v) @ np.linalg.solve(L @ C @ L.T, L @ v)); het[F[f]] = [w, chi2_sf(w, 4)]
        result['measures'][m] = {'b': b.tolist(), 'se': se.tolist(), 'half_b': [h[0].tolist() for h in hb], 'half_se': [h[1].tolist() for h in hb],
                                 'team_b': bt[:len(tcols)].tolist(), 'team_se': set_[:len(tcols)].tolist(), 'team_fields': [F[f] for f in tcols], 'het': het}
    (out / 'analysis.json').write_text(json.dumps(result))
    return meta, result


def report(a):
    out = Path(a.out).resolve(); meta, r = analyse(out)
    cols = [tuple(c) for c in r['cols']]; season = 38
    def cell(m, g, f):
        x = r['measures'][m]; i = cols.index((g, f)); b, se = x['b'][i], x['se'][i]
        conf = all(abs(hb[i] / hs[i]) > 2 and (hb[i] > 0) == (b > 0) for hb, hs in zip(x['half_b'], x['half_se']))
        return f"{season * b:+.2f}{'*' if conf else ''}"
    lines = [f"# {meta['title']}", '', f"{r['n']} matches, one random configuration each (every attribute of every starter "
             f"+{STEP} or −{STEP}). Per season (38 games) for +1 level in ONE player of that position; * = |t| > 2 with the "
             "same sign in both random halves. 'Team' is one coefficient for all ten outfield players. 'Differ?' is the "
             "p value of the test that the five outfield positions are equal.", '']
    for m, title in (('xPts', 'Expected points'), ('Pts', 'Points'), ('GD', 'Goal difference')):
        x = r['measures'][m]; tf = x['team_fields']
        order = sorted(range(len(tf)), key=lambda i: -x['team_b'][i])
        lines += [f'## {title}', '', '| Attribute | Team | ST | AM | DM | FB | CB | Differ? |', '|---|---|---|---|---|---|---|---|']
        for i in order:
            f = tf[i]; tb, ts = x['team_b'][i], x['team_se'][i]
            lines.append(f"| {f} | {season * tb:+.2f} ({tb / ts:+.1f}) | " + ' | '.join(cell(m, g, f) for g in ('ST', 'AM', 'DM', 'FB', 'CB'))
                         + f" | {x['het'][f][1]:.3f} |")
        ses = {g: 1.96 * season * sorted(x['se'][cols.index((g, f))] for f in tf)[len(tf) // 2] for g in ('ST', 'AM', 'DM', 'FB', 'CB')}
        lines += ['', 'Typical 95% margin: ' + ', '.join(f'{g} ±{v:.2f}' for g, v in ses.items()), '']
    lines += ['## Goalkeeper', '', '| Attribute | Goals against | xG against | Points | Expected points |', '|---|---|---|---|---|']
    gk = [(f) for g, f in cols if g == 'GK']
    for f in sorted(gk, key=lambda f: r['measures']['GA']['b'][cols.index(('GK', f))]):
        lines.append(f"| {f} | {cell('GA', 'GK', f)} | {cell('xGA', 'GK', f)} | {cell('Pts', 'GK', f)} | {cell('xPts', 'GK', f)} |")
    (out / 'report.md').write_text('\n'.join(lines) + '\n'); print('\n'.join(lines[:60]))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('step', choices=['build', 'pilot', 'run', 'report']); p.add_argument('out')
    p.add_argument('--configs', type=int, default=50000); p.add_argument('--style', default='Gegenpress')
    p.add_argument('--seed', type=int, default=27); p.add_argument('--workers', type=int, default=7)
    a = p.parse_args(); {'build': build, 'pilot': pilot, 'run': run, 'report': report}[a.step](a)


if __name__ == '__main__':
    main()
