import json,sys,time,urllib.request
B='http://127.0.0.1:18765'
def api(p,d=None):
    r=urllib.request.Request(B+p,data=None if d is None else json.dumps(d).encode(),headers={'Content-Type':'application/json'})
    try:return json.loads(urllib.request.urlopen(r,timeout=120).read())
    except urllib.error.HTTPError as e:print('HTTP',e.code,e.read().decode()[:800]);sys.exit(1)
s=json.load(open(sys.argv[1]));n=int(sys.argv[2]);w=int(sys.argv[3]) if len(sys.argv)>3 else 2
j=api('/api/run',{'scenario':s,'seeds':list(range(1,n+1)),'workers':w,'event_details':True,'name':sys.argv[4] if len(sys.argv)>4 else None})
key=j.get('id') or j.get('job',{}).get('id');print('job',key);t=time.time()
while True:
    time.sleep(5);job=api(f'/api/jobs/{key}')
    if job['status'] not in('queued','running'):break
print(job['status'],job['completed'],'/',job['total'],'failures',len(job['failures']),f'{time.time()-t:.0f}s')
print(json.dumps(job['failures'][:3],ensure_ascii=False)[:1500])
print(json.dumps(job.get("metrics"),ensure_ascii=False)[:2500]);json.dump(job,open(sys.argv[1].replace(".json","_job.json"),"w"))
