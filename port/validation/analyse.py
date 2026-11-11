import json,sys,math
S=sys.argv[1];PAT=sys.argv[2] if len(sys.argv)>2 else 'p6_{k}_feet100_job.json';ref={'wingplay':0.453,'aceofclubs':0.510,'tikitaka':0.235}
print('| Home (vs Gegenpress 433-433) | n | W-D-L | Mac win % | Windows win % | diff | 95% band of Windows figure | Result | Goals H-A | xG H-A | Possession H |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for k,name in [('wingplay','Wing Play 424-442'),('aceofclubs','ZaZ Ace of Clubs'),('tikitaka','Tiki-Taka 4231-442')]:
    try:j=json.load(open(S+'/'+PAT.format(k=k)))
    except OSError:continue
    runs=[r for r in j['runs'] if r.get('result')];n=len(runs)
    w=sum(r['result']['score'][0]>r['result']['score'][1] for r in runs);d=sum(r['result']['score'][0]==r['result']['score'][1] for r in runs);l=n-w-d
    p=ref[k];half=1.96*math.sqrt(p*(1-p)/n);rate=w/n
    avg=lambda f:sum(f(r) for r in runs)/n
    gh=avg(lambda r:r['result']['score'][0]);ga=avg(lambda r:r['result']['score'][1])
    xh=avg(lambda r:r['statistics']['teams'][0]['xg']);xa=avg(lambda r:r['statistics']['teams'][1]['xg'])
    ph=avg(lambda r:r['statistics']['teams'][0]['possession'])
    ok='PASS' if abs(rate-p)<=half else ('BORDERLINE' if abs(rate-p)<=half*1.25 else 'FAIL')
    print(f'| {name} | {n} | {w}-{d}-{l} | {rate*100:.1f} | {p*100:.1f} | {(rate-p)*100:+.1f} | ±{half*100:.1f} | {ok} | {gh:.2f}-{ga:.2f} | {xh:.2f}-{xa:.2f} | {ph*100:.1f}% |')
    print(f'<!-- {k}: failures {len(j["failures"])}, status {j["status"]} -->')
