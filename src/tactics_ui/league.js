'use strict';
// League page: many tactics against each other, home and away, over several seasons (server: src/league_web.py,
// shared league code: src/league.py, the same as `scripts/study.py league`).
const LG = {opts: null, list: null, id: null, result: null, timer: null, clubs: {}, busy: false,
 setup: (() => { try { return JSON.parse(localStorage.getItem('fm27-league-setup-v1')) || null; } catch (e) { return null; } })() || {
  name: '', base: '', seasons: 2, familiarity: 70, perTeamFamiliarity: false, equalStart: true,
  squad: {kind: 'reference', tier: 'pl-middle'}, perTeamSquad: false, teams: []}};
// uploaded tactic files are stored on this Mac's server once (lgUpload) and referred to by a short token
const lgSave = () => { try { localStorage.setItem('fm27-league-setup-v1', JSON.stringify({...LG.setup, teams: LG.setup.teams.map(t => t.tactic.kind === 'upload' ? {...t, tactic: {kind: 'upload', filename: t.tactic.filename, token: t.tactic.token}} : t)})); } catch (e) {} };
async function lgUpload(file){ const r = await api('/api/league/upload', {filename: file.name, file_base64: await lgB64(file)}); return {kind: 'upload', filename: file.name, token: r.token}; }

$('.rail nav').insertAdjacentHTML('beforeend', '<button data-view="league">▦ <span>League</span></button>');
$('.rail nav [data-view="league"]').onclick = () => { view = 'league'; render(); window.scrollTo(0, 0); lgLoad(); };

async function lgLoad(){
 try {
  if (!LG.opts) LG.opts = await api('/api/league/options');
  const known = new Set([...LG.opts.own_matches, ...LG.opts.other_matches].map(m => m.path));
  if (!LG.setup.baseChosen || !known.has(LG.setup.base)) LG.setup.base = LG.opts.default_template || '';   // the default until one is picked
  if (LG.setup.base2 && !known.has(LG.setup.base2)) LG.setup.base2 = '';
  LG.list = (await api('/api/league/list')).leagues;
  const running = LG.list.find(l => ['running', 'building', 'stopping'].includes(l.state));
  if (running && !LG.current) LG.id = LG.current = running.id;   // the hub follows a league that is running
  else if (!LG.id && LG.list.length) LG.id = LG.list[0].id;
  if (LG.id) await lgPoll(false);
 } catch (e) { LG.error = e.message; }
 if (view === 'league') render();
}
async function lgPoll(again = true){
 clearTimeout(LG.timer);
 if (!LG.id) return;
 try { LG.result = await api('/api/league/status/' + encodeURIComponent(LG.id)); } catch (e) { LG.result = {error: e.message}; }
 try { LG.list = (await api('/api/league/list')).leagues; } catch (e) {}
 // keep refreshing while the open league or any other league is running (the running box shows them all)
 const live = (LG.result && !['complete', 'stopped', 'error', 'not built'].includes(LG.result.state)) || (LG.list || []).some(l => ['running', 'building', 'stopping'].includes(l.state));
 if (view === 'league' && again && !(LG.tab === 'setup' && document.activeElement?.closest?.('#workspace'))) render();
 if (live) LG.timer = setTimeout(() => lgPoll(true), 2500);
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
function lgTemplatePicker(id, value, optional){
 const o = LG.opts, opt = m => `<option value="${esc(m.path)}" ${value === m.path ? 'selected' : ''}>${esc(m.label.replace(' (Other clubs)', ''))}</option>`;
 return `<select id="${id}">${optional ? `<option value="" ${value ? '' : 'selected'}>none</option>` : ''}${o.other_matches.length ? `<optgroup label="Other clubs' matches (neutral)">${o.other_matches.map(opt).join('')}</optgroup>` : ''}<optgroup label="Your matches">${o.own_matches.map(opt).join('')}</optgroup></select>`;
}
// the league's four components, each set up on its own page; the hub shows them as cards and runs the league
const LG_SECTIONS = [['teams', 'Teams & tactics'], ['squads', 'Squads'], ['format', 'Familiarity & format'], ['template', 'Template match']];
const lgTemplateLabel = p => { const m = [...(LG.opts?.other_matches || []), ...(LG.opts?.own_matches || [])].find(x => x.path === p); return m ? m.label.replace(' (Other clubs)', '') : 'not chosen'; };
const lgSquadText = sq => sq.kind === 'reference' ? 'Synthetic: ' + lgTierLabel(sq.tier) : sq.kind === 'match' ? (sq.match ? 'Real, from ' + lgTemplateLabel(sq.match) + (sq.side ? ' (away side)' : ' (home side)') : 'Real, from a match: not chosen') : sq.kind === 'save' ? (sq.club ? `${sq.club} from ${sq.save}` : 'From a save: not chosen') : sq.kind === 'levelled' ? `Levelled: every attribute ${sq.value || 12}` : 'not chosen';
function lgSummary(){
 const s = LG.setup, n = s.teams.length;
 return {
  teams: {text: n ? `${n} team${n === 1 ? '' : 's'}: ${s.teams.slice(0, 6).map(t => t.name).join(', ')}${n > 6 ? ', …' : ''}` : 'No teams yet', ok: n >= 2 && n <= 20, problem: n < 2 ? 'add at least 2 teams' : n > 20 ? 'at most 20 teams' : ''},
  squads: {text: s.perTeamSquad ? 'Chosen per team' : lgSquadText(s.squad), ok: true},
  format: {text: `Familiarity ${s.perTeamFamiliarity ? 'per team' : s.familiarity} · ${s.seasons} season${s.seasons === 1 ? '' : 's'}, home and away · ${s.equalStart ? 'both sides start alike' : "each side keeps the template's start state"}`, ok: true},
  template: {text: lgTemplateLabel(s.base) + (s.base2 && s.base2 !== s.base ? ' / ' + lgTemplateLabel(s.base2) : ''), ok: !!s.base, problem: s.base ? '' : 'choose a template'}};
}
function lgSectionNav(){
 const i = LG_SECTIONS.findIndex(([id]) => id === LG.tab), next = LG_SECTIONS[i + 1];
 return `<div class="toolbar"><div class="toolbar-left"><button class="button small" data-lg-tab="hub">← Set up & run</button><div class="segmented">${LG_SECTIONS.map(([id, label], k) => `<button data-lg-tab="${id}" class="${id === LG.tab ? 'active' : ''}">${k + 1}. ${label}</button>`).join('')}</div></div><div class="toolbar-right">${next ? `<button class="button small" data-lg-tab="${next[0]}">Next: ${next[1]} →</button>` : '<button class="button small primary" data-lg-tab="hub">Done – back to run</button>'}</div></div>`;
}
function lgSectionView(){
 const s = LG.setup, o = LG.opts, card = (title, sub, body) => `<div class="card"><div class="card-head"><div><h2>${title}</h2><div class="subtitle">${sub}</div></div></div><div class="card-body">${body}</div></div>`;
 if (LG.tab === 'teams') {
  const rows = s.teams.map((t, k) => `<tr><td>${k + 1}</td><td><input data-lg-name="${k}" value="${esc(t.name)}" style="width:14em"></td><td>${lgTacticPicker(t, k)}</td>${s.perTeamSquad ? `<td>${lgSquadPicker(t.squad || s.squad, 't' + k)}</td>` : ''}${s.perTeamFamiliarity ? `<td><input type="number" min="0" max="100" data-lg-fam="${k}" value="${t.familiarity ?? s.familiarity}" style="width:4em"></td>` : ''}<td><button class="button small ghost" data-lg-remove="${k}">✕</button></td></tr>`).join('');
  return card('1. Teams & tactics', 'One team per tactic: an FM27 preset or one of your .fmf tactic files. Between 2 and 20 teams.', `
   <p><label>League name <input id="lg-name" value="${esc(s.name)}" placeholder="optional" style="width:18em"></label></p>
   <p><button class="button small" id="lg-add">Add a team</button> <button class="button small" id="lg-presets">Add all presets</button> <button class="button small" id="lg-folder">Load a folder of .fmf files</button> <button class="button small ghost" id="lg-clear">Remove all</button>
   <input type="file" id="lg-folder-input" webkitdirectory multiple hidden><input type="file" id="lg-file-input" accept=".fmf" hidden></p>
   <table><thead><tr><th>#</th><th>Name</th><th>Tactic</th>${s.perTeamSquad ? '<th>Squad</th>' : ''}${s.perTeamFamiliarity ? '<th>Familiarity</th>' : ''}<th></th></tr></thead><tbody>${rows || '<tr><td colspan="6" class="muted">No teams yet: add some, or add all presets or a folder of tactics.</td></tr>'}</tbody></table>`);
 }
 if (LG.tab === 'squads') return card('2. Squads', 'Keep the same squad for every team so that only the tactics differ.', `
   <p><label class="tiny"><input type="checkbox" id="lg-per-squad" ${s.perTeamSquad ? 'checked' : ''}> choose a squad per team (in the Teams & tactics table)</label></p>
   ${s.perTeamSquad ? '' : `<p>${lgSquadPicker(s.squad, 'all')}</p>`}
   <ul class="tiny muted"><li><b>Synthetic</b> (recommended): invented players calibrated on FM27's database (${esc(o.reference.calibration.game_build)}, ${esc(o.reference.calibration.source)}), one squad per tier: three for the Premier League, and the middle of the Championship, League One, League Two and National League.</li>
   <li><b>Real</b>: the players of one side of one of your saved or imported matches, or a club from your FM27 save. Built on this Mac; never leaves it.</li>
   <li><b>Levelled</b>: every match attribute at one value. ${esc(o.levelled_note)}</li></ul>`);
 if (LG.tab === 'format') return card('3. Familiarity & format', 'Everything the same for every team, so that only the tactics differ.', `
   <p><b>Tactical familiarity</b> <input type="number" min="0" max="100" id="lg-fam" value="${s.familiarity}" style="width:4em"> in all eight tactical areas, for every team <label class="tiny"><input type="checkbox" id="lg-per-fam" ${s.perTeamFamiliarity ? 'checked' : ''}> choose per team</label></p>
   <p><b>Seasons</b> <input type="number" min="1" max="50" id="lg-seasons" value="${s.seasons}" style="width:4em"> · every team plays every other at home and away once per season, each season on new random seeds. More seasons give a surer table.</p>
   <p><label><input type="checkbox" id="lg-equal" ${s.equalStart ? 'checked' : ''}> Both sides start alike (fitness, sharpness, morale, cohesion)</label> <span class="tiny muted">(recommended)</span></p>`);
 return card('4. Template match', 'Every fixture is played in this match: its stadium and weather. The squads and tactics are the teams\'; no player of the template is used.', `
   <p>${lgTemplatePicker('lg-base', s.base, false)}</p><p class="tiny">Alternate with ${lgTemplatePicker('lg-base2', s.base2, true)} (seasons alternate between the two)</p>
   <p class="tiny muted">A match between two other clubs keeps your own club out of the test. Every side picks its XI by position for its tactic and is managed by the assistant during the match.</p>`);
}
function lgHubView(){
 const s = LG.setup, o = LG.opts, sum = lgSummary(), ready = Object.values(sum).every(x => x.ok);
 const matches = s.teams.length * (s.teams.length - 1) * s.seasons, workers = Number($('#workers')?.value || o.workers);
 const cards = LG_SECTIONS.map(([id, label], k) => { const x = sum[id];
  return `<div class="card" style="padding:16px"><div class="tiny muted">${k + 1}</div><h3>${label}</h3><p class="tiny" style="min-height:3em">${esc(x.text)}${x.problem ? `<br><span style="color:#c0573f">${esc(x.problem)}</span>` : ''}</p><button class="button small" data-lg-tab="${id}">${x.ok ? 'Change' : 'Set up'} →</button></div>`; }).join('');
 return `<div class="card" style="margin-bottom:18px"><div class="card-head"><div><h2>Test many tactics against each other</h2><div class="subtitle">Add a team per tactic, keep the same squad for every team so that only the tactics differ, and run several seasons. Differences smaller than the spread across seasons are probably noise.</div></div>
  <div style="text-align:right"><button class="button primary" id="lg-run" ${LG.busy ? 'disabled' : ''}>Run the league ↗</button><div class="tiny muted">${matches} matches · about ${Math.max(1, Math.round(matches / (1000 * workers) * 60))} min with ${workers} workers</div></div></div>
  <div class="card-body"><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px">${cards}</div>${ready ? '' : '<p class="tiny" style="color:#c0573f">Complete the highlighted parts before running.</p>'}</div></div>`;
}
function lgConfirm(){
 const sum = lgSummary(), s = LG.setup, ready = Object.values(sum).every(x => x.ok), matches = s.teams.length * (s.teams.length - 1) * s.seasons;
 let d = $('#lg-confirm');
 if (!d) { document.body.insertAdjacentHTML('beforeend', '<dialog id="lg-confirm"></dialog>'); d = $('#lg-confirm'); }
 d.innerHTML = `<h2>Have you set up all four parts?</h2><ol>${LG_SECTIONS.map(([id, label]) => `<li><b>${label}</b>: ${esc(sum[id].text)}${sum[id].problem ? ` <span style="color:#c0573f">(${esc(sum[id].problem)})</span>` : ''}</li>`).join('')}</ol><p class="tiny muted">${matches} matches. You can stop the league at any time and resume it later.</p>
  <div class="dialog-actions"><button class="button" id="lg-confirm-no">Not yet</button><button class="button primary" id="lg-confirm-yes" ${ready ? '' : 'disabled'}>Yes, run the league</button></div>`;
 d.showModal();
 $('#lg-confirm-no').onclick = () => d.close();
 $('#lg-confirm-yes').onclick = () => { d.close(); lgStart(); };
}
async function lgStart(){
 const s = LG.setup;
 try {
  LG.busy = true; render();
  for (const t of s.teams) if (t.tactic.kind === 'upload' && !t.tactic.token) {   // files added before uploads were separate
   if (!t.tactic.file_base64) throw Error(`${t.name}: choose its tactic file again`);
   t.tactic = {kind: 'upload', filename: t.tactic.filename, token: (await api('/api/league/upload', {filename: t.tactic.filename, file_base64: t.tactic.file_base64})).token};
  }
  lgSave();
  const teams = s.teams.map(t => ({name: t.name, tactic: t.tactic, squad: s.perTeamSquad ? (t.squad || s.squad) : s.squad, familiarity: s.perTeamFamiliarity ? (t.familiarity ?? s.familiarity) : s.familiarity}));
  const r = await api('/api/league/start', {name: s.name, teams, base_match: s.base2 && s.base2 !== s.base ? [s.base, s.base2] : s.base, seasons: s.seasons, familiarity: s.familiarity, equal_start: s.equalStart, workers: Number($('#workers')?.value || LG.opts.workers)});
  LG.id = r.id; LG.current = r.id; LG.tab = 'hub'; LG.result = null; LG.list = (await api('/api/league/list')).leagues; toast('League started'); lgPoll(true); }
 catch (e) { toast(e.message); } finally { LG.busy = false; render(); }
}
const lgNum = (v, d = 1) => v == null ? '' : Number(v).toFixed(d);
function lgResultView(){
 const r = LG.result;
 if (!r) return '';
 if (r.error && !r.table) return `<div class="results-error">${esc(r.error)}</div>`;
 const m = r.meta || {}, live = !['complete', 'stopped', 'error', 'not built'].includes(r.state);
 const head = `<div class="card-head"><div><h2>${esc(r.name)}</h2><div class="tiny muted">${r.completed} of ${r.total} matches · ${r.seasons_complete ?? 0} of ${m.seasons ?? '?'} seasons complete · ${esc(LG_STATUS[r.state] || r.state)}</div></div><div><a class="button small" href="/api/league/csv/${encodeURIComponent(r.id)}" download="league-${esc(r.id)}.csv">CSV ↓</a></div></div>`;
 // a placeholder name ("Team 5") shows as its tactic; a name the user typed stays, with the tactic underneath
 const tacticOf = Object.fromEntries((m.teams || []).map(t => [t.name, (t.tactic || '').replace(/^Preset: /, '')]));
 const shown = n => /^Team \d+( \(2\))*$/.test(n) && tacticOf[n] ? tacticOf[n] : n;
 const rows = (r.table || []).filter(x => x.seasons).map(x => `<tr><td>${x.rank}</td><td><b>${esc(shown(x.team))}</b>${shown(x.team) === (x.tactic || '').replace(/^Preset: /, '') ? '' : `<div class="tiny muted">${esc(x.tactic)}</div>`}</td><td>${lgNum(x.W)}</td><td>${lgNum(x.D)}</td><td>${lgNum(x.L)}</td><td>${lgNum(x.GF)}</td><td>${lgNum(x.GA)}</td><td>${lgNum(x.xGF, 2)}</td><td>${lgNum(x.xGA, 2)}</td><td>${lgNum(x.xPts)}</td><td><b>${lgNum(x.Pts)}</b></td><td>${x.Pts_sd == null ? '' : '±' + lgNum(x.Pts_sd)}</td><td>${lgNum(x.PPG, 2)}</td></tr>`).join('');
 const order = r.order || [], h = r.head_to_head || {};
 // colour by distance from an even 1.5 points per match: red below, green above, stronger further away; translucent
 // so the page's own text colour stays readable in light and dark mode
 const cell = (v, a, b) => {
  if (v == null) return '<td></td>';
  const d = Math.max(-1, Math.min(1, (v - 1.5) / 1.5)), rgb = d < 0 ? '220,70,60' : '60,170,90';
  return `<td title="${esc(shown(a))} against ${esc(shown(b))}: ${v.toFixed(2)} points per match" style="text-align:center;padding:8px 6px;background:rgba(${rgb},${(0.08 + 0.6 * Math.abs(d)).toFixed(2)});${Math.abs(d) > 0.45 ? 'font-weight:700' : ''}">${v.toFixed(1)}</td>`;
 };
 const grid = `<table class="tiny h2h"><thead><tr><th></th>${order.map((t, k) => `<th style="text-align:center;padding:8px 6px" title="${esc(shown(t))}">${k + 1}</th>`).join('')}</tr></thead><tbody>${order.map((a, k) => `<tr><td style="white-space:nowrap;padding:8px 10px"><b>${k + 1}</b> ${esc(shown(a))}</td>${order.map(b => a === b ? '<td style="text-align:center;opacity:.35">—</td>' : cell(h[a]?.[b], a, b)).join('')}</tr>`).join('')}</tbody></table>
  <p class="tiny muted" style="margin-top:8px"><span style="background:rgba(60,170,90,.6);padding:1px 6px;border-radius:3px">green</span> the row team took more than 1.5 points per match against the column team · <span style="background:rgba(220,70,60,.6);padding:1px 6px;border-radius:3px">red</span> fewer · bold: a clear result. Columns are numbered like the rows; hover over a cell for the names.</p>`;
 const teams = (m.teams || []).map(t => `<li>${esc(t.name)}: ${esc(t.tactic)} · ${esc(t.squad)} · familiarity ${t.familiarity}</li>`).join('');
 return `<div class="card">${head}${r.error ? `<div class="results-error">${esc(r.error)}</div>` : ''}<div class="card-body">
 ${rows ? `<div class="table-scroll"><table><thead><tr><th>#</th><th>Team</th><th>W</th><th>D</th><th>L</th><th>Goals for</th><th>Goals against</th><th>xG for</th><th>xG against</th><th>xPts</th><th>Points</th><th>Spread</th><th>Per game</th></tr></thead><tbody>${rows}</tbody></table></div>
 <p class="tiny muted">Per season, averaged over the seasons played; xG per game. Spread: standard deviation of a team's points across seasons. Differences smaller than the spread are probably noise.</p>
 <h3>Head to head</h3><p class="tiny muted">Points per match of the row team against the column team, both venues and all seasons.</p><div class="table-scroll">${grid}</div>` : `<div class="notice">${live ? 'Building the fixtures and playing the first matches…' : 'No matches played yet.'}</div>`}
 <h3>Settings</h3><ul class="tiny">${teams}</ul><p class="tiny muted">Template match: ${esc(m.base_match || '')} (${esc(m.base_match_game_version || '')}) · engine ${esc(m.engine || '')} · ${m.seasons} season(s), home and away · ${m.equal_start ? 'both sides start alike' : 'each side keeps the template\'s start state'}${m.reference_squads ? ` · synthetic squads calibrated on FM27's database ${esc(m.reference_squads.game_build)}` : ''}${(m.skipped || []).length ? ` · skipped: ${esc(m.skipped.join('; '))}` : ''}</p>
 </div></div>`;
}
const LG_STATUS = {running: 'Playing matches', building: 'Building fixtures', stopping: 'Stopping…', stopped: 'Stopped – resume to continue',
 complete: 'Complete', error: 'Error'};
// the running box: a bar in the run bar's green that starts with a sliver, fills to 10% while the fixtures are built
// (team by team), then moves with every batch of matches; a shimmer runs across it while it works
document.head.insertAdjacentHTML('beforeend', `<style>
.lg-running{border-color:#83ac64}
.lg-bar{position:relative;height:8px;border-radius:4px;background:rgba(131,172,100,.18);overflow:hidden;margin:10px 0 6px}
.lg-bar>div{height:100%;background:#83ac64;border-radius:4px;transition:width .8s ease;position:relative;overflow:hidden}
.lg-bar>div::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.55),transparent);transform:translateX(-100%);animation:lg-shimmer 1.6s ease-in-out infinite}
.lg-bar.live>div{animation:lg-pulse 1.2s ease-in-out infinite}
@keyframes lg-shimmer{to{transform:translateX(100%)}}
@keyframes lg-pulse{50%{opacity:.65}}
</style>`);
const lgLive = l => ['running', 'building', 'stopping'].includes(l.state);
function lgProgress(l){
 if (l.state === 'complete') return 100;
 if (l.state === 'building') return 3 + 7 * ((l.built || 0) / (l.build_total || l.teams || 1));
 if (!l.total) return 3;
 return 10 + 90 * l.completed / l.total;
}
function lgRunningView(){
 const live = (LG.list || []).filter(lgLive);
 if (!live.length) return '';
 return live.map(l => {
  const line = l.state === 'building' ? `Building fixtures: ${l.built || 0} of ${l.build_total || l.teams} teams`
   : l.state === 'stopping' ? `Stopping after the matches in progress (${l.completed} of ${l.total} played)`
   : `Playing matches: ${l.completed} of ${l.total}`;
  return `<div class="card lg-running" style="margin-bottom:18px"><div class="card-head"><div><div class="tiny muted">RUNNING NOW</div><h3>${esc(l.name)}</h3></div><div style="white-space:nowrap"><button class="button small ${l.id === LG.id ? 'primary' : ''}" data-lg-open="${esc(l.id)}">${l.id === LG.id ? 'Showing below' : 'Show results so far'}</button> ${l.state === 'stopping' ? '' : `<button class="button small" data-lg-stop="${esc(l.id)}">Stop</button>`}</div></div>
   <div class="card-body"><div class="lg-bar live"><div style="width:${lgProgress(l).toFixed(1)}%"></div></div><div class="tiny muted">${esc(line)} · ${l.teams} teams, ${l.seasons} season(s) · results arrive in batches of up to 30 matches</div></div></div>`;
 }).join('');
}
function lgListView(){
 const others = (LG.list || []).filter(l => !lgLive(l));
 if (!others.length) return `<div class="card"><div class="card-body"><p>No previous leagues yet.</p><button class="button primary" data-lg-tab="hub">Set up and run a league</button></div></div>`;
 const rows = others.map(l => {
  const live = ['running', 'building', 'stopping'].includes(l.state), pct = l.total ? Math.round(100 * l.completed / l.total) : 0;
  const when = l.created ? new Date(l.created * 1000).toLocaleString('en-GB', {day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'}) : '';
  const actions = [`<button class="button small ${l.id === LG.id ? 'primary' : ''}" data-lg-open="${esc(l.id)}">${l.id === LG.id ? 'Showing' : 'Open'}</button>`,
   live ? `<button class="button small" data-lg-stop="${esc(l.id)}">Stop</button>` : (l.completed < l.total || !l.total) ? `<button class="button small" data-lg-resume="${esc(l.id)}">Resume</button>` : '',
   live ? '' : `<button class="button small ghost" data-lg-remove-league="${esc(l.id)}" title="Remove this league and its results">Remove</button>`].join(' ');
  return `<tr><td><b>${esc(l.name)}</b><div class="tiny muted">${esc(when)}</div></td><td>${l.teams}</td><td>${l.seasons ?? ''}</td>
   <td style="min-width:12em"><div style="background:rgba(128,128,128,.3);border-radius:4px;height:6px;overflow:hidden"><div style="width:${pct}%;height:6px;background:#8b5cf6"></div></div><span class="tiny muted">${l.completed} of ${l.total} matches</span></td>
   <td>${esc(LG_STATUS[l.state] || l.state)}</td><td style="white-space:nowrap">${actions}</td></tr>`;
 }).join('');
 return `<div class="card" style="margin-bottom:18px"><div class="card-head"><h3>Previous leagues</h3></div><div class="table-scroll"><table><thead><tr><th>League</th><th>Teams</th><th>Seasons</th><th>Progress</th><th>Status</th><th></th></tr></thead><tbody>${rows}</tbody></table></div>
  <p class="tiny muted" style="padding:0 16px 12px">One league plays at a time; a stopped league resumes where it stopped. Open one to see its table below.</p></div>`;
}
function lgTabs(){
 const tab = (id, label) => `<button class="button ${LG.tab === id ? 'primary' : ''}" data-lg-tab="${id}">${label}</button>`;
 const previous = (LG.list || []).filter(l => !lgLive(l)).length;
 return `<div class="toolbar"><div class="toolbar-left">${tab('hub', 'Set up & run')} ${tab('previous', 'Previous leagues' + (previous ? ` (${previous})` : ''))}</div></div>`;
}
function leagueView(){
 if (LG.error) return `<div class="results-error">${esc(LG.error)}</div>`;
 if (!LG.opts) return '<div class="loading">Reading presets, reference squads and your matches…</div>';
 if (!LG.tab || !['hub', 'previous', ...LG_SECTIONS.map(x => x[0])].includes(LG.tab)) LG.tab = 'hub';
 if (LG_SECTIONS.some(([id]) => id === LG.tab)) return lgSectionNav() + lgSectionView();
 if (LG.tab === 'previous') return lgTabs() + lgListView() + (LG.id && LG.id !== LG.current ? lgResultView() : '');
 // the hub: the set-up, the run, anything running, and the results of the league run here (earlier ones are under Previous)
 const shown = LG.id && (LG.id === LG.current || (LG.list || []).some(l => l.id === LG.id && lgLive(l)));
 return lgTabs() + lgHubView() + lgRunningView() + (shown ? lgResultView() : '');
}

function lgB64(file){ return new Promise((ok, bad) => { const r = new FileReader(); r.onload = () => ok(String(r.result).split(',')[1]); r.onerror = bad; r.readAsDataURL(file); }); }
function lgSetSquad(key, sq){ if (key === 'all') LG.setup.squad = sq; else LG.setup.teams[Number(key.slice(1))].squad = sq; }
function lgGetSquad(key){ return key === 'all' ? LG.setup.squad : (LG.setup.teams[Number(key.slice(1))].squad || {...LG.setup.squad}); }
function lgBind(){
 const s = LG.setup, rerender = () => { lgSave(); render(); };
 const on = (sel, ev, fn) => { const el = $(sel); if (el) el[ev] = fn; };
 on('#lg-name', 'onchange', e => { s.name = e.target.value; lgSave(); });
 // a team is named after its tactic until the user types a name of their own
 const tacticName = t => t.kind === 'preset' ? t.style : (t.filename || '').replace(/\.fmf$/i, '');
 const autoNamed = team => /^Team \d+$/.test(team.name) || team.name === tacticName(team.tactic);
 on('#lg-add', 'onclick', () => { if (s.teams.length >= 20) return toast('At most 20 teams');
  const used = new Set(s.teams.map(t => t.tactic.kind === 'preset' && t.tactic.style)), style = LG.opts.presets.find(p => !used.has(p)) || LG.opts.presets[0];
  s.teams.push({name: style, tactic: {kind: 'preset', style}}); rerender(); });
 on('#lg-presets', 'onclick', () => { const have = new Set(s.teams.filter(t => t.tactic.kind === 'preset').map(t => t.tactic.style)); LG.opts.presets.filter(p => !have.has(p)).forEach(p => s.teams.length < 20 && s.teams.push({name: p, tactic: {kind: 'preset', style: p}})); rerender(); });
 on('#lg-clear', 'onclick', () => { s.teams = []; rerender(); });
 on('#lg-folder', 'onclick', () => $('#lg-folder-input').click());
 on('#lg-folder-input', 'onchange', async e => { const files = [...e.target.files].filter(f => f.name.toLowerCase().endsWith('.fmf')).sort((a, b) => a.name.localeCompare(b.name));
  for (const f of files) { if (s.teams.length >= 20) { toast('At most 20 teams'); break; } try { s.teams.push({name: f.name.replace(/\.fmf$/i, ''), tactic: await lgUpload(f)}); } catch (e) { toast(e.message); } }
  if (!files.length) toast('No .fmf files in that folder'); rerender(); });
 $$('[data-lg-name]').forEach(el => el.onchange = () => { s.teams[el.dataset.lgName].name = el.value; lgSave(); });
 $$('[data-lg-remove]').forEach(el => el.onclick = () => { s.teams.splice(Number(el.dataset.lgRemove), 1); rerender(); });
 $$('[data-lg-fam]').forEach(el => el.onchange = () => { s.teams[el.dataset.lgFam].familiarity = Number(el.value); lgSave(); });
 $$('[data-lg-tactic]').forEach(el => el.onchange = () => { const k = Number(el.dataset.lgTactic), v = el.value;
  if (v.startsWith('preset:')) { const auto = autoNamed(s.teams[k]); s.teams[k].tactic = {kind: 'preset', style: v.slice(7)}; if (auto) s.teams[k].name = tacticName(s.teams[k].tactic); return rerender(); }
  if (v === 'choose') { const input = $('#lg-file-input'); input.value = ''; input.onchange = async () => { const f = input.files[0]; if (f) { const auto = autoNamed(s.teams[k]); try { s.teams[k].tactic = await lgUpload(f); } catch (e) { toast(e.message); return; } if (auto) s.teams[k].name = tacticName(s.teams[k].tactic); } rerender(); }; input.click(); } });
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
 on('#lg-base', 'onchange', e => { s.base = e.target.value; s.baseChosen = true; lgSave(); });
 on('#lg-base2', 'onchange', e => { s.base2 = e.target.value; lgSave(); });
 on('#lg-run', 'onclick', lgConfirm);
 $$('[data-lg-tab]').forEach(el => el.onclick = () => { LG.tab = el.dataset.lgTab; render(); window.scrollTo(0, 0); });
 const refreshList = async () => { LG.list = (await api('/api/league/list')).leagues; };
 $$('[data-lg-open]').forEach(el => el.onclick = () => { LG.id = el.dataset.lgOpen; LG.result = null; render(); lgPoll(true); });
 $$('[data-lg-stop]').forEach(el => el.onclick = async () => { await api('/api/league/stop', {id: el.dataset.lgStop}); toast('Stopping after the matches in progress'); await refreshList(); LG.id = el.dataset.lgStop; lgPoll(true); });
 $$('[data-lg-resume]').forEach(el => el.onclick = async () => { try { await api('/api/league/resume', {id: el.dataset.lgResume, workers: Number($('#workers')?.value || LG.opts.workers)}); LG.id = el.dataset.lgResume; await refreshList(); lgPoll(true); } catch (e) { toast(e.message); } });
 $$('[data-lg-remove-league]').forEach(el => el.onclick = async () => { const id = el.dataset.lgRemoveLeague, l = LG.list.find(x => x.id === id);
  if (!confirm(`Remove the league "${l?.name}" and its results?`)) return;
  try { await api('/api/league/delete', {id}); if (LG.id === id) { LG.id = null; LG.result = null; } await refreshList(); if (!LG.id && LG.list.length) LG.id = LG.list[0].id; render(); if (LG.id) lgPoll(true); } catch (e) { toast(e.message); } });
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
