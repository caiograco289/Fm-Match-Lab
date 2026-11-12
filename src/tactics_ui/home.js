'use strict';
// Home page and the two areas: "Test a tactic" (its hub is the results page: the four components, the run, the
// results; earlier runs under "Previous runs") and "Test a league" (league.js). The bottom run bar is replaced by the
// run panel on the hub; its inputs stay in the page, hidden, and the hub's controls write to them.
const TA = {tab: 'hub', current: null, fam: (() => { try { const v = JSON.parse(localStorage.getItem('fm27-tactic-familiarity')); return Array.isArray(v) && v.length === 2 ? v : [null, null]; } catch (e) { return [null, null]; } })()};
const famSave = () => { try { localStorage.setItem('fm27-tactic-familiarity', JSON.stringify(TA.fam)); } catch (e) {} };
const famText = (hold, names) => [0, 1].map(i => `${esc(names[i])}: ${hold?.[i] == null ? 'as in the match' : 'held at ' + hold[i]}`).join(' · ');
// held tactical familiarity goes with every run (both the tactic and the reference), as the studies and leagues do
const homeApiPrevious = api;
api = async function(url, data){
 if (url === '/api/run' && data && TA.fam.some(v => v != null)) {
  data = {...data, scenario: {...data.scenario, familiarity_hold: TA.fam.slice()}};
  if (data.reference) data.reference = {...data.reference, familiarity_hold: TA.fam.slice()};
 }
 return homeApiPrevious(url, data);
};
const TACTIC_PARTS = [['tactics', 'Tactics', 'Formation, roles, team and player instructions, mentality, for the home and the away side.'],
 ['players', 'Player attributes', 'Every attribute of every player, for either side.'],
 ['opposition', 'Opposition instructions', 'How each side treats the other side\'s players: pressing, marking, tackling, which foot to show.'],
 ['setpieces', 'Set pieces', 'Routines, takers, captains and throw-ins.']];
const TACTIC_VIEWS = ['results', ...TACTIC_PARTS.map(p => p[0])];

document.head.insertAdjacentHTML('beforeend', `<style>
.runbar{display:none}
.rail nav [data-view="tactics"],.rail nav [data-view="players"],.rail nav [data-view="opposition"],.rail nav [data-view="setpieces"],.rail nav [data-view="results"],.rail nav [data-view="league"]{display:none}
.home-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:22px;max-width:1100px}
.home-card{text-align:left;padding:28px;border-radius:14px;cursor:pointer;transition:transform .15s,box-shadow .15s}
.home-card:hover{transform:translateY(-2px);box-shadow:0 8px 26px rgba(0,0,0,.18)}
.home-card h2{font-size:22px;margin:6px 0 10px}.home-card ol,.home-card p{font-size:13px;line-height:1.75}
.parts{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}
.part{padding:16px}.part .state{font-size:11px;margin:6px 0 10px;min-height:2.6em}.part .changed{color:#6aa84f}
</style>`);

// the rail: Home, Test a tactic, Test a league, then Saved matches and Guide
(function rail(){
 const nav = $('.rail nav'), first = nav.firstChild;
 for (const [area, symbol, label] of [['home', '⌂', 'Home'], ['tactic', '◈', 'Test a tactic'], ['league', '▦', 'Test a league']]) {
  const b = document.createElement('button'); b.dataset.area = area; b.innerHTML = `${symbol} <span>${label}</span>`;
  b.onclick = () => { view = area === 'home' ? 'home' : area === 'tactic' ? 'results' : 'league'; if (area === 'tactic') TA.tab = 'hub'; if (area === 'league' && typeof LG !== 'undefined') LG.tab = 'hub'; render(); window.scrollTo(0, 0); if (area === 'league' && typeof lgLoad === 'function') lgLoad(); };
  nav.insertBefore(b, first);
 }
})();
view = 'home';

function homeView(){
 return `<div class="home-cards">
  <div class="card home-card" data-go="tactic"><div class="tiny muted">1</div><h2>Test a tactic ↗</h2>
   <p>Take one match, change something, and see what difference it makes over many simulated replays.</p>
   <ol><li>Choose the match: one FM27 saved, or the built-in sample.</li><li>Set up the four parts: tactics (home and away), player attributes, opposition instructions, set pieces.</li>
   <li>Run hundreds of matches. Save a reference tactic first to compare two versions on the same seeds.</li></ol>
   <p class="tiny muted">Good for: is this change better for my team in this kind of match?</p></div>
  <div class="card home-card" data-go="league"><div class="tiny muted">2</div><h2>Test a league ↗</h2>
   <p>Many tactics play each other, home and away, over several seasons, with the same squad for every team so only the tactics differ.</p>
   <ol><li>Set up the four parts: teams and tactics, squads, familiarity and format, template match.</li><li>Run the league; it can stop and resume.</li>
   <li>Read the table: points with the spread across seasons, head to head, CSV.</li></ol>
   <p class="tiny muted">Good for: which tactic is strongest overall?</p></div></div>
  <p class="small-note">Everything runs FM27's own match engine from your Steam install, on this Mac. Results stay here.</p>`;
}

// the tactic hub: what each part looks like now compared with the match as loaded
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
function tacticStatus(){
 const sideNames = [0, 1].map(i => state.teams[i].name || ['Home', 'Away'][i]);
 const per = f => [0, 1].map(i => f(state.teams[i], defaults.teams[i]));
 const tac = per((t, d) => !same([t.phases, t.instructions, t.mentality, t.lineup], [d.phases, d.instructions, d.mentality, d.lineup]));
 const att = per((t, d) => t.players.filter((p, k) => !same(p.attributes, d.players[k]?.attributes)).length);
 const opp = per((t, d) => !same(t.opposition, d.opposition));
 const sp = per((t, d) => !same([t.setpieces, t.takers, t.captains], [d.setpieces, d.takers, d.captains]));
 const two = (vals, fmt) => vals.map((v, i) => `${esc(sideNames[i])}: ${fmt(v)}`).join('<br>');
 return {tactics: two(tac, v => v ? '<span class="changed">changed</span>' : 'as in the match'),
  players: two(att, v => v ? `<span class="changed">${v} player${v === 1 ? '' : 's'} edited</span>` : 'as in the match'),
  opposition: two(opp, v => v ? '<span class="changed">changed</span>' : 'as in the match'),
  setpieces: two(sp, v => v ? '<span class="changed">changed</span>' : 'as in the match')};
}
function matchLabel(){ return typeof isSavedBase === 'function' && isSavedBase() && state.match_base ? `${state.match_base.home} v ${state.match_base.away} (saved match, seed ${state.match_base.seed})` : 'the built-in sample match'; }
function runSettings(){
 const workers = $('#workers'), compare = $('#compare');
 return `<div style="display:flex;gap:14px;align-items:end;flex-wrap:wrap">
  <label class="tiny">Start seed<br><input id="hub-seed" type="number" min="0" value="${esc($('#seed').value)}" style="width:8em"></label>
  <label class="tiny">Matches<br><input id="hub-count" type="number" min="1" max="10000" value="${esc($('#count').value)}" style="width:6em"></label>
  <label class="tiny">Workers<br><select id="hub-workers">${workers.innerHTML}</select></label>
  <label class="tiny" title="${reference ? 'Runs the saved reference tactic and this one on the same seeds' : 'Save a reference tactic on the Tactics page first'}"><input id="hub-compare" type="checkbox" ${compare.checked ? 'checked' : ''} ${reference ? '' : 'disabled'}> compare with the saved reference tactic</label>
  <label class="tiny">Name (optional)<br><input id="hub-name" value="${esc($('#experiment-name')?.value || '')}" placeholder="named automatically" style="width:14em"></label></div>
  <div class="tiny" style="margin-top:12px"><b>Tactical familiarity</b> ${[0, 1].map(i => `<span style="margin-left:10px">${esc(state.teams[i].name || ['Home', 'Away'][i])}: <select data-fam-side="${i}"><option value="" ${TA.fam[i] == null ? 'selected' : ''}>as in the match</option><option value="hold" ${TA.fam[i] != null ? 'selected' : ''}>held at</option></select>${TA.fam[i] != null ? ` <input type="number" min="0" max="100" data-fam-level="${i}" value="${TA.fam[i]}" style="width:4.5em">` : ''}</span>`).join('')}
   <div class="muted" style="margin-top:4px">"Held at" sets training and match exposure in all eight tactical areas for every player of that side, for the whole match (0-100; Study 3: the gain flattens from about 50). Player tactical ability and tactic complexity stay as stored.</div></div>`;
}
function tacticHub(){
 const st = tacticStatus(), j = polledJob && polledJob.id === activeJob ? polledJob : null, busy = !!j && ['queued', 'running'].includes(j.status);
 const parts = TACTIC_PARTS.map(([id, label, what], k) => `<div class="card part"><div class="tiny muted">${k + 1}</div><h3>${label}</h3><div class="tiny muted">${what}</div><div class="state">${st[id]}</div><button class="button small" data-goto-part="${id}">Set up →</button></div>`).join('');
 const bar = j ? `<div class="lg-bar ${busy ? 'live' : ''}"><div style="width:${(busy ? Math.max(3, 100 * j.completed / Math.max(1, j.total)) : 100).toFixed(1)}%"></div></div><div class="tiny muted">${busy ? `Simulating ${j.completed} of ${j.total} matches` : j.status === 'complete' ? 'Finished' : esc(j.status)}</div>` : '';
 return `<div class="card" style="margin-bottom:18px"><div class="card-head"><div><h2>Test a tactic</h2><div class="subtitle">Match: <b>${esc(matchLabel())}</b> · <a href="#" data-goto-saved>choose another match</a></div></div>
  <div style="text-align:right">${busy ? '<button class="button" id="hub-cancel">Stop</button>' : '<button class="button primary" id="hub-run">Run matches ↗</button>'}</div></div>
  <div class="card-body"><div class="parts">${parts}</div><div style="margin-top:16px">${runSettings()}</div>${bar}${j?.familiarity_hold ? `<div class="tiny muted">This run: tactical familiarity ${famText(Object.values(j.familiarity_hold)[0], ['Home', 'Away'])}</div>` : ''}</div></div>`;
}
function tacticTabs(){
 const tab = (id, label) => `<button class="button ${TA.tab === id ? 'primary' : ''}" data-ta-tab="${id}">${label}</button>`;
 return `<div class="toolbar"><div class="toolbar-left">${tab('hub', 'Set up & run')} ${tab('previous', 'Previous runs' + (history?.length ? ` (${history.length})` : ''))}</div></div>`;
}
function partNav(){
 const i = TACTIC_PARTS.findIndex(p => p[0] === view), next = TACTIC_PARTS[i + 1];
 return `<div class="toolbar" id="part-nav"><div class="toolbar-left"><button class="button small" data-goto-hub>← Results & run</button><div class="segmented">${TACTIC_PARTS.map(([id, label], k) => `<button data-goto-part="${id}" class="${id === view ? 'active' : ''}">${k + 1}. ${label}</button>`).join('')}</div></div><div class="toolbar-right">${next ? `<button class="button small" data-goto-part="${next[0]}">Next: ${next[1]} →</button>` : '<button class="button small primary" data-goto-hub>Done – back to run</button>'}</div></div>`;
}
function confirmRun(){
 const st = tacticStatus();
 let d = $('#ta-confirm');
 if (!d) { document.body.insertAdjacentHTML('beforeend', '<dialog id="ta-confirm"></dialog>'); d = $('#ta-confirm'); }
 const n = Number($('#count').value) * ($('#compare').checked ? 2 : 1);
 d.innerHTML = `<h2>Have you set up all four parts?</h2><p class="tiny">Match: <b>${esc(matchLabel())}</b></p><ol>${TACTIC_PARTS.map(([id, label]) => `<li><b>${label}</b><div class="tiny">${st[id]}</div></li>`).join('')}</ol>
  <p class="tiny muted">${n} matches from seed ${esc($('#seed').value)}${$('#compare').checked ? ', the saved reference tactic and this one on the same seeds' : ''}.</p>
  <p class="tiny">Tactical familiarity: ${famText(TA.fam, [0, 1].map(i => state.teams[i].name || ['Home', 'Away'][i]))}</p>
  <div class="dialog-actions"><button class="button" id="ta-no">Not yet</button><button class="button primary" id="ta-yes">Yes, run</button></div>`;
 d.showModal();
 $('#ta-no').onclick = () => d.close();
 $('#ta-yes').onclick = async () => { d.close(); TA.tab = 'hub'; await run(); TA.current = activeJob; render(); };
}

const homeRenderPrevious = render;
render = function(){
 if (view === 'home') {
  $('#page-title').textContent = 'What would you like to test?';
  $('#workspace').innerHTML = homeView();
  $$('[data-go]').forEach(c => c.onclick = () => $(`.rail nav [data-area="${c.dataset.go}"]`).click());
 } else {
  homeRenderPrevious();
  if (activeJob) TA.current = activeJob;
  if (TACTIC_PARTS.some(p => p[0] === view)) $('#workspace').insertAdjacentHTML('afterbegin', partNav());
  if (view === 'results') {
   $('#page-title').textContent = TA.tab === 'previous' ? 'Earlier runs' : 'Test a tactic';
   const ws = $('#workspace');
   if (TA.tab === 'hub') {
    // only this run's results here; earlier ones live under "Previous runs"
    if (!selectedJob || selectedJob.id !== TA.current) ws.innerHTML = '';
    ws.querySelector('.history')?.remove();
    ws.insertAdjacentHTML('afterbegin', tacticTabs() + tacticHub());
   } else ws.insertAdjacentHTML('afterbegin', tacticTabs() + (history?.length ? '<p class="tiny muted">Choose a run below to see its results.</p>' : '<p>No earlier runs yet.</p>'));
  }
 }
 const area = view === 'home' ? 'home' : TACTIC_VIEWS.includes(view) ? 'tactic' : view === 'league' ? 'league' : null;
 $$('.rail nav [data-area]').forEach(b => b.classList.toggle('active', b.dataset.area === area));
 bindHub();
};
function bindHub(){
 $$('[data-goto-part]').forEach(b => b.onclick = () => { view = b.dataset.gotoPart; render(); window.scrollTo(0, 0); });
 $$('[data-goto-hub]').forEach(b => b.onclick = () => { view = 'results'; TA.tab = 'hub'; render(); window.scrollTo(0, 0); });
 $$('[data-goto-saved]').forEach(a => a.onclick = e => { e.preventDefault(); $('.rail nav [data-view="saved"]').click(); });
 $$('[data-ta-tab]').forEach(b => b.onclick = () => { TA.tab = b.dataset.taTab; render(); });
 const sync = (id, target, prop = 'value') => { const el = $(id); if (el) el.onchange = () => { $(target)[prop] = el[prop]; }; };
 sync('#hub-seed', '#seed'); sync('#hub-count', '#count'); sync('#hub-compare', '#compare', 'checked');
 const w = $('#hub-workers'); if (w) { w.value = $('#workers').value; w.onchange = () => { $('#workers').value = w.value; }; }
 const nm = $('#hub-name'); if (nm && $('#experiment-name')) nm.onchange = () => { $('#experiment-name').value = nm.value; };
 $$('[data-fam-side]').forEach(s => s.onchange = () => { const i = Number(s.dataset.famSide); TA.fam[i] = s.value === 'hold' ? 70 : null; famSave(); render(); });
 $$('[data-fam-level]').forEach(n => n.onchange = () => { const i = Number(n.dataset.famLevel), v = Math.round(Number(n.value)); TA.fam[i] = Number.isFinite(v) ? Math.max(0, Math.min(100, v)) : 70; famSave(); });
 if ($('#hub-run')) $('#hub-run').onclick = confirmRun;
 if ($('#hub-cancel')) $('#hub-cancel').onclick = () => $('#cancel').click();
}
