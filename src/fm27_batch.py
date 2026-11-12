"""Bounded, cancellable native process pool. Every match retains process isolation."""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import desktop_platform
import json
import os
from pathlib import Path
import subprocess
import threading
import time
from fm27_simulator import inspect_log
import fm27_match_events

def worker_limits():
    # Reserve 1 GiB for the desktop/editor; a macOS engine host uses about 60 MB (measured), so 0.25 GiB per worker is
    # generous. One core is left free for the app and the rest of the Mac.
    available=max(1,int((desktop_platform.memory_available_gib()-1)/0.25))
    maximum=max(1,min(max(1,(os.cpu_count()or 2)-1),available))
    return {'maximum':maximum,'recommended':max(1,min(6,maximum))}

def own_child_processes():
    """Hosts are children of the service and exit with it (each polls its cancellation file)."""
    return None

class BatchCancelled(Exception):pass

class MatchCancellation:
    """A per-match cancellation file: only this host's session is asked to exit."""
    def __init__(self):
        self.file=desktop_platform.FileCancellation();self.name=self.file.name;self.handle=None
    def signal(self):return self.file.signal()
    def close(self):return self.file.close()

class BatchRunner:
    def __init__(self,root,workers=1,retries=1,timeout=190):
        self.root=Path(root);self.workers=workers;self.retries=retries;self.timeout=timeout
        self.stop=threading.Event();self.lock=threading.Lock();self.processes={};self.active={};self.cancellations={}
        self.cleanup_timeout=15
    def cancel(self):
        self.stop.set()
        with self.lock:
            for cancellation in self.cancellations.values():cancellation.signal()
    def communicate(self,process,cancellation,path):
        deadline=time.monotonic()+self.timeout;grace=None;reason=None
        while True:
            now=time.monotonic()
            if reason is None and (self.stop.is_set()or now>=deadline):
                reason='cancelled'if self.stop.is_set()else'timeout'
                cancellation.signal();grace=now+self.cleanup_timeout
            if grace is not None and now>=grace:
                process.kill();stdout,_=process.communicate()
                Path(str(path)+'.lifecycle.json').write_text(json.dumps({'reason':reason,'graceful_cleanup_seconds':self.cleanup_timeout,'forced_termination':True,'steam_cleanup_not_confirmed':True}),encoding='utf8')
                if reason=='cancelled':raise BatchCancelled()
                raise RuntimeError('Native host timed out; clean-up wait timed out and the host was force-stopped;Steam release not confirmed')
            try:stdout,_=process.communicate(timeout=min(.25,max(.01,(grace or deadline)-now)))
            except subprocess.TimeoutExpired:continue
            if reason:Path(str(path)+'.lifecycle.json').write_text(json.dumps({'reason':reason,'forced_termination':False,'exit_code':process.returncode}),encoding='utf8')
            if reason=='cancelled':raise BatchCancelled()
            if reason=='timeout':raise RuntimeError('Native host timed out; normal clean-up requested before exit')
            return stdout
    def command(self,task,path):
        command=[str(self.root/('fm27_native/'+desktop_platform.HOST_NAME)),'--output',str(path),'--tick-step',str(task.get('tick_step',1))]
        if task['seed']is not None:command+=['--seed',str(task['seed'])]
        if task.get('config'):command+=['--scenario-file',str(task['config'])]
        if task.get('fixture'):command+=['--fixture',str(task['fixture'])]
        return command
    def one(self,task):
        began=time.perf_counter();attempts=[]
        for attempt in range(self.retries+1):
            if self.stop.is_set():raise BatchCancelled()
            path=Path(task['path']);path=path if attempt==0 else path.with_name(path.stem+f'.retry{attempt}'+path.suffix)
            process=None;cancellation=None
            try:
                with self.lock:
                    if self.stop.is_set():raise BatchCancelled()
                    environment=os.environ.copy()
                    if task.get('engine_path'):environment['FM27_ENGINE_PATH']=task['engine_path']   # saved matches keep their own version word
                    if task.get('episode'):
                        episode=task['episode'];environment.update(FM27_EPISODE_TYPE=str(episode['type']),FM27_EPISODE_SIDE=str(episode['attacking_side']),FM27_EPISODE_SECONDS=str(episode['window_seconds']))
                    cancellation=MatchCancellation();command=self.command(task,path)
                    if cancellation.name:command+=['--cancel-event',cancellation.name]
                    process=subprocess.Popen(command,cwd=self.root,env=environment,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                    self.processes[task['key']]=process
                    self.cancellations[task['key']]=cancellation
                    self.active[task['key']]={'seed':task['seed'],'variant':task['variant'],'attempt':attempt+1}
                stdout=self.communicate(process,cancellation,path)
                if self.stop.is_set():raise BatchCancelled()
                if process.returncode:raise RuntimeError(f'Native host exited {process.returncode}: {stdout.decode(errors="replace")[-200:]}')
                rows=[json.loads(line)for line in path.read_text(encoding='utf8').splitlines()if line]
                compatibility=next((r for r in rows if r.get('event')=='native_engine_compatibility'),None)
                if not compatibility or not (compatibility.get('compatible')or compatibility.get('trial_allowed')):raise RuntimeError('No valid native key interface check')
                cleanup=next((r for r in rows if r.get('event')=='steam_session_cleanup'),None)
                if not cleanup or not cleanup.get('ok'):raise RuntimeError('This match Steam session release failed the check; this match was not accepted')
                episode=next((r for r in rows if r.get('event')=='native_setpiece_episode_finished'),None)
                if task.get('episode'):
                    if episode is None:raise ValueError('Missing the original set-piece episode end record')
                    run={'result':{'event':'native_setpiece_episode_finished','full_match_completed':False,'score':[0,0],'tick':episode['end_tick'],'clock':episode['clock']},'score_changes':[r for r in rows if r.get('event')=='observed_score_change']}
                else:run=inspect_log(path)
                for event in (('native_scenario_readback_verified','native_player_tactic_bindings_verified','native_opposition_effective_verified')if task.get('config')else()):
                    if not any(r.get('event')==event for r in rows):raise RuntimeError('Missing native check: '+event)
                stats=next((r for r in rows if r.get('event')==('native_episode_statistics'if episode else'native_match_statistics')),None)
                events=fm27_match_events.collect(rows,task['scenario'],task['position_names'])if task.get('scenario')else None
                if episode and events:
                    if events.get('scorers_verified_against_native_totals')is False:raise ValueError('Episode goal attribution failed the game’s full-time count check')
                    for key in ['goals','cancelled_goals','cards']:events[key]=[r for r in events[key]if episode['found']and episode['start_tick']<r['tick']<=episode.get('window_end_tick',episode['end_tick'])]
                if episode and events:
                    run['result']['score']=[sum(g['side']==side for g in events['goals'])for side in range(2)]
                return {'variant':task['variant'],'seed':task['seed'],'result':run['result'],'episode':episode,'statistics':stats,'events':events,'score_changes':run['score_changes'],'log':path.name,'verified':True,'engine_compatibility':compatibility,'engine_dll_sha256':os.environ.get('FM27_EXPECTED_DLL_SHA256'),'elapsed_seconds':round(time.perf_counter()-began,3),'attempts':attempt+1,'retry_errors':attempts,'timings':next((r for r in rows if r.get('event')=='native_timings'),None)}
            except BatchCancelled:raise
            except Exception as error:
                attempts.append(str(error))
                if attempt==self.retries or (process is not None and process.returncode==180):
                    phase='simulation'
                    try:
                        inspect_log(path);phase='host_exit_after_match'
                    except (ValueError,OSError):pass
                    return {'variant':task['variant'],'seed':task['seed'],'failed':True,'failure_phase':phase,'errors':attempts,'attempts':attempt+1,'log':path.name}
            finally:
                with self.lock:
                    self.processes.pop(task['key'],None);self.active.pop(task['key'],None);self.cancellations.pop(task['key'],None)
                    if cancellation:cancellation.close()
                if process is not None:
                    if process.stdout:process.stdout.close()
                    handle=getattr(process,'_handle',None)
                    if handle is not None and hasattr(handle,'Close'):handle.Close()
    def run(self,tasks,on_result,on_progress=lambda active:None):
        tasks=iter(tasks);pending={};exhausted=False
        with ThreadPoolExecutor(max_workers=self.workers,thread_name_prefix='fm27-match')as pool:
            try:
                while pending or not exhausted:
                    while not exhausted and not self.stop.is_set()and len(pending)<self.workers:
                        task=next(tasks,None)
                        if task is None:exhausted=True;break
                        pending[pool.submit(self.one,task)]=task
                    if self.stop.is_set():break
                    if not pending:break
                    done,_=wait(pending,timeout=.25,return_when=FIRST_COMPLETED)
                    for future in done:
                        task=pending.pop(future)
                        try:result=future.result()
                        except BatchCancelled:continue
                        if not self.stop.is_set():on_result(result)
                    with self.lock:active=list(self.active.values())
                    on_progress(active)
            except BaseException:
                self.cancel();raise
            finally:
                if self.stop.is_set():
                    self.cancel()
                    for future in pending:future.cancel()
