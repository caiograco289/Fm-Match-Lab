'use strict';
// Saved matches (macOS): matches FM27 saved itself (instant result or watched; matches/automatic) as the base of the
// editor. Opening one loads the real squads, tactics and player states; an unedited scenario on the match's own seed
// replays it exactly, and every edit becomes a what-if on that match. The bundled sample stays one click away.
let savedMatches = null, savedBusy = false;
const MANAGED_LABELS = {human: 'You (managed or watched)', assistant: 'Assistant (instant result / holiday)', ai: 'Computer'};
const isSavedBase = () => typeof state?.fixture === 'string' && state.fixture.startsWith('saved:');

$('.rail nav').insertAdjacentHTML('beforeend', '<button data-view="saved">⇆ <span>Saved matches</span></button>');
$('.rail nav [data-view="saved"]').onclick = () => { view = 'saved'; render(); window.scrollTo(0, 0); loadSavedMatches(); };

function savedWhen(t){ return new Date(t * 1000).toLocaleString('en-GB', {month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit'}); }
function savedView(){
 const current = isSavedBase() ? state.match_base : null;
 const head = `<div class="card"><div class="card-head"><div><h2>FM27 saved matches</h2><div class="subtitle">Matches played as instant result or watched are saved automatically (holiday matches are not saved on 27.0.1). Once opened, the editor uses the real teams, tactics and player states of that match; with no changes and the original seed it replays the game’s result exactly, and any change is a “what if”. </div></div></div>
 <p class="tiny muted">Note: a match you managed, with substitutions or changes, replays your recorded substitutions; in a match you only watched, your team makes no substitutions at all. Instant-result matches are the best for comparisons. Save before the match, play it with instant result, then open it here.</p>
 ${current ? `<p>The editor is currently based on: <b>${esc(current.home)} v ${esc(current.away)}</b> (${esc(current.competition)} · Seed ${current.seed}) <button class="button small" id="saved-bundled">Back to the built-in sample match</button></p>` : '<p class="tiny muted">The editor is currently based on the built-in sample match.</p>'}</div>`;
 if (!savedMatches) return head + '<div class="loading">Reading saved matches…</div>';
 if (savedMatches.error) return head + `<div class="results-error">${esc(savedMatches.error)}</div>`;
 if (!savedMatches.available) return head + `<div class="results-error">Could not find the FM27 saved matches folder: ${esc(savedMatches.folder)}</div>`;
 const rows = savedMatches.matches.map(m => {
  const version = m.game_version ? (m.game_version === savedMatches.installed_game_version ? `<span class="tag">${esc(m.game_version)}</span>` : `<span class="tag" title="This match was saved by another game version; the current engine cannot replay it exactly">${esc(m.game_version)} ≠ installed ${esc(savedMatches.installed_game_version)}</span>`) : '';
  const active = current && current.key === m.key ? ' <span class="tag">Editing</span>' : '';
  const kept = m.kept_copy_only ? ' <span class="tiny muted"> (deleted by the game; using the local copy)</span>' : '';
  const who = m.managed_by ? `<div class="tiny muted">${[m.home, m.away].map((t, s) => `${esc(t)}: ${esc(MANAGED_LABELS[m.managed_by[s]])}`).join(' · ')}</div>` : '';
  const actions = m.path || m.opened ? `<button class="button small" data-saved-open="${esc(m.key)}">Open in editor</button> <button class="button small primary" data-saved-replay="${esc(m.key)}">Exact replay</button>` : '';
  return `<tr><td>${savedWhen(m.modified)}</td><td>${esc(m.competition)}</td><td><b>${esc(m.home)}</b> v <b>${esc(m.away)}</b>${active}${kept}${who}</td><td>${m.seed}</td><td>${version}</td><td>${actions}</td></tr>`;
 }).join('');
 return head + `<div class="card"><table class="saved-matches"><thead><tr><th>Saved</th><th>Competition</th><th>Match</th><th>Seed</th><th>Version</th><th></th></tr></thead><tbody>${rows || '<tr><td colspan="6" class="muted">No saved matches yet</td></tr>'}</tbody></table><p class="tiny muted">Folder: ${esc(savedMatches.folder)}</p></div>`;
}
async function loadSavedMatches(){
 try { savedMatches = await api('/api/saved-matches'); } catch (e) { savedMatches = {error: e.message}; }
 if (view === 'saved') render();
}
async function openSavedMatch(key){
 const row = savedMatches?.matches.find(m => m.key === key);
 if (!row) throw Error('Match not found');
 const result = row.path ? await api('/api/saved-matches/open', {path: row.path}) : {key, defaults: await api('/api/defaults?fixture=' + encodeURIComponent(key))};
 defaults = result.defaults; state = clone(defaults); side = phase = slot = player = 0;
 if (reference && reference.fixture !== state.fixture) { reference = null; localStorage.removeItem('fm27-lab-reference-v1'); $('#compare').checked = false; }
 save();
 return row;
}
function useBundled(){
 api('/api/defaults').then(d => {
  defaults = d; state = clone(d); side = phase = slot = player = 0;
  if (reference && reference.fixture !== state.fixture) { reference = null; localStorage.removeItem('fm27-lab-reference-v1'); $('#compare').checked = false; }
  save(); render(); toast('Back to the built-in sample match');
 }).catch(e => toast(e.message));
}

const savedRenderPrevious = render;
render = function(){
 if (view !== 'saved') return savedRenderPrevious();
 if (!savedMatches) loadSavedMatches();
 $('#page-title').textContent = 'Experiment with your own matches';
 $$('[data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === view));
 $('#workspace').innerHTML = savedView();
 $$('[data-saved-open]').forEach(b => { b.disabled = savedBusy; b.onclick = async () => {
  try { savedBusy = true; b.textContent = 'Reading…'; const row = await openSavedMatch(b.dataset.savedOpen);
   $('#seed').value = row.seed; $('#count').value = 1; view = 'tactics'; toast(`Opened ${row.home} v ${row.away}: start seed set to the match’s own seed`); }
  catch (e) { toast('Open failed: ' + e.message); } finally { savedBusy = false; render(); } }; });
 $$('[data-saved-replay]').forEach(b => { b.disabled = savedBusy || !!activeJob; b.onclick = async () => {
  try { savedBusy = true; b.textContent = 'Preparing…'; const row = await openSavedMatch(b.dataset.savedReplay);
   $('#seed').value = row.seed; $('#count').value = 1;
   const result = await api('/api/run', {workers: 1, scenario: clone(state), seeds: [row.seed], name: `Replay · ${row.home} v ${row.away}`});
   activeJob = result.id; polledJob = null; selectedJob = null; view = 'results'; savedBusy = false; await poll(); }
  catch (e) { toast('Replay failed: ' + e.message); savedBusy = false; render(); } }; });
 if ($('#saved-bundled')) $('#saved-bundled').onclick = useBundled;
};

// Every other view: say which match the editor is working on, and that players keep their stored state.
const savedToolbarPrevious = toolbar;
toolbar = function(){
 let html = savedToolbarPrevious();
 if (!isSavedBase()) return html;
 const m = state.match_base;
 html = html.replace(/<p class="tiny muted controlled-state-note">[\s\S]*?<\/p>/, '<p class="tiny muted controlled-state-note">Players keep the start state stored in the saved match (condition, sharpness, morale, cohesion); only values you changed are written.</p>');
 const warn = (m.exact_replay ? '' : ` · <b>This match was saved by ${esc(m.game_version)} , installed ${esc(m.installed_game_version)}: cannot be replayed exactly</b>`)
  + (m.managed_by || []).map((w, s) => w === 'human' && state.teams[s].in_match === 'saved' ? `<br>${esc(state.teams[s].name)} was managed or watched by you in this match: replaying it as saved repeats your substitutions (a watched side makes none). For what-if experiments, set it below to “Assistant manages”. ` : '').join('');
 return `<div class="saved-base-banner">Based on saved match <b>${esc(m.home)} v ${esc(m.away)}</b> (${esc(m.competition)} · original seed ${m.seed}${warn}) <button class="button small" data-saved-seed="${m.seed}">Use original seed</button> <button class="button small" data-goto="saved">Change match</button></div>` + html;
};
const savedBindPrevious = bind;
bind = function(){
 savedBindPrevious();
 $$('[data-saved-seed]').forEach(b => b.onclick = () => { $('#seed').value = b.dataset.savedSeed; toast('Start seed set to the match’s own seed; 1 match is an exact replay, more matches show other ways the same match could go'); });
};

// After boot: a saved-match scenario restored from this browser needs its own defaults (reset, per-player reset).
(async () => {
 while (!state) await new Promise(r => setTimeout(r, 100));
 if (isSavedBase()) {
  try { defaults = await api('/api/defaults?fixture=' + encodeURIComponent(state.fixture)); }
  catch (e) { toast('The saved match is no longer available; back to the built-in sample: ' + e.message); defaults = await api('/api/defaults'); state = clone(defaults); save(); }
  render();
 }
})();
