'use strict';
// Experiment naming, rename/delete, and the tactical-effectiveness experiment panel.
const experimentLabel=document.createElement('label');experimentLabel.innerHTML='Experiment name<input id="experiment-name" maxlength="100" placeholder="Leave empty to name automatically">';
$('#seed').closest('label').before(experimentLabel);
const executionOptions=document.createElement('details');
executionOptions.className='card experiment-panel';
executionOptions.innerHTML=`
 <summary>Tactical effectiveness experiment</summary>
 <p class="tiny muted">When enabled, every match runs the newer engine branch on its own. The values are artificial experimental conditions.</p>
 <div class="experiment-controls">
  <label><input id="execution-enabled" type="checkbox">Enable</label>
  <label>Own team<input id="execution-own" type="number" min="0" max="100" step="1" value="70" disabled></label>
  <label>Opponent<input id="execution-opponent" type="number" min="0" max="100" step="1" value="70" disabled></label>
 </div>`;
$('#engine-settings').after(executionOptions);
$('#execution-enabled').onchange=()=>{
 for(const id of ['execution-own','execution-opponent'])$('#'+id).disabled=!$('#execution-enabled').checked;
};
const experimentApiPrevious=api;
api=async function(url,data){
 if(url==='/api/run'&&data){
  data={...data,name:$('#experiment-name').value.trim()||undefined};
  delete data.scenario.experimental_execution;
  if(data.reference)delete data.reference.experimental_execution;
  if($('#execution-enabled').checked){
   const values=['execution-own','execution-opponent'].map(id=>{
    const input=$('#'+id);
    if(input.value===''||!input.checkValidity())throw Error('Tactical effectiveness must be a whole number from 0 to 100');
    return Number(input.value);
   });
   data.scenario={...data.scenario,experimental_execution:values};
   if(data.reference)data.reference={...data.reference,experimental_execution:values};
  }
  }
 return experimentApiPrevious(url,data);
};
const experimentResultsPrevious=resultsView;
resultsView=function(){
 let html=experimentResultsPrevious();if(!selectedJob)return html;
 const j=selectedJob;
 if(j.experimental_execution){
  const row=j.runs[j.detailIndex??Math.max(0,j.runs.length-1)];
  const variant=row?.variant??Object.keys(j.experimental_execution)[0];
  const values=j.experimental_execution[variant];
  if(values)html=`<p class="card experiment-panel">Tactical effectiveness experiment · ${esc(j.team_names[variant][0])} ${values[0]} / ${esc(j.team_names[variant][1])} ${values[1]}${row?.experimental_execution?' · native sampling verified':''}</p>`+html;
 }
 const busy=['queued','running'].includes(j.status);
 return `<div class="card experiment-heading"><h2>${esc(j.name||'Experiment '+j.id)}</h2><button class="button small" id="rename-experiment">Rename</button><button class="button small" id="delete-experiment" ${busy?'disabled title="Wait until the experiment finishes, or cancel it, before deleting"':''}>Delete experiment</button><label>Find experiment<input id="find-experiment" placeholder="Search by name"></label></div>${html}`;
};
async function deleteExperiment(button){
 const {id,name}=selectedJob;
 if(!confirm(`Permanently delete “${name||'Experiment '+id}” and its local results and logs?`))return;
 button.disabled=true;
 try{
  await api('/api/jobs/delete',{id});
 }catch(e){
  button.disabled=false;
  toast(e.message);
  return;
 }
 history=history.filter(job=>job.id!==id);
 if(polledJob?.id===id)polledJob=null;
 if(selectedJob?.id===id){
  selectedJob=null;
  const next=history[0];
  if(next){
   try{
    const job=await api('/api/jobs/'+next.id);
    if(!selectedJob)selectedJob=job;
   }catch(e){toast(e.message)}
  }
 }
 render();
 toast('Experiment deleted');
}
const experimentBindPrevious=bind;
bind=function(){experimentBindPrevious();
 if($('#lineup-player'))[...$('#lineup-player').options].forEach(o=>o.disabled=Number(o.value)>=team().roster_size);
 if($('#sp-strategy')&&view==='setpieces'){const select=$('#sp-strategy'),value=spCurrent().strategy;if(![...select.options].some(o=>+o.value===value)){select.add(new Option('Game’s stored strategy (code  '+value+')',value));select.value=value;}}
 $$('[data-job]').forEach(b=>{const h=history.find(h=>h.id===b.dataset.job);if(h){b.textContent=(h.name||'Experiment '+h.id)+' · '+h.completed+'/'+h.total;b.title=new Date(h.created*1000).toLocaleString();}});
 if($('#rename-experiment'))$('#rename-experiment').onclick=async()=>{const name=prompt('Experiment name (1–100 characters)',selectedJob.name||'');if(name===null)return;try{const r=await api('/api/jobs/rename',{id:selectedJob.id,name});selectedJob.name=r.name;const h=history.find(h=>h.id===r.id);if(h)h.name=r.name;if(polledJob?.id===r.id)polledJob.name=r.name;render();}catch(e){toast(e.message)}};
 if($('#delete-experiment'))$('#delete-experiment').onclick=e=>deleteExperiment(e.currentTarget);
 if($('#find-experiment'))$('#find-experiment').oninput=e=>$$('[data-job]').forEach(b=>b.hidden=!b.textContent.toLowerCase().includes(e.target.value.toLowerCase()));
};
