'use strict';
// In-match management per team (macOS host): who makes decisions once the match starts.
// fixed: your tactic, no substitutions or in-match changes (the app's earlier behaviour); assistant: your tactic is
// kept and the assistant substitutes, as with an instant result; ai: the AI manager re-plans roles at kick-off and
// manages the match; saved: as stored in the saved match (a match you managed replays your own substitutions).
const IN_MATCH_LABELS = {
 assistant: 'Assistant manages (keeps your tactic, makes substitutions; like instant result)',
 fixed: 'Fixed tactic (no substitutions or changes all match)',
 ai: 'AI  manager (re-plans roles its own way at kick-off and adjusts during the match)',
 saved: 'As saved (a match you managed replays your substitutions)',
};
function inMatchModes(){ return isSavedBase() ? ['saved', 'assistant', 'ai'] : ['assistant', 'fixed', 'ai']; }
const inMatchToolbarPrevious = toolbar;
toolbar = function(){
 const html = inMatchToolbarPrevious(); if (view !== 'tactics') return html;
 const rows = [0, 1].map(s => {
  const t = state.teams[s], mode = t.in_match || (isSavedBase() ? 'saved' : 'fixed');
  return `<label class="field in-match-field"><span>${esc(t.name || ['Home', 'Away'][s])} ·  in-match management</span><select data-in-match="${s}">${inMatchModes().map(m => `<option value="${m}" ${m === mode ? 'selected' : ''}>${esc(IN_MATCH_LABELS[m])}</option>`).join('')}</select></label>`;
 }).join('');
 return html + `<div class="in-match-grid">${rows}</div>`;
};
const inMatchBindPrevious = bind;
bind = function(){
 inMatchBindPrevious();
 $$('[data-in-match]').forEach(e => e.onchange = () => { state.teams[+e.dataset.inMatch].in_match = e.value; save(); render(); toast('In-match management: ' + IN_MATCH_LABELS[e.value]); });
};
const inMatchResultsPrevious = resultsView;
resultsView = function(){
 const j = selectedJob, modes = j?.in_match?.B || j?.in_match?.A;
 const note = modes ? `<p class="tiny muted">In-match management: ${modes.map((m, s) => `${esc(j.team_names?.B?.[s] || ['Home', 'Away'][s])} ${esc(IN_MATCH_LABELS[m] || m)}`).join(' / ')}</p>` : '';
 return note + inMatchResultsPrevious();
};
