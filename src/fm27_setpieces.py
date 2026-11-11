import os
"""Typed set-piece scenarios, backed by original native routines and enum policies."""
import copy,json
from pathlib import Path
ROOT=Path(os.environ["FM27_ENGINE_ROOT"])
import catalog_en
ENUMS=catalog_en.translate_setpieces(json.loads((ROOT/'fm27_research/setpiece_enum_catalog.json').read_text(encoding='utf8')))
SNAP=json.loads((ROOT/'fm27_native/editor_setpieces_default.json').read_text(encoding='utf8'))
TYPE_NAMES=['Defending corners','Defending direct free kicks','Defending wide free kicks','Defending indirect free kicks','Defending throw-ins','Attacking corners','Attacking direct free kicks','Attacking wide free kicks','Attacking indirect free kicks','Attacking throw-ins']
CATALOG={**ENUMS,'types':[{'id':i,'label':name,'strategy_kind':'corner_target'if i==5 else 'free_kick_risk'if i in (6,7,8)else 'defensive_line'if i in (2,3)else None,'swing':i in (5,7)}for i,name in enumerate(TYPE_NAMES)],'frequencies':[{'id':0,'label':'Less often · weight 2'},{'id':1,'label':'Normal · weight 5'},{'id':2,'label':'More often · weight 8'}]}
def defaults(side,snapshot=None):
 # snapshot: a match-input dump team (Windows format); default the bundled fixture's
 t=snapshot if snapshot is not None else SNAP['teams'][side];routines={}
 for variants in t['routine_variants']:
  routines[str(variants[0]['type'])]=[]
  for i,r in enumerate(variants):
   groups=[[]for _ in range(8)]
   for g in r['groups']:groups[g['id']]=list(g['values'])
   backups=[[0]*len(g)for g in groups]
   for g,j,value in r['backups']:backups[g][j]=value
   routines[str(r['type'])].append({'name':f'{TYPE_NAMES[r["type"]]} {i+1}','opaque_flags':r.get('opaque_flags',0)if snapshot is not None else 0,'frequency':r['frequency'],'strategy':r['strategy'],'swing':r['swing'],'groups':groups,'backups':backups,'priority':r['priority']})
 raw=bytes.fromhex(t['manager_tactical_hex']);styles=list(raw[0x16f0-0x2e0:0x16f3-0x2e0])
 return {'routines':routines,'throw_styles':styles,'role_priorities':{str(g):[]for g in range(8)}}
DEFAULTS=[defaults(0),defaults(1)]
def normalize(value,side,roster_size,base=None):
 base_defaults=base if base is not None else DEFAULTS[side]
 def integer(v,lo,hi):
  if type(v)is not int or not lo<=v<=hi:raise ValueError('Invalid set-piece setting value')
  return v
 if not isinstance(value,dict):raise ValueError('Invalid set-piece settings format')
 out=copy.deepcopy(base_defaults);styles=value['throw_styles']
 if len(styles)!=3:raise ValueError('Throw-ins need three strategies: defensive, middle and final third')
 out['throw_styles']=[integer(v,0,1)for v in styles]
 for g in range(8):
  v=value['role_priorities'][str(g)]
  if not isinstance(v,list)or len(v)>roster_size or any(type(i)is not int for i in v)or len(set(v))!=len(v):raise ValueError('Invalid set-piece role player order')
  out['role_priorities'][str(g)]=[integer(i,0,roster_size-1)for i in v]
 for kind in range(10):
  rows=value['routines'][str(kind)];base=base_defaults['routines'][str(kind)][0];result=[]
  if not isinstance(rows,list)or not 1<=len(rows)<=3:raise ValueError('Each set piece keeps 1–3 routines')
  for row in rows:
   r={'name':str(row['name'])[:48],'frequency':integer(row['frequency'],0,2)}
   r['opaque_flags']=integer(row.get('opaque_flags',0),0,255)
   for k in ['strategy','swing']:
    if base[k]==255:
     if row[k]!=255:raise ValueError('This set-piece type does not use this delivery strategy')
     r[k]=255
    elif k=='strategy' and (kind,row[k]) in ((5,3),(7,6),(8,3)):
     r[k]=row[k]
    else:r[k]=integer(row[k],0,1 if k=='swing'else 2)
   priority=row['priority']
   if not isinstance(priority,list)or sorted(priority)!=sorted(base['priority']):raise ValueError('Set-piece assignment order must keep the game’s role categories')
   r['priority']=list(priority)
   if len(row['groups'])!=8 or len(row['backups'])!=8:raise ValueError('Set-piece task groups are incomplete')
   r['groups']=[];r['backups']=[]
   for g in range(8):
    tasks=row['groups'][g];backups=row['backups'][g]
    if not isinstance(tasks,list)or len(tasks)>10 or len(backups)!=len(tasks):raise ValueError('Set-piece tasks and backup tasks do not match')
    if tasks and g not in priority:raise ValueError('This set piece does not use this role category')
    for task in tasks:
     integer(task,0,15)
     if task not in ENUMS['allowed'][str(g)]:raise ValueError('This set-piece role cannot use the chosen task')
    r['groups'].append(list(tasks));r['backups'].append([integer(v,0,15)for v in backups])
   expected=sum(map(len,base['groups']))
   if sum(map(len,r['groups']))!=expected:raise ValueError(f'{TYPE_NAMES[kind]} needs{expected} tasks; remove old tasks before adding new ones')
   result.append(r)
  out['routines'][str(kind)]=result
 return out
def encode(value,side,base=None):
 records=[];base=base if base is not None else DEFAULTS[side]
 for i,v in enumerate(value['throw_styles']):
  if v!=base['throw_styles'][i]:records.append((46,side,i,0,v))
 for g in range(8):
  rows=value['role_priorities'][str(g)]
  if rows!=base['role_priorities'][str(g)]:
   records.append((30,side,12+g,0xffffffff,0));records.extend((30,side,12+g,i,v)for i,v in enumerate(rows))
 for kind in range(10):
  rows=value['routines'][str(kind)]
  if rows==base['routines'][str(kind)]:continue
  records.append((40,side,kind,0,len(rows)))
  for i,row in enumerate(rows):
   slot=kind*16+i
   records.append((41,side,slot,0,row['frequency']))
   records.append((47,side,slot,0,row.get('opaque_flags',0)))
   if row['strategy']!=255:records.append((41,side,slot,1,row['strategy']))
   if row['swing']!=255:records.append((41,side,slot,2,row['swing']))
   records.append((42,side,slot,0,0))
   for g in row['priority']:
    records.extend((43,side,slot,g,v)for v in row['groups'][g])
   records.extend((44,side,slot,j,g)for j,g in enumerate(row['priority']))
   for g,tasks in enumerate(row['groups']):
    records.extend((45,side,slot,g*32+j,row['backups'][g][j])for j in range(len(tasks)))
 return records
