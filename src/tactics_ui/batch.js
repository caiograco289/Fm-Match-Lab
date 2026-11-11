'use strict';
const formatDuration=s=>s==null?'Estimating':s<60?`${Math.round(s)}  s`:`${Math.floor(s/60)}  min ${Math.round(s%60)}  s`;
const batchResultsView=resultsView,batchBind=bind;
resultsView=function(){
 const html=batchResultsView(),j=selectedJob;if(!j?.batch_schema)return html;
 const resumable=['cancelled','error','interrupted'].includes(j.status)&&j.completed<j.total;
 return `<div class="card batch-status"><div class="card-head"><div><h3>Batch run · ${j.workers}  workers · ${j.event_details===false?'Fast mode':'Full mode'}</h3><div class="subtitle">Completed ${j.completed} / ${j.total}  matches · failed ${j.failures?.length||0}  matches · ${j.matches_per_minute||0}  matches/min</div></div><div>${resumable?'<button id="batch-resume" class="button primary">Continue unfinished matches</button>':''} <button id="batch-csv" class="button">Export per-match CSV</button></div></div><div class="card-body tiny">Total time ${formatDuration(j.elapsed_seconds)} · ${j.status==='complete'?'All done':`Remaining ${formatDuration(j.eta_seconds)}`} · ${isComparison(j)?'Each seed runs the reference tactic and this tactic separately':'Single tactic, runs only this tactic'}; ${j.event_details===false?'Only native final score and team statistics kept; scorers, assists and cards were not collected or checked.':''}${j.runtime_mode==='reused_native_worker'?'Full matches reuse the native host; failures keep their evidence and are not rerun automatically.':j.experiment_type==='setpiece_episode'?'Set-piece episodes use a separate host.':'This record uses a host per match.'}${j.active?.length?'<br>Running: '+j.active.map(a=>`${esc(variantLabel(a.variant,j))} / Seed ${a.seed}${a.attempt>1?' / retry':''}`).join('; '):''}</div></div>${html}`;
};
bind=function(){
 batchBind();
 if($('#batch-resume'))$('#batch-resume').onclick=async()=>{try{const response=await api('/api/resume',{id:selectedJob.id,workers:Number($('#workers').value)});activeJob=response.id;await poll()}catch(e){toast(e.message)}};
 if($('#batch-csv'))$('#batch-csv').onclick=()=>{
  const header=['Mode','Scenario','Seed','Home goals','Away goals','Seconds','Attempts','Log'],rows=selectedJob.runs.map(r=>[selectedJob.event_details===false?'Fast (score/statistics only)':'Full',variantLabel(r.variant),r.seed,...r.result.score,r.elapsed_seconds??'',r.attempts??1,r.log]);
  const csv='\ufeff'+[header,...rows].map(row=>row.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\r\n');
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download=`FM27-${selectedJob.id}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 };
};
api('/api/status').then(status=>{const limits=status.batch,element=$('#workers');element.innerHTML=Array.from({length:limits.maximum},(_,i)=>`<option value="${i+1}" ${i+1===limits.recommended?'selected':''}>${i+1}  workers</option>`).join('');element.title=`Suggested from this machine’s processor and memory: ${limits.recommended}  workers, at most ${limits.maximum}  workers`;}).catch(e=>toast(e.message));

const quickModeLabel=document.createElement('label');quickModeLabel.className='compare-toggle';
quickModeLabel.title='Full matches collect only the score and team statistics; scorers, assists and cards are not collected or checked. Set-piece episodes still use full mode. Affects new jobs only.';
quickModeLabel.innerHTML='<input id="quick-score-mode" type="checkbox">Fast mode (score/statistics only)';
$('#run').before(quickModeLabel);
const apiBeforeQuickMode=api;
api=async function(url,data){
 if(url==='/api/run'&&data)data={...data,event_details:!$('#quick-score-mode').checked};
 return apiBeforeQuickMode(url,data);
};
window.addEventListener('DOMContentLoaded',()=>{
 const detailedEventsView=eventsView;
 eventsView=function(run){return run?.events?.disabled?'<p class="tiny muted">Fast mode: scorers, assists and cards were not collected for this match; score and team statistics were checked.</p>':detailedEventsView(run);};
});
