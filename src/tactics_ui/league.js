'use strict';
// League page: many tactics against each other, home and away, over several seasons (server: src/league_web.py,
// shared league code: src/league.py, the same as `scripts/study.py league`).
const LG = {opts: null, list: null, id: null, result: null, timer: null, clubs: {}, busy: false,
 setup: (() => { try { return JSON.parse(localStorage.getItem('fm27-league-setup-v1')) || null; } catch (e) { return null; } })() || {
  name: '', base: '', seasons: 2, familiarity: 70, perTeamFamiliarity: false, equalStart: true,
  squad: {kind: 'reference', tier: 'pl-middle'}, perTeamSquad: false, teams: []}};
const lgSave = () => { try { localStorage.setItem('fm27-league-setup-v1', JSON.stringify({...LG.setup, teams: LG.setup.teams.map(t => t.tactic.kind === 'upload' ? {...t, tactic: {kind: 'upload', filename: t.tactic.filename, file_base64: t.tactic.file_base64}} : t)})); } catch (e) {} };

$('.rail nav').insertAdjacentHTML('beforeend', '<button data-view="league">▦ <span>League</span></button>');
$('.rail nav [data-view="league"]').onclick = () => { view = 'league'; render(); window.scrollTo(0, 0); lgLoad(); };

async function lgLoad(){
 try {
  if (!LG.opts) LG.opts = await api('/api/league/options');
  if (!LG.setup.base && LG.opts.own_matches.length) LG.setup.base = LG.opts.own_matches.slice().sort((a, b) => b.modified - a.modified)[0].path;
  LG.list = (await api('/api/league/list')).leagues;
  if (!LG.id && LG.list.length) LG.id = LG.list[0].id;
  if (LG.id) await lgPoll(false);
 } catch (e) { LG.error = e.message; }
 if (view === 'league') render();
}
async function lgPoll(again = true){
 clearTimeout(LG.timer);
 if (!LG.id) return;
 try { LG.result = await api('/api/league/status/' + encodeURIComponent(LG.id)); } catch (e) { LG.result = {error: e.message}; }
 const live = LG.result && !['complete', 'stopped', 'error', 'not built'].includes(LG.result.state);
 if (view === 'league' && again) render();
 if (live) LG.timer = setTimeout(() => lgPoll(true), 2500);
 else if (again) api('/api/league/list').then(d => { LG.list = d.leagues; if (view === 'league') render(); });
}

const lgTierLabel = id => LG.opts?.reference.tiers.find(t => t.id === id)?.label || id;
function lgSquadPicker(sq, key){
 const o = LG.opts, kind = sq.kind || 'reference';
 const tiers = o.reference.tiers.map(t => `<option value="reference:${t.id}" ${kind === 'reference' && sq.tier === t.id ? 'selected' : ''}>Synthetic: ${esc(t.label)}</option>`).join('');
 const sel = `<select data-lg-squad-kind="${key}">${tiers}<option value="match" ${kind === 'match' ? 'selected' : ''}>Real: from a saved or imported match</option><option value="save" ${kind === 'save' ? 'selected' : ''} ${o.fmsave ? '' : 'disabled'}>Real: from your FM27 save${o.fmsave ? '' : ' (needs fmsave)'}</option><option value="levelled" ${kind === 'levelled' ? 'selected' : ''}>Levelled: every attribute one value</option></select>`;
 let extra = '';
 if (kind === 'match') {
  const opt = m => `<option value="${esc(m.path)}" ${sq.match === m.path ? 'selected' : ''}>${esc(m.label)}</option>`;
  extra = `<select data-lg-squad-match="${key}"><option value="">Choose a match…</option><optgroup label="Your matches">${o.own_matches.map(opt).join('')}</optgroup>${o.other_matches.length ? `<optgroup label="Other clubs' matches">${o.other_matches.map(opt).join('')}</optgroup>` : ''}</select> <select data-lg-squad-side="${key}"><option value="0" ${!sq.side ? 'selected' : ''}>home side</option><option value="1" ${sq.side ? 'selected' : ''}>away side</option></select>`;
 } else if (kind === 'save') {
  const clubs = LG.clubs[sq.save];
  extra = `<select data-lg-squad-save="${key}"><option value="">Choose a save…</option>${o.saves.map(s => `<option ${sq.save === s ? 'selected' : ''}>${esc(s)}</option>`).join('')}</select> ` +
   (sq.save ? (clubs ? `<select data-lg-squad-club="${key}"><option value="">Choose a club…</option>${clubs.map(c => `<option ${sq.club === c ? 'selected' : ''}>${esc(c)}</option>`).join('')}</select>` : '<span class="tiny muted">reading the save…</span>') : '');
 } else if (kind === 'levelled') {
  extra = `<label class="tiny">value <input type="number" min="1" max="20" value="${sq.value || 12}" data-lg-squad-value="${key}" style="width:4em"></label><div class="tiny muted">${esc(o.levelled_note)}</div>`;
 }
 return sel + ' ' + extra;
}
function lgTacticPicker(t, k){
 const presets = LG.opts.presets.map(p => `<option value="preset:${esc(p)}" ${t.tactic.kind === 'preset' && t.tactic.style === p ? 'selected' : ''}>Preset: ${esc(p)}</option>`).join('');
 const up = t.tactic.kind === 'upload' ? `<option value="upload" selected>File: ${esc(t.tactic.filename)}</option>` : '';
 return `<select data-lg-tactic="${k}">${up}${presets}<option value="choose">Upload an .fmf file…</option></select>`;
}
function lgSetupView(){
 const s = LG.setup, o = LG.opts;
 const rows = s.teams.map((t, k) => `<tr><td>${k + 1}</td><td><input data-lg-name="${k}" value="${esc(t.name)}" style="width:14em"></td><td>${lgTacticPicker(t, k)}</td>${s.perTeamSquad ? `<td>${lgSquadPicker(t.squad || s.squad, 't' + k)}</td>` : ''}${s.perTeamFamiliarity ? `<td><input type="number" min="0" max="100" data-lg-fam="${k}" value="${t.familiarity ?? s.familiarity}" style="width:4em"></td>` : ''}<td><button class="button small ghost" data-lg-remove="${k}">✕</button></td></tr>`).join('');
 const matches = s.teams.length * (s.teams.length - 1) * s.seasons;
 return `<div class="card"><div class="card-head"><div><h2>Set up a league</h2><div class="subtitle">Test many tactics against each other: add a team per tactic, keep the same squad for every team so only the tactics differ, and run several seasons. Differences smaller than the spread across seasons are probably noise.</div></div></div><div class="card-body">
 <p><label>Name <input id="lg-name" value="${esc(s.name)}" placeholder="optional" style="width:18em"></label></p>
 <p><b>Teams</b> (${s.teams.length}; 2 to 20) <button class="button small" id="lg-add">Add a team</button> <button class="button small" id="lg-presets">All presets</button> <button class="button small" id="lg-folder">Load a folder of .fmf files</button> <button class="button small ghost" id="lg-clear">Remove all</button>
 <input type="file" id="lg-folder-input" webkitdirectory multiple hidden><input type="file" id="lg-file-input" accept=".fmf" hidden></p>
 <table><thead><tr><th>#</th><th>Name</th><th>Tactic</th>${s.perTeamSquad ? '<th>Squad</th>' : ''}${s.perTeamFamiliarity ? '<th>Familiarity</th>' : ''}<th></th></tr></thead><tbody>${rows || '<tr><td colspan="6" class="muted">No teams yet: add some, or load all presets or a folder of tactics.</td></tr>'}</tbody></table>
 <p><b>Squad</b> <label class="tiny"><input type="checkbox" id="lg-per-squad" ${s.perTeamSquad ? 'checked' : ''}> choose per team</label><br>${s.perTeamSquad ? '<span class="tiny muted">Set in the table above.</span>' : lgSquadPicker(s.squad, 'all')}<br><span class="tiny muted">Synthetic reference squads: invented players calibrated on FM27's database (${esc(o.reference.calibration.game_build)}, ${esc(o.reference.calibration.source)}). Real squads are built on this Mac and never leave it.</span></p>
 <p><b>Familiarity</b> <input type="number" min="0" max="100" id="lg-fam" value="${s.familiarity}" style="width:4em"> in all eight tactical areas <label class="tiny"><input type="checkbox" id="lg-per-fam" ${s.perTeamFamiliarity ? 'checked' : ''}> choose per team</label></p>
 <p><b>Format</b> home and away · <label>seasons <input type="number" min="1" max="50" id="lg-seasons" value="${s.seasons}" style="width:4em"></label> (each season on a new seed) · <label><input type="checkbox" id="lg-equal" ${s.equalStart ? 'checked' : ''}> both sides start alike (fitness, sharpness, morale, cohesion)</label></p>
 <p><b>Template match</b> <select id="lg-base">${o.own_matches.map(m => `<option value="${esc(m.path)}" ${s.base === m.path ? 'selected' : ''}>${esc(m.label)}</option>`).join('')}</select><br><span class="tiny muted">Every fixture is played in this saved match (stadium, conditions); the squads and tactics are the teams'. Every side picks its XI by position for its tactic and is managed by the assistant during the match.</span></p>
 <p><button class="button primary" id="lg-start" ${LG.busy || s.teams.length < 2 || s.teams.length > 20 ? 'disabled' : ''}>Run the league ↗</button> <span class="tiny muted">${matches} matches, about ${Math.max(1, Math.round(matches / (1000 * Number($('#workers')?.value || o.workers)) * 60))} min with ${$('#workers')?.value || o.workers} workers · engine ${esc(o.engine || '')}</span></p>
 </div></div>`;
}
const lgNum = (v, d = 1) => v == null ? '' : Number(v).toFixed(d);
function lgResultView(){
 const r = LG.result;
 if (!r) return '';
 if (r.error && !r.table) return `<div class="results-error">${esc(r.error)}</div>`;
 const m = r.meta || {}, live = !['complete', 'stopped', 'error', 'not built'].includes(r.state);
 const head = `<div class="card-head"><div><h2>${esc(r.name)}</h2><div class="tiny muted">${r.completed} / ${r.total} matches · ${r.seasons_complete ?? 0} of ${m.seasons ?? '?'} seasons complete · ${esc(r.state)}</div></div><div>${live ? `<button class="button small" id="lg-stop">Stop</button>` : r.completed < r.total ? `<button class="button small" id="lg-resume">Resume</button>` : ''} <a class="button small" href="/api/league/csv/${encodeURIComponent(r.id)}" download="league-${esc(r.id)}.csv">CSV ↓</a></div></div>`;
 const rows = (r.table || []).filter(x => x.seasons).map(x => `<tr><td>${x.rank}</td><td><b>${esc(x.team)}</b><div class="tiny muted">${esc(x.tactic)}</div></td><td>${lgNum(x.W)}</td><td>${lgNum(x.D)}</td><td>${lgNum(x.L)}</td><td>${lgNum(x.GF)}</td><td>${lgNum(x.GA)}</td><td>${lgNum(x.xGF, 2)}</td><td>${lgNum(x.xGA, 2)}</td><td>${lgNum(x.xPts)}</td><td><b>${lgNum(x.Pts)}</b></td><td>${x.Pts_sd == null ? '' : '±' + lgNum(x.Pts_sd)}</td><td>${lgNum(x.PPG, 2)}</td></tr>`).join('');
 const order = r.order || [], h = r.head_to_head || {};
 const cell = v => v == null ? '<td></td>' : `<td style="background:hsl(${Math.round(v / 3 * 120)},45%,${document.documentElement.dataset.theme === 'dark' ? 25 : 85}%)">${v.toFixed(1)}</td>`;
 const grid = `<table class="tiny"><thead><tr><th></th>${order.map((_, k) => `<th>${k + 1}</th>`).join('')}</tr></thead><tbody>${order.map((a, k) => `<tr><td>${k + 1} ${esc(a)}</td>${order.map(b => a === b ? '<td>·</td>' : cell(h[a]?.[b])).join('')}</tr>`).join('')}</tbody></table>`;
 const teams = (m.teams || []).map(t => `<li>${esc(t.name)}: ${esc(t.tactic)} · ${esc(t.squad)} · familiarity ${t.familiarity}</li>`).join('');
 return `<div class="card">${head}${r.error ? `<div class="results-error">${esc(r.error)}</div>` : ''}<div class="card-body">
 ${rows ? `<div class="table-scroll"><table><thead><tr><th>#</th><th>Team</th><th>W</th><th>D</th><th>L</th><th>Goals for</th><th>Goals against</th><th>xG for</th><th>xG against</th><th>xPts</th><th>Points</th><th>Spread</th><th>Per game</th></tr></thead><tbody>${rows}</tbody></table></div>
 <p class="tiny muted">Per season, averaged over the seasons played; xG per game. Spread: standard deviation of a team's points across seasons. Differences smaller than the spread are probably noise.</p>
 <h3>Head to head</h3><p class="tiny muted">Points per match of the row team against the column team, both venues and all seasons.</p><div class="table-scroll">${grid}</div>` : `<div class="notice">${live ? 'Building the fixtures and playing the first matches…' : 'No matches played yet.'}</div>`}
 <h3>Settings</h3><ul class="tiny">${teams}</ul><p class="tiny muted">Template match: ${esc(m.base_match || '')} (${esc(m.base_match_game_version || '')}) · engine ${esc(m.engine || '')} · ${m.seasons} season(s), home and away · ${m.equal_start ? 'both sides start alike' : 'each side keeps the template\'s start state'}${m.reference_squads ? ` · synthetic squads calibrated on FM27's database ${esc(m.reference_squads.game_build)}` : ''}${(m.skipped || []).length ? ` · skipped: ${esc(m.skipped.join('; '))}` : ''}</p>
 </div></div>`;
}
function lgListView(){
 if (!LG.list || !LG.list.length) return '';
 return `<div class="card"><div class="card-head"><h3>Leagues on this Mac</h3></div><div class="card-body history">${LG.list.map(l => `<button class="button small ${l.id === LG.id ? 'active' : ''}" data-lg-open="${esc(l.id)}">${esc(l.name)} · ${l.teams} teams · ${l.completed}/${l.total} · ${esc(l.state)}</button>`).join(' ')}</div></div>`;
}
function leagueView(){
 if (LG.error) return `<div class="results-error">${esc(LG.error)}</div>`;
 if (!LG.opts) return '<div class="loading">Reading presets, reference squads and your matches…</div>';
 return lgResultView() + lgListView() + lgSetupView();
}

function lgB64(file){ return new Promise((ok, bad) => { const r = new FileReader(); r.onload = () => ok(String(r.result).split(',')[1]); r.onerror = bad; r.readAsDataURL(file); }); }
function lgSetSquad(key, sq){ if (key === 'all') LG.setup.squad = sq; else LG.setup.teams[Number(key.slice(1))].squad = sq; }
function lgGetSquad(key){ return key === 'all' ? LG.setup.squad : (LG.setup.teams[Number(key.slice(1))].squad || {...LG.setup.squad}); }
function lgBind(){
 const s = LG.setup, rerender = () => { lgSave(); render(); };
 const on = (sel, ev, fn) => { const el = $(sel); if (el) el[ev] = fn; };
 on('#lg-name', 'onchange', e => { s.name = e.target.value; lgSave(); });
 on('#lg-add', 'onclick', () => { if (s.teams.length >= 20) return toast('At most 20 teams'); s.teams.push({name: `Team ${s.teams.length + 1}`, tactic: {kind: 'preset', style: LG.opts.presets[s.teams.length % LG.opts.presets.length]}}); rerender(); });
 on('#lg-presets', 'onclick', () => { const have = new Set(s.teams.filter(t => t.tactic.kind === 'preset').map(t => t.tactic.style)); LG.opts.presets.filter(p => !have.has(p)).forEach(p => s.teams.length < 20 && s.teams.push({name: p, tactic: {kind: 'preset', style: p}})); rerender(); });
 on('#lg-clear', 'onclick', () => { s.teams = []; rerender(); });
 on('#lg-folder', 'onclick', () => $('#lg-folder-input').click());
 on('#lg-folder-input', 'onchange', async e => { const files = [...e.target.files].filter(f => f.name.toLowerCase().endsWith('.fmf')).sort((a, b) => a.name.localeCompare(b.name));
  for (const f of files) { if (s.teams.length >= 20) { toast('At most 20 teams'); break; } s.teams.push({name: f.name.replace(/\.fmf$/i, ''), tactic: {kind: 'upload', filename: f.name, file_base64: await lgB64(f)}}); }
  if (!files.length) toast('No .fmf files in that folder'); rerender(); });
 $$('[data-lg-name]').forEach(el => el.onchange = () => { s.teams[el.dataset.lgName].name = el.value; lgSave(); });
 $$('[data-lg-remove]').forEach(el => el.onclick = () => { s.teams.splice(Number(el.dataset.lgRemove), 1); rerender(); });
 $$('[data-lg-fam]').forEach(el => el.onchange = () => { s.teams[el.dataset.lgFam].familiarity = Number(el.value); lgSave(); });
 $$('[data-lg-tactic]').forEach(el => el.onchange = () => { const k = Number(el.dataset.lgTactic), v = el.value;
  if (v.startsWith('preset:')) { s.teams[k].tactic = {kind: 'preset', style: v.slice(7)}; return rerender(); }
  if (v === 'choose') { const input = $('#lg-file-input'); input.value = ''; input.onchange = async () => { const f = input.files[0]; if (f) { s.teams[k].tactic = {kind: 'upload', filename: f.name, file_base64: await lgB64(f)}; if (/^Team \d+$/.test(s.teams[k].name)) s.teams[k].name = f.name.replace(/\.fmf$/i, ''); } rerender(); }; input.click(); } });
 $$('[data-lg-squad-kind]').forEach(el => el.onchange = () => { const v = el.value, key = el.dataset.lgSquadKind;
  lgSetSquad(key, v.startsWith('reference:') ? {kind: 'reference', tier: v.slice(10)} : v === 'levelled' ? {kind: 'levelled', value: 12} : {kind: v}); rerender(); });
 $$('[data-lg-squad-match]').forEach(el => el.onchange = () => { lgSetSquad(el.dataset.lgSquadMatch, {...lgGetSquad(el.dataset.lgSquadMatch), match: el.value}); lgSave(); });
 $$('[data-lg-squad-side]').forEach(el => el.onchange = () => { lgSetSquad(el.dataset.lgSquadSide, {...lgGetSquad(el.dataset.lgSquadSide), side: Number(el.value)}); lgSave(); });
 $$('[data-lg-squad-value]').forEach(el => el.onchange = () => { lgSetSquad(el.dataset.lgSquadValue, {...lgGetSquad(el.dataset.lgSquadValue), value: Number(el.value)}); lgSave(); });
 $$('[data-lg-squad-club]').forEach(el => el.onchange = () => { lgSetSquad(el.dataset.lgSquadClub, {...lgGetSquad(el.dataset.lgSquadClub), club: el.value}); lgSave(); });
 $$('[data-lg-squad-save]').forEach(el => el.onchange = async () => { const key = el.dataset.lgSquadSave, save = el.value; lgSetSquad(key, {kind: 'save', save}); rerender();
  if (save && !LG.clubs[save]) { try { LG.clubs[save] = (await api('/api/league/clubs', {save})).clubs; } catch (e) { toast(e.message); } render(); } });
 on('#lg-per-squad', 'onchange', e => { s.perTeamSquad = e.target.checked; rerender(); });
 on('#lg-per-fam', 'onchange', e => { s.perTeamFamiliarity = e.target.checked; rerender(); });
 on('#lg-fam', 'onchange', e => { s.familiarity = Number(e.target.value); lgSave(); });
 on('#lg-seasons', 'onchange', e => { s.seasons = Math.max(1, Math.min(50, Number(e.target.value) || 1)); rerender(); });
 on('#lg-equal', 'onchange', e => { s.equalStart = e.target.checked; lgSave(); });
 on('#lg-base', 'onchange', e => { s.base = e.target.value; lgSave(); });
 on('#lg-start', 'onclick', async () => {
  const teams = s.teams.map(t => ({name: t.name, tactic: t.tactic, squad: s.perTeamSquad ? (t.squad || s.squad) : s.squad, familiarity: s.perTeamFamiliarity ? (t.familiarity ?? s.familiarity) : s.familiarity}));
  try { LG.busy = true; render(); const r = await api('/api/league/start', {name: s.name, teams, base_match: s.base, seasons: s.seasons, familiarity: s.familiarity, equal_start: s.equalStart, workers: Number($('#workers')?.value || LG.opts.workers)});
   LG.id = r.id; LG.list = (await api('/api/league/list')).leagues; toast('League started'); lgPoll(true); }
  catch (e) { toast(e.message); } finally { LG.busy = false; render(); } });
 on('#lg-stop', 'onclick', async () => { await api('/api/league/stop', {id: LG.id}); toast('Stopping after the matches in progress'); lgPoll(true); });
 on('#lg-resume', 'onclick', async () => { try { await api('/api/league/resume', {id: LG.id, workers: Number($('#workers')?.value || LG.opts.workers)}); lgPoll(true); } catch (e) { toast(e.message); } });
 $$('[data-lg-open]').forEach(el => el.onclick = () => { LG.id = el.dataset.lgOpen; LG.result = null; lgPoll(true); });
}

const lgRenderPrevious = render;
render = function(){
 if (view !== 'league') return lgRenderPrevious();
 if (!LG.opts && !LG.error) lgLoad();
 $('#page-title').textContent = 'Let the tactics play a league';
 $$('[data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === view));
 $('#workspace').innerHTML = leagueView();
 lgBind();
};
