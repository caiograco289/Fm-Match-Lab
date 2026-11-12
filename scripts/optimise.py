"""Search for better team instructions and mentality for your team, across your saved matches.

The target is one tactic that is strong across a mix of real opponents, not one tailored to a single fixture.
Your saved matches are split by opponent: most are used for the search; every match against a few other opponents is
held out and used only for the final check, so the reported gain is measured on opponents the search never played.
Matches come from the backup of everything FM27 has saved (src/match_backup.py), not only the game's last 10.

  .venv/bin/python scripts/optimise.py runs/opt --team "Your Club"
  .venv/bin/python scripts/optimise.py runs/opt --team "Your Club" --save "<your save>.fm"   # needs fmsave

With --save, the search runs on built matches with your current squad from the save, against many real opponents:
other clubs' matches the game played (scripts/import_other_matches.py; your team takes one side's place, the other
keeps its players and AI manager as the game had them) and this season's fixtures (the opponent's current players,
its XI and tactic picked by its AI manager); every saved match of yours is then held out for the final check.

1. Screen. Several hundred random variations of your tactic (each instruction changed with probability 0.35 to
   another of its options; mentality likewise), only combinations the app's validator accepts, each played on the
   search matches on the same seeds as your unchanged tactic, so every result is a paired difference.
2. Model. A ridge regression of the paired differences on each option (main effects), then on the strongest
   options plus their pairwise interactions. The model predicts the best combinations.
3. Confirm. The top predicted combinations of at most 4 changes are replayed against your tactic on fresh seeds
   (300 paired matches each). The best by expected points is kept if its gain holds (t >= 2.5: it is the best of
   several, so a plain t >= 2 lets chance through too often).
4. Repeat 1-3 around the new tactic (--rounds), then a final check against your starting tactic on the held-out
   matches.

Scoring: expected points (xPts: 3 x P(win) + P(draw), with each side's goals Poisson around its xG) and xG
difference; real points and goals for and against are reported too.

Equal footing: your players' training and match exposure are held at --familiarity (default 70) in all eight
tactical areas for every candidate; the opponent's records are left as saved. Tactical complexity stays as stored
in each saved match: the match engine does not recompute it from the tactic (checked: team complexity is identical
under any tactic), so complex instructions do not pay their in-game cost here. Your team is managed by the
assistant during the match in every replay (a replay of your own recorded in-match changes would undo the tactic).

Resumable: run the same command again and it continues; finished matches are reused. Default size: about 6,000
matches per round (about an hour with 6 workers). Writes OUT/report.md, OUT/best.json (open in the app with "Open
full scenario JSON") and, when the export works, OUT/best.fmf.
"""
import argparse, copy, hashlib, json, math, os, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts')); sys.path.insert(0, str(ROOT / 'src'))
import match_backup
# matches opened once stay opened (reading 100+ matches through the engine takes minutes the first time)
os.environ.setdefault('FM27_DESKTOP_DATA', str(match_backup.backup_folder().parent / 'opened_matches'))
import study   # sets up paths and the app environment
from study import app, AREAS

MEASURES = ('xPts', 'xGD', 'pts', 'xGF', 'xGA', 'GF', 'GA')


def xpts(a, b, cap=12):
    """3 P(win) + P(draw) with goals Poisson(a) and Poisson(b)."""
    pa = [math.exp(-a) * a ** k / math.factorial(k) for k in range(cap)]
    pb = [math.exp(-b) * b ** k / math.factorial(k) for k in range(cap)]
    win = sum(pa[i] * pb[j] for i in range(cap) for j in range(i)); draw = sum(pa[i] * pb[i] for i in range(cap))
    return 3 * win + draw


def ridge(X, y, lam):
    """Ridge fit with an intercept left free; returns weights and their sandwich standard errors."""
    import numpy as np
    X = np.asarray(X, float); y = np.asarray(y, float)
    X1 = np.hstack([np.ones((len(y), 1)), X]); P = lam * np.eye(X1.shape[1]); P[0, 0] = 0
    A = X1.T @ X1 + P; Ai = np.linalg.inv(A); w = Ai @ X1.T @ y
    resid = y - X1 @ w; s2 = float(resid @ resid) / max(1, len(y) - X1.shape[1] // 2)
    cov = s2 * Ai @ (X1.T @ X1) @ Ai
    return w[1:], np.sqrt(np.clip(np.diag(cov)[1:], 1e-12, None)), w[0]


def cv_lambda(X, y, lams=(0.3, 1, 3, 10, 30, 100), folds=5):
    import numpy as np
    X = np.asarray(X, float); y = np.asarray(y, float); idx = np.arange(len(y)); best = None
    for lam in lams:
        err = 0.0
        for f in range(folds):
            test = idx % folds == f; w, _, b = ridge(X[~test], y[~test], lam); err += float(((X[test] @ w + b - y[test]) ** 2).sum())
        if best is None or err < best[0]: best = (err, lam)
    return best[1]


class Search:
    def __init__(self, a):
        self.a = a; self.out = Path(a.out).resolve(); self.out.mkdir(parents=True, exist_ok=True)
        (self.out / 'bins').mkdir(exist_ok=True)
        self.lines = []; self.data = {}; A = self.A = app()
        found = self.find_matches()
        self.bases = {}
        for name, path, side in found:
            s = A.validate_scenario(A.SAVED_MATCHES.open(path).default)
            if a.start_tactic: s = study.apply_tactic(s, side, study.tactic_sources([a.start_tactic], self.out)[0], self.out)
            s['teams'][side]['in_match'] = 'assistant'
            self.bases[name] = (A.validate_scenario(s), path, side)
        t = self.bases[found[0][0]][0]['teams'][found[0][2]]   # the newest match's instructions are "your tactic"
        self.start = {'instructions': dict(t['instructions']), 'mentality': t['mentality']}
        if a.save:   # search on built matches (your current squad against real opponents); every saved match is held out
            self.search = self.build_pool(found); self.held = found
        else:
            if a.holdout: hold = {h.replace(' ', '_') for h in a.holdout}
            else: hold = {self.opponent(found[i]) for i in range(2, len(found), 3)}   # the opponents of every third match by date
            self.search = [m for m in found if m[0] not in hold and self.opponent(m) not in hold]
            self.held = [m for m in found if m not in self.search]
        if not self.search or not self.held: raise SystemExit('Need at least one search and one held-out match')
        self.check = [self.search[0][0], self.held[0][0]]   # validity of a configuration is checked on these two

    def build_pool(self, real):
        """Matches with your current squad (from the save) and tactic against real opponents:
        - other clubs' matches the game played (Other_clubs in the backup, see scripts/import_other_matches.py): your
          team takes one side's place; the other side keeps its players, start state and AI manager as the game had them;
        - your fixtures this season in the save: the opponent's current players in one of your saved matches (at the
          same venue), its XI and tactic picked by its AI manager during the match preparation.
        Only opponents at least as strong as the weaker of your saved matches' opponents are used."""
        import squad_from_save, desktop_saved_matches
        a, A = self.a, self.A; save = Path(a.save).expanduser(); clubs = squad_from_save.read_clubs(save)
        club = a.club or next((c for c in clubs if c.lower() == a.team.lower()), None) or \
            next((c for c in sorted(clubs, key=len) if a.team.lower() in c.lower()), None)
        if not club or club not in clubs: raise SystemExit(f'Club {a.club or a.team!r} not found in the save; give --club')
        ours = clubs[club]; name0, _, side0 = real[0]; template = self.bases[name0][0]['teams'][side0]
        TACTIC = ('phases', 'instructions', 'mentality', 'native_extra_team_bits', 'tactic_name')

        def ours_on(s, side):
            s['teams'][side].update({k: copy.deepcopy(template[k]) for k in TACTIC})
            s = squad_from_save.apply_squad(A, s, side, ours); s['teams'][side]['in_match'] = 'assistant'
            return A.validate_scenario(s)

        def xi_ca(t): v = [t['players'][i]['native_profile'].get('current_ability') or 0 for i in t['lineup'][:11]]; return sum(v) / max(1, len(v))
        real_ca = sorted(xi_ca(self.bases[n][0]['teams'][1 - s]) for n, _, s in real)
        floor = a.min_opponent_ca if a.min_opponent_ca is not None else real_ca[len(real_ca) // 4]
        cands = []
        folder = match_backup.source_folder() / 'Other_clubs'
        for f in sorted(folder.glob('*_VER_fm.pkm')):
            m = desktop_saved_matches.NAME.match(f.name)
            try: base = A.validate_scenario(A.SAVED_MATCHES.open(str(f)).default)
            except Exception: continue
            for side in (0, 1):
                opp = m['away' if side == 0 else 'home'].replace('_', ' ')
                if opp == club or m['home' if side == 0 else 'away'].replace('_', ' ') == club: continue
                if xi_ca(base['teams'][1 - side]) < floor: continue
                cands.append((f'{f.stem[:-7]}@{"home" if side == 0 else "away"}', str(f), side, opp,
                              lambda base=base, side=side: ours_on(copy.deepcopy(base), side)))
        n_other = len(cands)
        import fmsave, warnings
        warnings.simplefilter('ignore')
        with fmsave.open(save) as s:
            fx = [x for x in s.fixtures() if club in (x.home_club_name, x.away_club_name)]
        season = max((x.season_start_year for x in fx if x.season_start_year), default=None)
        seen = set(); homes = [m for m in real if m[2] == 0]; aways = [m for m in real if m[2] == 1]
        for x in fx:
            if x.season_start_year != season: continue
            side = 0 if x.home_club_name == club else 1; opp = x.away_club_name if side == 0 else x.home_club_name
            rows = clubs.get(opp)
            if not rows or (opp, side) in seen or len(rows) < 16: continue
            if sum(r['current_ability'] or 0 for r in rows[:11]) / 11 < floor: continue
            seen.add((opp, side)); host = (homes if side == 0 else aways) or real; cont = host[len(seen) % len(host)]

            def build(cont=cont, side=side, rows=rows):
                s = copy.deepcopy(self.bases[cont[0]][0]); t = s['teams'][1 - side]
                keep = {k: copy.deepcopy(t[k]) for k in ('lineup', 'phases', 'instructions', 'mentality', 'in_match')}
                s = squad_from_save.apply_squad(A, s, 1 - side, rows); s['teams'][1 - side].update(keep)   # the AI picks XI and tactic
                return ours_on(s, side)
            cands.append((f'{opp.replace(" ", "_")}@{"home" if side == 0 else "away"}-{season}', cont[1], side, opp, build))
        n_fixtures = len(cands) - n_other
        rng = random.Random(a.seed); rng.shuffle(cands); cands = cands[:a.pool]
        pool = []
        for name, path, side, opp, build in cands:
            try: self.bases[name] = (build(), path, side); pool.append((name, path, side))
            except Exception as e: print('skipped', name, str(e)[:100])
        from_fixtures = sum('-' in name.split('@')[1] for name, _, _ in pool)
        self.pool_note = (f'{len(pool)} built matches with {club}\'s current squad from the save: {len(pool) - from_fixtures} from other clubs\' '
                          f'matches (of {n_other} eligible) and {from_fixtures} from this season\'s fixtures (of {n_fixtures}); opponents\' XI '
                          f'average current ability at least {floor:.0f}, the lower quarter of your saved matches\' opponents')
        return sorted(pool)

    def find_matches(self):
        a = self.a; import exec_real
        if a.match:
            out = []
            for f in a.match:
                p = Path(f).expanduser().resolve(); name = p.stem.replace('_VER_fm', '')
                home, away = name.rsplit('_', 1)[0].split('_v_'); team = a.team.replace(' ', '_')
                if team not in (home, away): raise SystemExit(f'{p.name} is not a match of {a.team}')
                out.append((name, str(p), 0 if home == team else 1))
            return out
        found = sorted(exec_real.matches(a.team.replace(' ', '_')), key=lambda m: Path(m[1]).stat().st_mtime, reverse=True)
        if not found: raise SystemExit(f'No saved matches of {a.team}')
        return [(n, str(Path(p).resolve()), s) for n, p, s in found]

    def opponent(self, m): return m[0].rsplit('_', 1)[0].split('_v_')[1 - m[2]]

    # configurations: {'instructions': {group id: option id}, 'mentality': id}
    def key(self, cfg): return hashlib.sha1(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:12]

    def blob(self, cfg, name):
        s, path, side = self.bases[name]; s = copy.deepcopy(s); t = s['teams'][side]
        t['instructions'] = dict(cfg['instructions']); t['mentality'] = cfg['mentality']
        if self.A.team_conflicts(t['instructions']): return None
        try: v = self.A.validate_scenario(s)
        except Exception: return None
        u = v['teams'][side]
        if u['mentality'] != cfg['mentality'] or any(u['instructions'].get(k) != x for k, x in cfg['instructions'].items()): return None
        return self.A.encode_scenario(v)

    def valid(self, cfg):
        k = self.key(cfg)
        if k not in self._valid: self._valid[k] = all(self.blob(cfg, n) is not None for n in self.check)
        return self._valid[k]
    _valid = {}

    def play(self, plan):
        """plan: list of (cfg, cells), cells = [(match name, seed)]. Plays whatever is not played yet."""
        import overnight
        jobs = []
        for cfg, cells in plan:
            k = self.key(cfg); seeds = {}
            for name, s in cells: seeds.setdefault(name, []).append(s)
            for name, ss in seeds.items():
                _, path, side = self.bases[name]
                f = self.out / 'bins' / f'{k}_{hashlib.sha1(name.encode()).hexdigest()[:8]}.bin'
                if not f.is_file():
                    b = self.blob(cfg, name)
                    if b is None: continue   # not valid on this match (checked on two matches only)
                    f.write_bytes(b)
                env = {'FM27_MAC_EXEC_FIELDS': ','.join(f'{side}:{o}={self.a.familiarity}' for o in AREAS)}
                ss = sorted(set(ss)); i = 0
                while i < len(ss):   # one job per run of consecutive seeds
                    j = i
                    while j + 1 < len(ss) and ss[j + 1] == ss[j] + 1: j += 1
                    jobs.append(['O', f'{name}|{k}', path, str(f), env, ss[j] - ss[i] + 1, ss[i]]); i = j + 1
        self.load()
        todo = sum(n - sum((c.split('|')[0], s) in self.data.get(c.split('|')[1], {}) for s in range(f0, f0 + n)) for _, c, _, _, _, n, f0 in jobs)
        if todo:
            (self.out / 'jobs.json').write_text(json.dumps(jobs))
            print(f'  playing {todo} matches', flush=True)
            overnight.run(self.out, self.a.workers); self.load()

    def load(self):
        f = self.out / 'results.jsonl'
        if not f.is_file(): return
        sides = {n: s for n, (_, _, s) in self.bases.items()}; self.data = {}
        for line in open(f):
            r = json.loads(line); name, k = r['cond'].split('|')
            if name not in sides: continue
            s = sides[name]; o = 1 - s; g, c = r['score'][s], r['score'][o]
            self.data.setdefault(k, {})[(name, r['seed'])] = {
                'pts': 3 if g > c else 1 if g == c else 0, 'xPts': xpts(r['xg'][s], r['xg'][o]), 'xGD': r['xg'][s] - r['xg'][o],
                'xGF': r['xg'][s], 'xGA': r['xg'][o], 'GF': g, 'GA': c}

    def diffs(self, cfg, ref, keys, m):
        a, b = self.data.get(self.key(cfg), {}), self.data.get(self.key(ref), {})
        return [a[k][m] - b[k][m] for k in keys if k in a and k in b]

    def stat(self, cfg, ref, keys, m):
        v = self.diffs(cfg, ref, keys, m)
        if len(v) < 3: return 0.0, 0.0, len(v)
        mean = sum(v) / len(v); sd = math.sqrt(sum((x - mean) ** 2 for x in v) / (len(v) - 1))
        return mean, (mean / (sd / math.sqrt(len(v))) if sd else 0.0), len(v)

    # search space
    def options(self, inc):
        """Every option that differs from inc: ('TI', group, option) or ('M', mentality)."""
        out = []
        for g in self.A.GROUPS.values():
            if self.a.only and g['label'] not in self.a.only: continue
            out += [('TI', g['id'], o['id']) for o in g['options'] if o['id'] != inc['instructions'].get(str(g['id']))]
        if not self.a.only: out += [('M', m['id']) for m in self.A.CATALOG['mentalities'] if m['id'] != inc['mentality']]
        return out

    def apply(self, inc, changes):
        c = copy.deepcopy(inc)
        for ch in changes:
            if ch[0] == 'TI': c['instructions'][str(ch[1])] = ch[2]
            else: c['mentality'] = ch[1]
        return c

    def slot(self, ch): return ('M',) if ch[0] == 'M' else ('TI', ch[1])

    def sample(self, inc, n, rng):
        slots = {}
        for ch in self.options(inc): slots.setdefault(self.slot(ch), []).append(ch)
        out, seen, tries = [], set(), 0
        while len(out) < n and tries < n * 50:
            tries += 1
            chs = tuple(rng.choice(v) for v in slots.values() if rng.random() < self.a.change_rate)
            if not chs or chs in seen: continue
            seen.add(chs); c = self.apply(inc, chs)
            if self.valid(c): out.append((chs, c))
        return out

    def describe(self, ch):
        if ch[0] == 'M': return 'Mentality: ' + next(m['label'] for m in self.A.CATALOG['mentalities'] if m['id'] == ch[1])
        g = self.A.GROUPS[ch[1]]; return f"{g['label']}: " + next(o['label'] for o in g['options'] if o['id'] == ch[2])

    def summary(self, cfg):
        parts = [f"mentality {next(m['label'] for m in self.A.CATALOG['mentalities'] if m['id'] == cfg['mentality'])}"]
        for k, v in sorted(cfg['instructions'].items(), key=lambda x: int(x[0])):
            g = self.A.GROUPS.get(int(k))
            if g: parts.append(f"{g['label']} {next((o['label'] for o in g['options'] if o['id'] == v), v)}")
        return '; '.join(parts)

    def say(self, line=''):
        print(line, flush=True); self.lines.append(line)

    def keys(self, matches, first, n): return [(name, s) for name, _, _ in matches for s in range(first, first + n)]

    def per_match(self, total, matches): return max(1, math.ceil(total / len(matches)))

    # one round: screen, model, confirm
    def round(self, r, inc):
        import numpy as np
        a = self.a; rng = random.Random(f'{a.seed}-{r}')
        # the screen's cells: every search match on a few seeds; the current tactic plays them all, each variation a
        # random sample of them (so a large pool of matches costs no more per variation)
        n = self.per_match(a.cells, self.search); first = 100 * r + 1
        cells = self.keys(self.search, first, n)
        combos = self.sample(inc, a.combos, rng)
        given = [(chs, c, rng.sample(cells, min(a.pairs, len(cells)))) for chs, c in combos]
        self.say(f'## Round {r}'); self.say()
        self.say(f'Screen: {len(combos)} valid random variations, each on {min(a.pairs, len(cells))} paired matches drawn from '
                 f'{len(self.search)} search matches × {n} seed(s) (seeds {first}-{first + n - 1}); the current tactic plays all {len(cells)}.')
        self.play([(inc, cells)] + [(c, cc) for _, c, cc in given])
        opts = self.options(inc); col = {ch: i for i, ch in enumerate(opts)}
        rows = [(chs, self.diffs(c, inc, cc, 'xPts'), self.diffs(c, inc, cc, 'xGD')) for chs, c, cc in given]
        rows = [x for x in rows if x[1]]
        X = np.zeros((len(rows), len(opts)))
        for i, (chs, _, _) in enumerate(rows):
            for ch in chs: X[i, col[ch]] = 1
        y = np.array([sum(v) / len(v) for _, v, _ in rows]); yg = np.array([sum(v) / len(v) for _, _, v in rows])
        lam = cv_lambda(X, y); w, se, _ = ridge(X, y, lam); wg, _, _ = ridge(X, yg, cv_lambda(X, yg))
        order = sorted(range(len(opts)), key=lambda i: -w[i])
        self.say(); self.say(f'Main effects of each option (per game against the current tactic; ridge, λ = {lam}):'); self.say()
        self.say('| Change | xPts | ± | xGD |'); self.say('|---|---|---|---|')
        for i in order[:10] + [i for i in order[-5:] if i not in order[:10]]:
            self.say(f'| {self.describe(opts[i])} | {w[i]:+.3f} | {se[i]:.3f} | {wg[i]:+.3f} |')
        # pairwise interactions among the strongest options, with the penalty chosen by cross-validation
        top = sorted(range(len(opts)), key=lambda i: -abs(w[i]))[:a.interact]
        pairs = [(i, j) for k, i in enumerate(top) for j in top[k + 1:] if self.slot(opts[i]) != self.slot(opts[j])]
        Xi = np.hstack([X, np.array([[row[i] * row[j] for i, j in pairs] for row in X]).reshape(len(X), len(pairs))])
        lam2 = cv_lambda(Xi, y); wi, sei, _ = ridge(Xi, y, lam2)
        inter = sorted(((wi[len(opts) + k], sei[len(opts) + k], p) for k, p in enumerate(pairs)), key=lambda x: -abs(x[0]))
        strong = [x for x in inter if abs(x[0]) > 2 * x[1]]
        self.say(); self.say(f'Pairwise interactions among the {len(top)} strongest options: {len(pairs)} modelled, '
                             f'{len(strong)} larger than 2 standard errors' + (':' if strong else '.'))
        for v, s, (i, j) in strong[:6]: self.say(f'- {self.describe(opts[i])} × {self.describe(opts[j])}: {v:+.3f} ± {s:.3f}')

        def predict(chs):
            x = np.zeros(Xi.shape[1])
            for ch in chs: x[col[ch]] = 1
            for k, (i, j) in enumerate(pairs): x[len(opts) + k] = x[i] * x[j]
            return float(x @ wi)
        slots = {}
        for ch in opts: slots.setdefault(self.slot(ch), []).append(ch)
        found = {}
        for start in range(30):   # hill-climb on the model from the current tactic and from random starts
            cur = {} if start == 0 else {self.slot(ch): ch for ch in rng.sample(opts, 3)}
            if cur and not self.valid(self.apply(inc, cur.values())): continue
            v0, improved = predict(cur.values()), True
            while improved:
                improved = False
                for sl, chs in slots.items():
                    for ch in chs + [None]:
                        trial = dict(cur)
                        if ch is None: trial.pop(sl, None)
                        else: trial[sl] = ch
                        v = predict(trial.values())
                        if len(trial) > a.max_changes: continue   # the model is only reliable close to what was tested
                        if v > v0 + 1e-9 and self.valid(self.apply(inc, trial.values())): cur, v0, improved = trial, v, True
            chs = tuple(sorted(cur.values()))
            if chs: found[chs] = v0
            sparse = tuple(ch for ch in chs if w[col[ch]] > se[col[ch]])   # only the changes the model is fairly sure of
            if sparse and self.valid(self.apply(inc, sparse)): found.setdefault(sparse, predict(sparse))
        # small candidates too: the 2, 4 and 6 best options by main effect (one per instruction), close to what was tested
        ranked, used = [], set()
        for i in order:
            if w[i] <= 0: break
            if self.slot(opts[i]) not in used: used.add(self.slot(opts[i])); ranked.append(opts[i])
        small = [tuple(sorted(ranked[:k])) for k in sorted({2, a.max_changes // 2 * 2 or 2, a.max_changes}) if len(ranked) >= k]
        small = [(chs, predict(chs)) for chs in small if self.valid(self.apply(inc, chs))]
        cands = sorted(found.items(), key=lambda x: -x[1])[:max(1, a.confirm_top - len(small))]
        cands += [x for x in small if x[0] not in dict(cands)]
        if not cands: self.say(); self.say('The model predicts no gain.'); self.say(); return None
        nc = self.per_match(a.confirm, self.search); fc = 1000 * r + 1; ck = self.keys(self.search, fc, nc)
        self.say(); self.say(f'Confirmation: the {len(cands)} best predicted combinations against the current tactic on fresh seeds '
                             f'({fc}-{fc + nc - 1}, {len(ck)} paired matches each):'); self.say()
        self.play([(inc, ck)] + [(self.apply(inc, chs), ck) for chs, _ in cands]); res = []
        self.say('| Changes | Predicted xPts | xPts (t) | xGD (t) | Points (t) |'); self.say('|---|---|---|---|---|')
        for chs, p in cands:
            c = self.apply(inc, chs); s = {m: self.stat(c, inc, ck, m) for m in ('xPts', 'xGD', 'pts')}; res.append((s, chs, c))
            self.say(f"| {'; '.join(self.describe(x) for x in chs)} | {p:+.3f} | {s['xPts'][0]:+.3f} ({s['xPts'][1]:+.1f}) | "
                     f"{s['xGD'][0]:+.3f} ({s['xGD'][1]:+.1f}) | {s['pts'][0]:+.3f} ({s['pts'][1]:+.1f}) |")
        s, chs, c = max(res, key=lambda x: x[0]['xPts'][0])
        self.say()
        if s['xPts'][1] < a.keep_t: self.say(f'Nothing held up on fresh seeds (needs t >= {a.keep_t}).'); self.say(); return None
        self.say(f"Kept: {'; '.join(self.describe(x) for x in chs)}."); self.say()
        return c, chs

    def run(self):
        a = self.a
        self.say(f'# Tactic search: {a.team}'); self.say()
        if getattr(self, 'pool_note', None): self.say(f'Search matches: {self.pool_note}.'); self.say()
        else: self.say(f'Search matches: {", ".join(n for n, _, _ in self.search)}.'); self.say()
        self.say(f'Held out for the final check: {", ".join(n for n, _, _ in self.held)}.'); self.say()
        self.say(f'Your players\' tactical areas held at {a.familiarity} for every candidate; complexity as stored. '
                 f'Your tactic at the start: {self.summary(self.start)}.'); self.say()
        inc = self.start
        for r in range(1, a.rounds + 1):
            res = self.round(r, inc)
            if not res: break
            inc = res[0]
        self.final(inc)

    def final(self, best):
        self.say('## Result'); self.say()
        if best == self.start: self.say('No combination beat your tactic.'); self.write(best); return
        n = self.per_match(self.a.final, self.held); keys = self.keys(self.held, 1, n)
        self.play([(self.start, keys), (best, keys)])
        changed = [self.describe(('TI', int(k), v)) for k, v in best['instructions'].items() if self.start['instructions'].get(k) != v]
        if best['mentality'] != self.start['mentality']: changed.append(self.describe(('M', best['mentality'])))
        self.say('Changes from your tactic: ' + '; '.join(changed) + '.'); self.say()
        self.say(f'Checked on the held-out matches ({", ".join(m[0] for m in self.held)}; seeds 1-{n}), per game:'); self.say()
        self.say('| | ' + ' | '.join(MEASURES) + ' |'); self.say('|---' * (len(MEASURES) + 1) + '|')
        a, b = self.data[self.key(best)], self.data[self.key(self.start)]
        ks = [k for k in keys if k in a and k in b]; avg = lambda d, m: sum(d[k][m] for k in ks) / len(ks)
        self.say('| Your tactic | ' + ' | '.join(f'{avg(b, m):.2f}' for m in MEASURES) + ' |')
        self.say('| Best found | ' + ' | '.join(f'{avg(a, m):.2f}' for m in MEASURES) + ' |')
        self.say('| Difference (t) | ' + ' | '.join('{:+.2f} ({:+.1f})'.format(*self.stat(best, self.start, ks, m)[:2]) for m in MEASURES) + ' |')
        self.say(); self.say(f'{len(ks)} paired matches against opponents the search never played. Both at the same familiarity; '
                             'in the game, changed instructions also have to be learned (switching cost not included yet).')
        self.write(best)

    def write(self, best):
        import base64
        name = self.held[0][0]; s, path, side = self.bases[name]; s = copy.deepcopy(s); t = s['teams'][side]
        t['instructions'] = dict(best['instructions']); t['mentality'] = best['mentality']
        s = self.A.validate_scenario(s)
        (self.out / 'best.json').write_text(json.dumps(s, ensure_ascii=False), encoding='utf8')
        try:
            r = self.A.export_fmf({'side': side, 'scenario': s, 'name': f'{t.get("tactic_name") or "Tactic"} (searched)'})
            (self.out / 'best.fmf').write_bytes(base64.b64decode(r['file_base64'])); self.say(); self.say('Tactic file: best.fmf; full scenario: best.json.')
        except Exception as e:
            self.say(); self.say(f'Full scenario: best.json (tactic file export failed: {str(e)[:100]}).')
        self.say(); self.say(f'Final tactic: {self.summary(best)}')
        (self.out / 'report.md').write_text('\n'.join(self.lines) + '\n', encoding='utf8')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('out'); p.add_argument('--team', required=True)
    p.add_argument('--match', nargs='+', help='saved match files instead of all of the team\'s saved matches')
    p.add_argument('--holdout', nargs='+', help='opponents (or match names) kept for the final check (default: the opponents of every third match by date; every match against them is held out)')
    p.add_argument('--start-tactic', help='start from this tactic (FILE.fmf or preset:STYLE) instead of your saved one')
    p.add_argument('--familiarity', type=int, default=70)
    p.add_argument('--combos', type=int, default=400, help='random variations screened per round')
    p.add_argument('--pairs', type=int, default=20, help='paired matches per screened variation')
    p.add_argument('--cells', type=int, default=300, help='paired matches the current tactic plays in each screen (the variations sample them)')
    p.add_argument('--save', help='FM27 save: search on built matches with your current squad (needs fmsave); your saved matches are then all held out')
    p.add_argument('--club', help='your club\'s name in the save (default: found from --team)')
    p.add_argument('--pool', type=int, default=150, help='most built matches in the search')
    p.add_argument('--min-opponent-ca', type=float, help='weakest opponent XI (average current ability) to include; default: lower quarter of your saved matches\' opponents')
    p.add_argument('--change-rate', type=float, default=0.35)
    p.add_argument('--interact', type=int, default=14, help='options whose pairwise interactions are modelled')
    p.add_argument('--confirm-top', type=int, default=4); p.add_argument('--confirm', type=int, default=300)
    p.add_argument('--final', type=int, default=450, help='paired matches for the held-out check')
    p.add_argument('--rounds', type=int, default=2); p.add_argument('--seed', type=int, default=1)
    p.add_argument('--max-changes', type=int, default=4, help='most instruction changes in one candidate (a first run: 12+ change\n'
                   'combinations the model liked failed on fresh seeds)')
    p.add_argument('--keep-t', type=float, default=2.5, help='t needed on fresh seeds to keep the best of the confirmed candidates')
    p.add_argument('--only', nargs='+', help='search only these team instructions (English names); mentality is then left alone')
    p.add_argument('--workers', type=int, default=6)
    a = p.parse_args()
    try: import numpy   # noqa: F401  (the model)
    except ImportError: raise SystemExit('The tactic search needs numpy: .venv/bin/pip install numpy')
    Search(a).run()


if __name__ == '__main__':
    main()
