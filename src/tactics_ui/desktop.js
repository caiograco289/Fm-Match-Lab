'use strict';
// Desktop-only presentation. The scenario schema and native position masks stay
// the same as the verified editor. Drops snap to engine-supported positions.
const desktopPositionNames={GK:'Goalkeeping',DR:'Right-back',DL:'Left-back',DC:'Centre-back',DCR:'Right centre-back',DCL:'Left centre-back',WBR:'Right wing-back',WBL:'Left wing-back',DMC:'DM',DMR:'Right defensive midfielder',DML:'Left defensive midfielder',MR:'Right midfielder',ML:'Left midfielder',MC:'Central midfielder',MCR:'Right midfielder',MCL:'Left midfielder',AMR:'Right winger',AML:'Left winger',AMC:'Attacking midfielder',AMCR:'Right attacking midfielder',AMCL:'Left attacking midfielder',ST:'Striker',STR:'Right striker',STL:'Left striker'};
function desktopIcon(kind='move'){
 const paths=kind==='shoot'?'<path d="M18 72L77 22M62 22h15v15"/><rect x="58" y="9" width="34" height="20"/>':kind==='width'?'<path d="M12 45h76M12 45l12-9m-12 9l12 9M88 45l-12-9m12 9l-12 9"/>':kind==='defend'?'<path d="M24 16h52v32c0 18-26 32-26 32S24 66 24 48Z"/><path d="M33 48h34M50 32v32"/>':'<path d="M21 72L50 20l29 52M50 20l-9 8m9-8l9 8M50 50v29"/><circle cx="21" cy="72" r="5"/><circle cx="79" cy="72" r="5"/>';
 return `<svg viewBox="0 0 100 90" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">${paths}</svg>`;
}
function desktopTile(g,value,attribute){
 const text=(g.name||'')+' '+(g.label||'');const kind=/Width|Width/.test(text)?'width':/Shoot|Shots|Shots/.test(text)?'shoot':/Press|Tack|Mark|Defen|Pressing|Marking|Tackling/.test(text)?'defend':'move';
 return `<label class="instruction-tile"><span class="tile-title">${esc(g.label||g.name)}</span><span class="tile-drawing">${desktopIcon(kind)}</span>${select(g.options,value,`${attribute} aria-label="${esc(g.label||g.name)}"`)}</label>`;
}
teamInstructions=function(){
 const groups=catalog.team_instructions.filter(g=>g.possession_phase===phase);
 const categories=phase?[[4,'Defensive organisation and transition'],[5,'Defending crosses'],[7,'Stop goalkeeper distribution'],[10,'Pressing direction']]:[[0,'Overall attack'],[1,'Build-up'],[2,'Support'],[3,'Final third'],[8,'Support runs'],[9,'Dribbling'],[11,'Progression direction'],[12,'Goalkeeper distribution']];
 return categories.map(([id,title])=>{const list=groups.filter(g=>g.phase===id);return list.length?`<div class="section-label">${title}</div><div class="instruction-grid fm-card-grid">${list.map(g=>desktopTile(g,team().instructions[g.id],`data-ti="${g.id}"`)).join('')}</div>`:''}).join('');
};
function desktopBoard(p){
 const ps=positions(),rs=roles();return `<section class="phase-board ${p===phase?'active-phase':''}" data-board="${p}"><button class="board-title" data-phase="${p}"><span class="phase-dot"></span>${p?'Out of possession':'In possession'}<small>${p===phase?'Editing':'Click to switch'}</small></button><div class="pitch desktop-pitch" data-pitch="${p}" aria-label="${p?'Out of possession':'In possession'} Tactics board"><div class="pitch-lines"><div class="halfway"></div><div class="centre-circle"></div><div class="box top"></div><div class="box bottom"></div><div class="six-yard top"></div><div class="six-yard bottom"></div></div>${catalog.positions.map(pos=>`<span class="drop-position" data-position="${pos.id}" style="left:${pos.x}%;top:${pos.y}%">${pos.id}</span>`).join('')}${team().phases[p].map((c,i)=>{const pos=ps[c.position],name=team().players[team().lineup[i]].name;return `<button class="pitch-slot ${p===phase&&i===slot?'selected':''}" data-board-slot="${i}" data-board-phase="${p}" style="left:${pos.x}%;top:${pos.y}%" aria-label="${p?'Out of possession':'In possession'} ${name} ${c.position}; drag or use the arrow keys to move" title="${esc(name+' · '+(rs[c.role]?.label||c.role))}"><span class="shirt">${i+1}</span><span class="slot-name">${esc(name)}</span><span class="slot-role">${esc(c.position)}</span></button>`}).join('')}</div></section>`;
}
tacticsView=function(){
 const t=team(),c=current();return `${toolbar()}<div class="editor-grid desktop-editor"><section class="card formation-card"><div class="card-head"><div><h2>Two-phase tactics board</h2><div class="subtitle">Drag the shirts to move players · in and out of possession set separately</div></div><span class="tag">Attacking direction ↑</span></div><div class="preset-row">${select([{id:'',label:`${phase?'Out of possession':'In possession'} phase: choose formation…`},...Object.keys(PRESETS).map(id=>({id,label:id}))],'','id="formation"')}<button id="auto-lineup" class="button small">Pick by position</button></div><div class="dual-boards">${desktopBoard(0)}${desktopBoard(1)}</div><p class="drag-help">Drops snap to positions the game supports; dropping on an occupied position swaps the players, and roles and instructions stay with the position. Both phases share one starting XI.</p><div class="compact-lineup">${t.lineup.map((p,i)=>`<button class="${i===slot?'active':''}" data-slot="${i}"><b>${i+1}</b><span>${esc(t.players[p].name)}</span><small>${esc(t.phases[phase][i].position)}</small></button>`).join('')}</div></section><section class="instruction-panel"><div class="phase-editor-heading">${phaseControls()}<span>${phase?'Out of possession':'In possession'} setup</span></div><div class="segmented editor-tabs"><button data-editor="team" class="${teamTab==='team'?'active':''}">Team instructions</button><button data-editor="personal" class="${teamTab==='personal'?'active':''}">Roles & player instructions</button></div><div class="card" ${teamTab==='team'?'':'hidden'}><div class="card-head"><div><input id="team-name" class="team-title" value="${esc(t.name)}" aria-label="Team name"><div class="subtitle">${phase?'Out of possession':'In possession'} phase team instructions</div></div></div><div class="card-body">${field('Mentality (whole team)',select(catalog.mentalities,t.mentality,'id="mentality"'))}${teamInstructions()}</div></div><div class="card inspector" ${teamTab==='personal'?'':'hidden'}><div class="card-head"><div><h2>${esc(t.players[t.lineup[slot]].name)}</h2><div class="subtitle">${phase?'Out of possession':'In possession'} · ${esc(desktopPositionNames[c.position])}</div></div><button id="edit-player" class="button small">Player attributes ↗</button></div><div class="card-body"><div class="inspector-top">${field('starter',select(t.players.map((p,i)=>({id:i,label:p.name})),t.lineup[slot],'id="lineup-player"'))}${field('Position',select(catalog.positions.map(p=>({id:p.id,label:`${desktopPositionNames[p.id]} · ${p.id}`})),c.position,'id="slot-position"'))}${field('Role',select(catalog.roles.filter(r=>r.phase===phase),c.role,'id="slot-role"'))}</div><div class="group-heading"><h3>Player instructions</h3><span class="tiny muted"></span></div><div class="instruction-grid fm-card-grid">${catalog.player_instructions.map(g=>desktopTile(g,c.instructions[g.id],`data-pi="${g.id}"`)).join('')}</div><div id="mark-target">${markTarget()}</div><p class="instructions-note"></p></div></div></section></div>`;
};
function desktopMove(p,i,target){
 const cells=team().phases[p],cell=cells[i];if(!positions()[target])return false;
 if((i===0)!==(target==='GK')){toast('Goalkeeper and outfield positions are set separately');render();return false;}
 if(cell.position!==target){
  const other=cells.findIndex(c=>c.position===target);
  if(other>=0){
   [cells[i],cells[other]]=[cells[other],cells[i]];
  }else{
   const moved=clone(cells);
   moved[i].position=target;
   moved.forEach((c,j)=>harmonizeCell(c,p,j,side,moved));
   const adjusted=moved.filter((c,j)=>c.role!==cells[j].role||c.duty!==cells[j].duty||
    Object.keys(c.instructions).some(key=>c.instructions[key]!==cells[j].instructions[key]));
   if(adjusted.length){
    const names=adjusted.map(c=>desktopPositionNames[c.position]).join(', ');
    if(!confirm(`After the move, ${names} have roles or player instructions that don’t fit the new formation. Continue and adjust them?`)){
     render();return false;
    }
   }
   team().phases[p]=moved;
  }
  save();
 }
 phase=p;slot=i;render();return true;
}
function desktopBindDrag(){
 $$('[data-board-slot]').forEach(button=>{
  const p=+button.dataset.boardPhase,i=+button.dataset.boardSlot,pitch=button.closest('.pitch');let drag=null,suppress=false;
  button.onclick=()=>{if(suppress){suppress=false;return;}phase=p;slot=i;teamTab='personal';render();};
  button.onpointerdown=e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY,target:team().phases[p][i].position,moved:false};button.setPointerCapture(e.pointerId);};
  button.onpointermove=e=>{
   if(!drag)return;if(Math.hypot(e.clientX-drag.x,e.clientY-drag.y)<5&&!drag.moved)return;
   drag.moved=true;pitch.classList.add('dragging');button.classList.add('being-dragged');const r=pitch.getBoundingClientRect(),x=Math.max(0,Math.min(100,(e.clientX-r.left)/r.width*100)),y=Math.max(0,Math.min(100,(e.clientY-r.top)/r.height*100));
   button.style.left=x+'%';button.style.top=y+'%';const possible=catalog.positions.filter(pos=>(i===0)===(pos.id==='GK'));
   const nearest=possible.reduce((a,b)=>Math.hypot(a.x-x,(a.y-y)*r.height/r.width)<=Math.hypot(b.x-x,(b.y-y)*r.height/r.width)?a:b);drag.target=nearest.id;
   pitch.querySelectorAll('.drop-position').forEach(dot=>dot.classList.toggle('drop-target',dot.dataset.position===nearest.id));
  };
  button.onpointerup=e=>{if(!drag)return;const ended=drag;drag=null;if(button.hasPointerCapture(e.pointerId))button.releasePointerCapture(e.pointerId);if(ended.moved){suppress=true;desktopMove(p,i,ended.target);}};
  button.onpointercancel=()=>{drag=null;render();};
  button.onkeydown=e=>{if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();if(i===0)return;const a=positions()[team().phases[p][i].position],dx=e.key==='ArrowLeft'?-1:e.key==='ArrowRight'?1:0,dy=e.key==='ArrowUp'?-1:e.key==='ArrowDown'?1:0;const candidates=catalog.positions.filter(b=>b.id!=='GK'&&(dx?(b.x-a.x)*dx>1:Math.abs(b.x-a.x)<3&&(b.y-a.y)*dy>1));if(candidates.length){candidates.sort((a1,b)=>Math.hypot(a1.x-a.x,a1.y-a.y)-Math.hypot(b.x-a.x,b.y-a.y));desktopMove(p,i,candidates[0].id);$(`[data-board-phase="${p}"][data-board-slot="${i}"]`)?.focus();}};
 });
}
const desktopBindPrevious=bind;bind=function(){desktopBindPrevious();if(view!=='tactics')return;desktopBindDrag();$('#slot-position').onchange=e=>desktopMove(phase,slot,e.target.value);$$('.instruction-tile').forEach(tile=>{const select=tile.querySelector('select');tile.classList.toggle('tile-locked',!!select?.disabled);if(select?.disabled)tile.setAttribute('aria-label',tile.querySelector('.tile-title').textContent+', role locked');});};
document.title='FM27 Match Lab';
fetch('/api/status').then(r=>r.json()).then(s=>{const m=/^fm27-([0-9.]+)/.exec(s.engine_compatibility?.profile||'');if(m)$('#desktop-version').textContent='FM27 '+m[1];}).catch(()=>{});
function desktopIsKeeper(index,s=side){const t=state.teams[s],slotIndex=t.lineup.indexOf(index);if(slotIndex>=0)return t.phases[0][slotIndex].position==='GK';const a=t.players[index].attributes;return a[0]>=10&&a[0]>=Math.max(...a.slice(2,15));}
function desktopAttributeVisible(id,keeper){if(id<15)return keeper?id===0:id!==0;if(GK.has(id))return keeper;if(keeper&&TECH.has(id)&&![22,37,38].includes(id))return false;if(keeper&&id===21)return false;return true;}
const desktopPlayersPrevious=playersView;playersView=function(){return desktopPlayersPrevious().replace('All 69','All relevant attributes');};
function desktopPlayerControls(){
 if(view!=='players')return;const keeper=desktopIsKeeper(player);
 $$('[data-attr]').forEach(input=>{if(!desktopAttributeVisible(+input.dataset.attr,keeper))input.closest('.attribute-row').remove();});
 $$('.attribute-group').forEach(group=>{if(!group.querySelector('.attribute-row'))group.remove();});
 const summary=$('.player-summary .tiny');if(summary)summary.textContent+=keeper?' · Goalkeeper attribute view':' · Outfield attribute view';
 const bulk=$('#bulk-attribute');if(bulk){[...bulk.options].forEach(option=>{if(!desktopAttributeVisible(+option.value,keeper))option.remove();});if(!bulk.value)bulk.selectedIndex=0;}
 if($('#bulk-apply'))$('#bulk-apply').onclick=()=>{
  const id=+bulk.value,value=+$('#bulk-value').value;if(!Number.isFinite(value)||value<1||value>20){toast('Displayed attribute values should be between 1 and 20');return;}
  const scope=$('#bulk-scope').value,targets=scope==='player'?[player]:scope==='starters'?team().lineup:team().players.map((_,i)=>i);let n=0;
  for(const i of targets)if(desktopAttributeVisible(id,desktopIsKeeper(i))){team().players[i].attributes[id]=Math.round(value*5);n++;}save();render();toast(`Changed ${n}  eligible players`);
 };
}
function desktopStatBlock(runs,title){
 const available=runs.filter(r=>r.statistics?.teams?.length===2);if(!available.length)return `<div class="notice">${esc(title)}: old records did not collect possession,xG etc.; matches run with the newer version show these figures.</div>`;
 const definitions=[['possession','Possession',true],['xg','Expected goals xG'],['shots','Shots'],['shots_on_target','Shots on target'],['passes','Passes'],['completed_passes','Completed passes']];
 return `<section class="card match-statistics"><div class="card-head"><h3>${esc(title)} · Per-match statistics</h3><span class="tag">${available.length}  matches with native statistics</span></div><div class="card-body"><div class="stat-sides"><b>${esc(state.teams[0].name)}</b><b>${esc(state.teams[1].name)}</b></div>${definitions.map(([key,label,percent])=>{const values=[0,1].map(s=>available.reduce((n,r)=>n+(r.statistics.teams[s][key]??0),0)/available.length);return `<div class="stat-comparison"><strong>${percent?pct(values[0]):fmt(values[0])}</strong><span>${label}</span><strong>${percent?pct(values[1]):fmt(values[1])}</strong></div>`;}).join('')}<p class="tiny muted"> come from the game’s team statistics object; possession is computed from the game’s possession counts. Averages cover only full matches with collected statistics.</p></div></section>`;
}
const desktopResultsPrevious=resultsView;resultsView=function(){let html=desktopResultsPrevious();const j=selectedJob;if(!j)return html;const blocks=['A','B'].filter(v=>j.runs.some(r=>r.variant===v)).map(v=>desktopStatBlock(j.runs.filter(r=>r.variant===v),variantLabel(v,j))).join('');const failures=(j.failures||[]).length?`<section class="card failure-details"><div class="card-head"><h3>Matches not counted in the results</h3></div><div class="card-body">${j.failures.map(f=>`<p>Seed ${f.seed} · ${esc(variantLabel(f.variant,j))}: ${f.failure_phase==='host_exit_after_match'?'The match finished, but the host exited abnormally; recheck with the same seed':'Host error or check failed'}<br><small>${esc((f.errors||[]).join('; '))}</small></p>`).join('')}</div></section>`:'';html=html.replace('<div class="result-layout">',blocks+failures+'<div class="result-layout">');return html;};
const desktopEventsPrevious=eventsView;eventsView=function(run){return desktopEventsPrevious(run)+(run?.statistics?desktopStatBlock([run],'Seed '+run.seed).replace('Per-match statistics','This match’s statistics'):'');};
const desktopFeatureBindPrevious=bind;bind=function(){desktopFeatureBindPrevious();desktopPlayerControls();if(view==='results'&&$('#batch-csv'))$('#batch-csv').onclick=()=>{
 const header=['Scenario','Seed','Home goals','Away goals','Home possession','Away possession','Home xG','Away xG','Home shots','Away shots','Home shots on target','Away shots on target','Home passes','Away passes','Home completed passes','Away completed passes','Scorer (in/out-of-possession position)','Assist pairs','Cards','Seconds','Log'];const rows=selectedJob.runs.map(r=>{const teams=r.statistics?.teams;return[variantLabel(r.variant),r.seed,...r.result.score,...['possession','xg','shots','shots_on_target','passes','completed_passes'].flatMap(k=>teams?[teams[0][k],teams[1][k]]:['','']),(r.events?.goals||[]).map(g=>(g.own_goal?'OG: ':'')+(g.scorer?g.scorer.name+' ('+g.scorer.ip_position+'/'+g.scorer.oop_position+')':'identity not confirmed')).join('; '),(r.events?.goals||[]).map(g=>(g.scorer?.name||'Unknown')+' ← '+(g.assist?.name||'No assist')).join('; '),(r.events?.cards||[]).map(c=>c.player.name+' '+({yellow:'Yellow card',red:'Red card',second_yellow:'Second yellow'}[c.card])).join('; '),r.elapsed_seconds??'',r.log];});const csv='\ufeff'+[header,...rows].map(row=>row.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download=`FM27-${selectedJob.id}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};};
