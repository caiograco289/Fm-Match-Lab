'use strict';
// Experimental start state: condition, match sharpness, fatigue, morale, team and club cohesion.
// Off by default (the controlled start); applying values switches the scenario to initial_state "custom".
const initialStateFields = [
 {key:'condition', label:'Condition (%)', min:0, max:100, scale:100, value:100},
 {key:'sharpness', label:'Match sharpness (%)', min:0, max:100, scale:100, value:100},
 {key:'fatigue_raw', label:'Fatigue (raw 0–65535)', min:0, max:65535, scale:1, value:0},
 {key:'morale', label:'Morale (1–20)', min:1, max:20, scale:1, value:20},
 {key:'team_cohesion', label:'Team cohesion (0–100)', min:0, max:100, scale:1, value:80},
 {key:'club_cohesion', label:'Club cohesion (0–100)', min:0, max:100, scale:1, value:100},
];
const initialStateValues = [{}, {}];

const initialStatePlayersPrevious = playersView;
playersView = function(){
 const custom = state.initial_state === 'custom';
 const values = initialStateValues[side];
 const range = (state.match_base?.cohesion_ranges || catalog.cohesion_ranges)?.[side];
 const inputs = initialStateFields.map(f=>`<label class="field"><span>${f.key==='team_cohesion'&&range?`Team cohesion (${range[0]}–${range[1]})`:f.label}</span><input data-initial-state="${f.key}" type="number" min="${f.min}" max="${f.max}" step="1" value="${values[f.key] ?? f.value}"></label>`).join('');
 const card = `<section class="team-bulk-controls" aria-label="Start state experiment"><div><h3>Start state (experimental) · current: ${state.initial_state === 'natural' ? 'Saved match’s original state (only changed values are written)' : custom ? 'Custom' : 'Controlled start'}</h3><p class="tiny muted">By default every match starts with full condition, full match sharpness, no fatigue, morale 20, team cohesion 80 (or the nearest the team can take) and club cohesion 100, so that tactics can be compared. Applying the values below switches this scenario to a custom start: the values are written into the native input and read back; players and fields you leave unset keep the controlled values. Custom-start experiments are labelled separately and never resumed together with controlled ones.</p></div><div class="team-bulk-actions">${inputs}<button id="initial-state-team" class="button">Apply to whole team</button><button id="initial-state-player" class="button ghost">Apply to current player only</button><button id="initial-state-reset" class="button ghost" ${custom ? '' : 'disabled'}>Restore controlled start (both teams)</button></div></section>`;
 return initialStatePlayersPrevious().replace('<div class="player-summary">', card + '<div class="player-summary">');
};

function readInitialState(){
 const result = {};
 for(const f of initialStateFields){
  const v = Number($(`[data-initial-state="${f.key}"]`).value);
  const range = f.key==='team_cohesion' ? (state.match_base?.cohesion_ranges || catalog.cohesion_ranges)?.[side] : null;
  const lo = range ? range[0] : f.min, hi = range ? range[1] : f.max;
  if(!Number.isFinite(v) || v < lo || v > hi){toast(`${f.label}  must be between ${lo}–${hi} `);return null;}
  initialStateValues[side][f.key] = v;
  result[f.key] = Math.round(v * f.scale);
 }
 result.sharpness_secondary = result.sharpness;
 return result;
}
function applyInitialState(onlyCurrent){
 const values = readInitialState();if(!values)return;
 const t = team(), roster = onlyCurrent ? [t.players[player]] : (typeof teamBulkRoster === 'function' ? teamBulkRoster(t) : t.players);
 for(const p of roster){p.native_profile ??= {};Object.assign(p.native_profile, values);}
 if(!onlyCurrent && t.squad && typeof syncMatchFromSquad === 'function')syncMatchFromSquad(t);
 if(state.initial_state !== 'natural')state.initial_state = 'custom';   // saved matches stay natural: changed fields only
 save();render();toast(`${t.name}: set for ${roster.length}  players ${state.initial_state === 'natural' ? '' : ' (custom start)'}`);
}
function resetInitialState(){
 if(state.initial_state === 'natural'){   // saved match: back to the stored values
  state.teams.forEach((t,s)=>t.players.forEach((p,i)=>{p.native_profile = clone(defaults.teams[s].players[i].native_profile);}));
  save();render();toast('Restored the player states stored in the saved match');return;
 }
 const keys = [...initialStateFields.map(f=>f.key), 'sharpness_secondary'];
 for(const t of state.teams)for(const list of [t.players, t.squad || []])for(const p of list)if(p.native_profile)for(const k of keys)delete p.native_profile[k];
 delete state.initial_state;
 save();render();toast('Restored the controlled start');
}

const initialStateBindPrevious = bind;
bind = function(){
 initialStateBindPrevious();if(view !== 'players')return;
 $('#initial-state-team').onclick = ()=>applyInitialState(false);
 $('#initial-state-player').onclick = ()=>applyInitialState(true);
 $('#initial-state-reset').onclick = resetInitialState;
};
