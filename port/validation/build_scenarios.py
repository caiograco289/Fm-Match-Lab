"""Build harvestgreen22-style Phase 6 scenarios from the Mac preset export, using the app's own plan/validation code."""
import json,sys,copy,collections
sys.path.insert(0,'build/source')
import fm27_tactics_server as app
S=sys.argv[1]
rows=[json.loads(l) for l in open(S+'/presets.jsonl')]
T=[r for r in rows if r['event']=='installed_tactic_preset']
names={p['mask']:p['id'] for p in app.POSITIONS.values()}
def shape(phase):
    v=[names.get(c['position'],'?') for c in phase]
    d=sum(p in {'DR','DCR','DCL','DC','DL'} for p in v);wb=sum(p.startswith('WB') for p in v);dm=sum(p.startswith('DM') for p in v)
    m=sum(p in {'ML','MR'} or p.startswith('MC') for p in v);am=sum(p.startswith('AM') for p in v);st=sum(p.startswith('ST') for p in v)
    return ''.join(str(n) for n in [d,wb,dm,m,am,st] if n)
for r in T: r['name']=bytes.fromhex(r['name_utf8_hex']).decode(); r['shape']=shape(r['phases'][0])+'-'+shape(r['phases'][1])
if len(sys.argv)>2 and sys.argv[2]=='list':
    for r in T: print(r['index'],r['name'],r['shape'],[names.get(c['position']) for c in r['phases'][0]])
    sys.exit()
if sys.argv[2]=='oop':
    for i in map(int,sys.argv[3].split(',')):
        r=T[i];print(i,r['name'],r['shape'],'IP',[names.get(c['position']) for c in r['phases'][0]],'OOP',[names.get(c['position']) for c in r['phases'][1]])
    sys.exit()
# --- build: python build.py S build
defaults=app.validate_scenario(json.load(open(S+'/defaults.json'))) if 'teams' in json.load(open(S+'/defaults.json')) else None
base=json.load(open(S+'/defaults.json'));base=base.get('scenario',base)
ace=next(json.loads(l) for l in open(S+'/ace.jsonl') if '"native_tactic_file_parsed"' in l)
plans={'wingplay':(T[43],'Wing Play 424-442'),'gegenpress':(T[16],'Gegenpress 433-433'),'tikitaka':(T[22],'Tiki-Taka 4231-442'),'aceofclubs':(ace,'ZaZ - Ace of Clubs 0.1 ST')}
def setup(team,level,pace_acc,feet=100):
    for p in team['players']:
        for i in range(15,69): p['attributes'][i]=level*5
        p['attributes'][39]=p['attributes'][40]=feet
        if pace_acc: p['attributes'][49]=p['attributes'][53]=pace_acc*5
        p['native_profile'].update(height_cm=180,weight_kg=70)
feet=int(sys.argv[3]) if len(sys.argv)>3 else 100
for home in ['wingplay','aceofclubs','tikitaka']:
    s=copy.deepcopy(base)
    for side,key in [(0,home),(1,'gegenpress')]:
        team=s['teams'][side];app.desktop_tactic_plan.apply(app, team, plans[key][0]);team['tactic_name']=plans[key][1]
    setup(s['teams'][0],12,None,feet);setup(s['teams'][1],13,12,feet)
    s=app.validate_scenario(s)
    json.dump(s,open(f'{S}/p6_{home}_feet{feet}.json','w'))
    print(home,'ok',s['teams'][0]['tactic_name'],'vs',s['teams'][1]['tactic_name'])
