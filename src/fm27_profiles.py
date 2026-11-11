"""Bounded extra player inputs, independently checked against native recordings."""
import copy
# ID, minimum, maximum. No user-supplied addresses or arbitrary memory writes.
FIELDS={
 'height_cm':(0,140,220),'age':(1,14,60),
 'professionalism':(2,1,20),'loyalty':(3,1,20),'sportsmanship':(4,1,20),
 'temperament':(5,1,20),'pressure':(6,1,20),'ambition':(7,1,20),'adaptability':(8,1,20),
 'traits_low':(9,0,0xffffffff),'traits_high':(10,0,0xffffffff),
 'current_ability':(11,0,200),'home_reputation':(12,0,10000),'current_reputation':(13,0,10000),'world_reputation':(14,0,10000),
 'condition':(15,0,10000),'sharpness':(16,0,10000),'sharpness_secondary':(17,0,10000),
 'fatigue_raw':(18,0,65535),'weight_kg':(19,40,140),
 'team_cohesion':(20,0,100),'club_cohesion':(21,0,100),'morale':(22,1,20),
}
def normalize(data):
 if not isinstance(data,dict)or set(data)-set(FIELDS):raise ValueError('Unknown player extra input')
 result={}
 for key,value in data.items():
  _,lo,hi=FIELDS[key]
  if type(value)is not int or not lo<=value<=hi:raise ValueError('Player extra input out of range: '+key)
  result[key]=value
 return result

# Controlled initial state, applied to both complete rosters before preparation.
CONTROLLED_START={"condition":10000,"sharpness":10000,"sharpness_secondary":10000,"fatigue_raw":0,"team_cohesion":80,"club_cohesion":100,"morale":20}

# Opt-in experiment (scenario "initial_state": "custom"): keep the per-player values the user set for these fields;
# any field left unset still gets its controlled value. The default stays the controlled start above.
STATE_FIELDS=tuple(CONTROLLED_START)
def start_state(profile,custom):
 result=dict(profile)
 for key,value in CONTROLLED_START.items():
  if not custom or key not in result:result[key]=value
 return result
def natural(values):
 """A saved match's own player values (host --dump-input profile list, indexed by field id), bounded and rounded."""
 result={}
 for key,(field,lo,hi) in FIELDS.items():
  result[key]=min(hi,max(lo,int(round(values[field]))))
 return result
def policy(*scenarios):
 if any(s is not None and s.get('initial_state')=='natural' for s in scenarios):
  return {'id':'natural-saved-v1','player_values':None,'note':'saved match: every player keeps the values stored in the match file; only edited fields are written'}
 if any(s is not None and s.get('initial_state')=='custom' for s in scenarios):
  return {'id':'custom-start-v1','player_values':None,'defaults':copy.deepcopy(CONTROLLED_START),'fields':list(STATE_FIELDS),
          'note':'experimental: per-player condition, sharpness, fatigue, morale and cohesion as set in the scenario'}
 return {'id':'controlled-start-v3','player_values':copy.deepcopy(CONTROLLED_START),'morale_verified':True,'cohesion_verified':True}
def cohesion_range(adjustment):
 """Team cohesion values the host can express for a team (input = 2v - 50 - 5*adjustment, as the native host)."""
 ok=[v for v in range(101) if 0<=2*v-50-5*adjustment<=100 and abs(v-50-5*adjustment)<=25]
 return (ok[0],ok[-1]) if ok else None
