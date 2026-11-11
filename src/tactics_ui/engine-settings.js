'use strict';
// Keep diagnostics outside the rerendered tactic workspace. No storage access.
function showEngineStatus(status){
 const e=status.engine_compatibility||status;
 document.querySelector('#engine-summary').textContent=e.can_simulate?(e.compatible?'Local engine: key interfaces check passed':'Local engine: not verified yet, trial runs allowed'):'Local engine: needs setup; tactic editing works normally';
 document.querySelector('#engine-message').textContent=e.message||'';
 document.querySelector('#engine-path').value=e.selected_game_root||'';
 document.querySelector('#engine-diagnostics').textContent=JSON.stringify({reason:e.reason,diagnostics:e.diagnostics,diagnostic_error:e.diagnostic_error,missing_files:e.missing_files},null,2);
 document.querySelector('#engine-details').open=!e.compatible;
}
window.addEventListener('DOMContentLoaded',async()=>{
 try{showEngineStatus(await api('/api/status'));}catch(e){document.querySelector('#engine-summary').textContent='Could not read engine diagnostics: '+e.message;}
 document.querySelector('#engine-check').onclick=async()=>{
  const button=document.querySelector('#engine-check');button.disabled=true;
  try{showEngineStatus(await api('/api/engine/select',{path:document.querySelector('#engine-path').value}));}
  catch(e){document.querySelector('#engine-message').textContent=e.message;}
  finally{button.disabled=false;}
 };
});
