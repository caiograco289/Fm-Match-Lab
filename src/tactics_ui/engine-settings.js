'use strict';
// Keep diagnostics outside the rerendered tactic workspace. No storage access.
function showEngineStatus(status){
 const e=status.engine_compatibility||status;
 document.querySelector('#engine-summary').textContent=e.can_simulate?(e.compatible?'Local engine: key interfaces check passed':'Local engine: not verified yet, trial runs allowed'):'Local engine: needs setup; tactic editing works normally';
 document.querySelector('#engine-message').textContent=e.message||'';
 document.querySelector('#engine-path').value=e.selected_game_root||'';
 document.querySelector('#engine-diagnostics').textContent=JSON.stringify({reason:e.reason,diagnostics:e.diagnostics,diagnostic_error:e.diagnostic_error,missing_files:e.missing_files},null,2);
 document.querySelector('#engine-details').open=!e.compatible;
 // the panel stays hidden while the engine is fine; the status line in the side rail opens it
 document.body.classList.toggle('show-engine',!e.compatible);
 const rail=document.querySelector('.rail-bottom');
 if(rail)rail.innerHTML=`<i class="status-dot" style="background:${e.compatible?'#99c881':'#e0a040'}"></i>${e.compatible?'Engine ready':'Engine: check needed'}<small>${e.compatible?'FM27 build verified · details':'Click for details'}</small>`;
}
document.head.insertAdjacentHTML('beforeend','<style>#engine-settings{display:none}body.show-engine #engine-settings{display:block}.rail-bottom{cursor:pointer}</style>');
document.addEventListener('click',e=>{if(e.target.closest('.rail-bottom')){document.body.classList.toggle('show-engine');window.scrollTo(0,0);}});
window.addEventListener('DOMContentLoaded',async()=>{
 try{showEngineStatus(await api('/api/status'));}catch(e){document.querySelector('#engine-summary').textContent='Could not read engine diagnostics: '+e.message;}
 document.querySelector('#engine-check').onclick=async()=>{
  const button=document.querySelector('#engine-check');button.disabled=true;
  try{showEngineStatus(await api('/api/engine/select',{path:document.querySelector('#engine-path').value}));}
  catch(e){document.querySelector('#engine-message').textContent=e.message;}
  finally{button.disabled=false;}
 };
});
