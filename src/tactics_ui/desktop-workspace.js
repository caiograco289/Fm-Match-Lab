'use strict';
let matchImportSide=0,matchImportBusy=false;
const workspaceToolbarPrevious=toolbar;
toolbar=function(){
 const base=workspaceToolbarPrevious()+(state.initial_state==='natural'?'<p class="tiny muted controlled-state-note">Both squads start as stored in the saved match (condition, sharpness, morale, cohesion); these change normally during the match.</p>':'<p class="tiny muted controlled-state-note">Both full squads start at 100% condition / sharpness · fatigue 0 · morale 20/20 · team cohesion 80 (or the nearest the team can take) · club cohesion 100; these change normally during the match.</p>');if(!['tactics','setpieces'].includes(view))return base;
 const setpiece=view==='setpieces',label=setpiece?spDefinition().label:'Match tactic';
 const sides=editableTeamSides(),singleTeam=sides.length===1;
 const cards=sides.map(s=>{
  const t=state.teams[s],teamLabel=singleTeam?'Own team':s?'Away':'Home';
  const edit=singleTeam?'':`<button class="button small" data-edit-team="${s}">${s===side?'Editing':'Edit this team'}</button>`;
  const name=setpiece?t.setpieces.routines[spType].map(r=>r.name).join(' / '):t.tactic_name||(state.initial_state==='natural'?'Tactic from the saved match':'Default / manual setup');
  const actions=setpiece?'<p class="tiny muted">Edit this team’s set pieces below.</p>':`<div class="team-load-actions"><button class="button" data-match-import="${s}">Import ${teamLabel} match tactic FMF</button><button class="button small" data-match-export="${s}">Export ${teamLabel} match tactic FMF</button></div><p class="tiny muted">A loaded match tactic can still be edited; set pieces are imported separately on the set-pieces page.</p>`;
  return `<section class="team-load-card ${s===side?'editing':''}" data-loaded-team="${s}"><div class="team-load-heading"><span class="tag">${teamLabel}</span><b>${esc(t.name)}</b>${edit}</div><small>${esc(label)}</small><strong class="loaded-tactic-name">${esc(name)}</strong>${actions}</section>`;
 });
 return base+`<div class="team-load-grid${singleTeam?' single-team':''}">${cards.join('')}</div>`;
};
const workspaceBindPrevious=bind;
bind=function(){workspaceBindPrevious();
 $$('[data-edit-team]').forEach(b=>b.onclick=()=>{side=+b.dataset.editTeam;slot=player=0;render();});
 $$('[data-match-import]').forEach(b=>{b.disabled=matchImportBusy;b.onclick=()=>{matchImportSide=+b.dataset.matchImport;$('#match-file').click();};});
 $$('[data-match-export]').forEach(b=>b.onclick=async()=>{const target=+b.dataset.matchExport;try{b.disabled=true;b.textContent='Writing and verifying…';const result=await api('/api/export-fmf',{side:target,scenario:state});downloadBinary(result);toast(`${target?'Away':'Home'} match tactic exported`);}catch(e){toast(e.message);}finally{render();}});
};
$('#match-file').onchange=async e=>{
 const file=e.target.files[0],target=matchImportSide;if(!file)return;
 try{if(!/\.fmf$/i.test(file.name))throw Error('Choose a match tactic FMF file');if(file.size>4*1024*1024)throw Error('FMF file exceeds 4 MB');matchImportBusy=true;render();
 const bytes=new Uint8Array(await file.arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
 const result=await api('/api/import-fmf',{side:target,scenario:state,file_base64:btoa(binary)});state=result.scenario;side=target;save();toast(`${target?'Away':'Home'} match tactic loaded: ${state.teams[target].tactic_name||file.name}`);
 }catch(e){toast('Match tactic import failed: '+e.message);}finally{matchImportBusy=false;e.target.value='';render();}
};
// Document leases survive navigation/reload without leaving a separate service window.
const desktopPage=crypto.randomUUID();
function desktopPresence(action){const body=JSON.stringify({page:desktopPage,action});if(action==='close')navigator.sendBeacon('/api/desktop-presence',new Blob([body],{type:'application/json'}));else fetch('/api/desktop-presence',{method:'POST',headers:{'Content-Type':'application/json'},body,keepalive:true}).catch(()=>{});}
window.addEventListener('pageshow',()=>desktopPresence('open'));
window.addEventListener('pagehide',()=>desktopPresence('close'));
setInterval(()=>desktopPresence('open'),15000);desktopPresence('open');
