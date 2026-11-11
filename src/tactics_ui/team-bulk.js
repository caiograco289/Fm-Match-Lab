'use strict';
const teamBulkValues = [15, 15], teamBulkUndo = [null, null];
const teamBulkPositions = [7, 7], teamBulkPositionValues = [15, 15];
const teamBulkPersonality = ['professionalism','loyalty','sportsmanship','temperament','pressure','ambition','adaptability'];
const teamBulkPositionOptions = () => catalog.attributes.filter(a=>a.position&&a.name!=='UnusedSweeper');

const teamBulkPlayersPrevious = playersView;
playersView = function(){
 if(teamBulkUndo[side] && teamBulkUndo[side].owner!==team())teamBulkUndo[side]=null;
 const controls = `<section class="team-bulk-controls" aria-label="Bulk edit the whole squad"><div><h3>${esc(team().name)} · Bulk edit the whole squad</h3><p class="tiny muted">Covers the goalkeeper, outfield players and all substitutes. All attributes include technical, mental, physical, goalkeeping and hidden personality attributes; position familiarity is set separately per selected position.</p></div><div class="team-bulk-actions"><label class="field"><span>All attributes, displayed value (1–20)</span><input id="team-all-attributes-value" type="number" min="1" max="20" step="0.2" value="${teamBulkValues[side]}" aria-label="Target value for all attributes of this team"></label><button id="team-all-attributes" class="button">Set all attributes of everyone to this value</button></div><div class="team-bulk-actions"><label class="field"><span>Position whose familiarity to change</span>${select(teamBulkPositionOptions().map(a=>({id:a.id,label:a.label+' · '+a.name})),teamBulkPositions[side],'id="team-position" aria-label="Target position for everyone’s familiarity"')}</label><label class="field"><span>Position familiarity (whole number 0–20)</span><input id="team-position-value" type="number" min="0" max="20" step="1" value="${teamBulkPositionValues[side]}" aria-label="Target familiarity for every player at this position"></label><button id="team-position-apply" class="button">Set this position’s familiarity for everyone</button><button id="team-bulk-undo" class="button ghost" ${teamBulkUndo[side]?'':'disabled'}>Undo this team’s last bulk edit</button></div><p class="tiny muted">Changes only the chosen position; other position familiarities are kept. Edits the simulation input directly and does not adjust CA. Non-integer displayed values are rounded at internal precision; hidden personality attributes are whole numbers 1–20.</p></section>`;
 return teamBulkPlayersPrevious().replace('<div class="player-summary">', controls+'<div class="player-summary">');
};

function teamBulkRoster(t){if(t.squad&&typeof syncSquadFromMatch==='function')syncSquadFromMatch(t);return t.squad||t.players;}
function applyTeamBulk(kind, value, position){
 if(kind!=='attributes' && kind!=='position')throw Error('Unknown bulk-edit operation');
 if(kind==='attributes' && (!Number.isFinite(value)||value<1||value>20)){
  toast('Displayed attribute values must be between 1 and 20');return false;
 }
 const selected=teamBulkPositionOptions().find(a=>a.id===position);
 if(kind==='position'&&(!selected||!Number.isInteger(value)||value<0||value>20)){
  toast('Choose a valid position and enter a whole-number familiarity from 0 to 20');return false;
 }
 const ids=kind==='position'?[selected.id]:catalog.attributes.filter(a=>!a.position).map(a=>a.id);
 const t=team(),roster=teamBulkRoster(t);
 teamBulkUndo[side]={owner:t,kind,ids,players:roster.map(p=>({native_id:p.source_uid??p.native_id,attributes:ids.map(id=>p.attributes[id]),personality:kind==='attributes'?Object.fromEntries(teamBulkPersonality.map(k=>[k,{present:Object.hasOwn(p.native_profile||{},k),value:p.native_profile?.[k]}])):null}))};
 for(const p of roster){
  for(const id of ids)p.attributes[id]=kind==='position'?value:Math.round(value*5);
  if(kind==='attributes'){
   p.native_profile??={};
   for(const key of teamBulkPersonality)p.native_profile[key]=Math.round(value);
  }
 }
 if(kind==='attributes')teamBulkValues[side]=value;
 else{teamBulkPositions[side]=position;teamBulkPositionValues[side]=value;}
 if(t.squad)syncMatchFromSquad(t);
 save();render();toast(`${t.name}: set ${roster.length}  players ${kind==='position'?selected.label+' familiarity set to '+value:'Set all attributes to '+value}`);
 return true;
}

function undoTeamBulk(){
 const before=teamBulkUndo[side],t=team();if(!before)return;const roster=teamBulkRoster(t);
 if(before.owner!==t||roster.length!==before.players.length||roster.some((p,i)=>(p.source_uid??p.native_id)!==before.players[i].native_id)){
  teamBulkUndo[side]=null;render();toast('The squad has changed; the undo record of the last bulk edit cannot be applied');return;
 }
 roster.forEach((p,i)=>{
  const old=before.players[i];before.ids.forEach((id,j)=>p.attributes[id]=old.attributes[j]);
  if(old.personality)for(const [key,entry]of Object.entries(old.personality)){
   if(entry.present)p.native_profile[key]=entry.value;else delete p.native_profile[key];
  }
 });
 teamBulkUndo[side]=null;if(t.squad)syncMatchFromSquad(t);save();render();toast('Undid this team’s last bulk edit');
}

const teamBulkBindPrevious=bind;
bind=function(){
 teamBulkBindPrevious();if(view!=='players')return;
 $('#team-all-attributes').onclick=()=>applyTeamBulk('attributes',Number($('#team-all-attributes-value').value));
 $('#team-position').onchange=e=>teamBulkPositions[side]=Number(e.target.value);
 $('#team-position-apply').onclick=()=>applyTeamBulk('position',$('#team-position-value').value.trim()===''?NaN:Number($('#team-position-value').value),Number($('#team-position').value));
 $('#team-bulk-undo').onclick=undoTeamBulk;
};
