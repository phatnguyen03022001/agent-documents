#!/usr/bin/env python3
"""Deterministic, standard-library-only V1 documentation validator."""
import json,re,sys
from pathlib import Path

V=1
TOP='model_version milestone coverage actors roles features acceptance systems data interfaces flows dependencies capabilities decisions unknowns'.split()
COL={
'actors':'ACT','roles':'ROL','features':'FTR','acceptance':'ACC','systems':'SYS','data':'DAT','interfaces':'IFC','flows':'FLW','dependencies':'EXT','capabilities':'CAP','decisions':'DEC','unknowns':'UNK'}
DEP={'NONE':-1,'L0':0,'L1':1,'L2':2}
DOC={'PRODUCT','BEHAVIOR','ARCHITECTURE','DATA','INTERFACES','QUALITY','DELIVERY','DECISIONS'}
DREF=re.compile(r'^docs/(PRODUCT|BEHAVIOR|ARCHITECTURE|DATA|INTERFACES|QUALITY|DELIVERY|DECISIONS)\.md#([^#\s]+)$')
PAT={p:re.compile(r'^'+p+r'-[0-9]{3,}$') for p in COL.values()}

def ne(x): return isinstance(x,str) and bool(x.strip())
def refs(x): return set(x.get('refs',[])) if isinstance(x,dict) and set(x)=={'refs'} else set()

class P:
 def __init__(s): s.f=[];s.b=[]
 def m(s,x): s.f.append(('MODEL_ERROR',x))
 def r(s,x,block=False): (s.b if block else s.f).append(('REFERENCE_ERROR',x))
 def x(s,c,x): s.b.append((c,x))

def exact(o,keys,p,l):
 if not isinstance(o,dict): p.m(f'{l} must be an object');return False
 a=set(o);k=set(keys)
 if a!=k: p.m(f"{l} has invalid fields (missing={','.join(sorted(k-a))}; extra={','.join(sorted(a-k))})");return False
 return True

def sl(x,p,l,n=0):
 if not isinstance(x,list): p.m(f'{l} must be an array');return False
 if len(x)<n: p.m(f'{l} must contain at least {n} item(s)');return False
 ok=True
 for i,v in enumerate(x):
  if not ne(v): p.m(f'{l}[{i}] must be a non-empty string');ok=False
 return ok

def rel(x,p,l):
 if not isinstance(x,dict) or set(x) not in ({'refs'},{'na'}): p.m(f'{l} must contain exactly one of refs or na');return False
 if 'refs' in x:return sl(x['refs'],p,l+'.refs',1)
 if not ne(x['na']):p.m(f'{l}.na must be a non-empty rationale');return False
 return True

def en(v,vals,p,l):
 if v not in vals:p.m(f'{l} is invalid')

def recs(c,p):
 # actors, roles, acceptance, systems, data, interfaces, flows, dependencies, decisions
 specs={
 'actors':({'id','name','kind','doc_ref'},{'kind':{'HUMAN','SYSTEM','EXTERNAL'}}),
 'roles':({'id','name','actor_refs','doc_ref'},{}),
 'acceptance':({'id','doc_ref'},{}),
 'systems':({'id','name','doc_ref','decision_refs'},{}),
 'data':({'id','name','kind','owner_system_ref','doc_ref'},{'kind':{'PERSISTENT','MATERIAL_EPHEMERAL'}}),
 'interfaces':({'id','name','kind','owner_system_ref','peer_refs','doc_ref'},{'kind':{'API','EVENT','JOB','COMMAND','PROTOCOL','FILE','PUBLIC_LIBRARY'}}),
 'flows':({'id','name','kind','critical','doc_ref','system_refs','interface_refs','data_refs','dependency_refs'},{'kind':{'USER','SYSTEM','FAILURE'}}),
 'dependencies':({'id','name','kind','critical','doc_ref'},{'kind':{'SERVICE','API','VENDOR','LIBRARY','PLATFORM','DATA_SOURCE'}}),
 'decisions':({'id','kind','subject','outcome','reversibility','doc_ref'},{'kind':{'TECHNOLOGY','ARCHITECTURE','BUILD_BUY','DATA','INTERFACE','DELIVERY','OTHER'},'reversibility':{'REVERSIBLE','COSTLY','IRREVERSIBLE'}})}
 for n,(ks,es) in specs.items():
  for i,r in enumerate(c[n]):
   l=f'{n}[{i}]'
   if not exact(r,ks,p,l):continue
   for k in ('name','subject','outcome'):
    if k in r and not ne(r[k]):p.m(f'{l}.{k} must be non-empty')
   for k,v in es.items():en(r[k],v,p,l+'.'+k)
   if n=='roles':sl(r['actor_refs'],p,l+'.actor_refs')
   if n=='systems':sl(r['decision_refs'],p,l+'.decision_refs')
   if n=='interfaces':sl(r['peer_refs'],p,l+'.peer_refs')
   if n=='flows':
    if not isinstance(r['critical'],bool):p.m(l+'.critical must be boolean')
    for k in ('system_refs','interface_refs','data_refs','dependency_refs'):sl(r[k],p,l+'.'+k)
   if n=='dependencies' and not isinstance(r['critical'],bool):p.m(l+'.critical must be boolean')
 # features
 for i,r in enumerate(c['features']):
  l=f'features[{i}]';ks={'id','name','actor_refs','spec_ref','acceptance_refs','relations','decision_refs'}
  if not exact(r,ks,p,l):continue
  if not ne(r['name']):p.m(l+'.name must be non-empty')
  sl(r['actor_refs'],p,l+'.actor_refs',1);sl(r['acceptance_refs'],p,l+'.acceptance_refs',1);sl(r['decision_refs'],p,l+'.decision_refs')
  if not ne(r['spec_ref']):p.m(l+'.spec_ref must be non-empty')
  if exact(r['relations'],{'roles','flows','data','interfaces','dependencies','capabilities'},p,l+'.relations'):
   for k in r['relations']:rel(r['relations'][k],p,l+'.relations.'+k)
 # capabilities
 for i,r in enumerate(c['capabilities']):
  l=f'capabilities[{i}]'
  if not isinstance(r,dict):p.m(l+' must be object');continue
  st=r.get('status');d=r.get('disposition')
  if st=='OPEN':
   ks={'id','name','status','disposition','system_refs','dependency_refs','blocking_unknown_ref'}
   if exact(r,ks,p,l):
    if d is not None:p.m(l+'.disposition must be null when OPEN')
  elif st=='RESOLVED' and d=='DEFER':
   exact(r,{'id','name','status','disposition','system_refs','dependency_refs','defer_ref'},p,l)
  elif st=='RESOLVED' and d in {'BUILD','BUY','HYBRID'}:
   ks={'id','name','status','disposition','system_refs','dependency_refs','decision_ref','boundary_ref','exit'}
   if exact(r,ks,p,l):
    e=r['exit']
    if not isinstance(e,dict) or set(e) not in ({'ref'},{'na'}) or not ne(next(iter(e.values()),'')):p.m(l+'.exit must contain exactly one non-empty ref or na')
  else:p.m(l+'.status/disposition is invalid')
  if isinstance(r,dict):
   if 'name'in r and not ne(r['name']):p.m(l+'.name must be non-empty')
   for k in ('system_refs','dependency_refs'):
    if k in r:sl(r[k],p,l+'.'+k)
 # unknowns
 K={'QUESTION','DECISION_REQUIRED','ASSUMPTION','AUTHORITY_CONFLICT','CONTRADICTION'};PH={'DESIGN','IMPLEMENTATION','VERIFICATION','POST_MILESTONE'}
 for i,r in enumerate(c['unknowns']):
  l=f'unknowns[{i}]';base={'id','kind','question','affected_refs','affected_coverage','blocking','reason','resolution_phase','status'}
  if not isinstance(r,dict):p.m(l+' must be object');continue
  ks=base|({'resolved_by_ref'} if r.get('status')=='RESOLVED' else set())
  if not exact(r,ks,p,l):continue
  en(r['kind'],K,p,l+'.kind');en(r['resolution_phase'],PH,p,l+'.resolution_phase');en(r['status'],{'OPEN','RESOLVED'},p,l+'.status')
  if not ne(r['question']) or not ne(r['reason']):p.m(l+' question/reason must be non-empty')
  sl(r['affected_refs'],p,l+'.affected_refs');sl(r['affected_coverage'],p,l+'.affected_coverage')
  if not isinstance(r['blocking'],bool):p.m(l+'.blocking must be boolean')
  if r['status']=='OPEN' and r['kind'] in {'AUTHORITY_CONFLICT','CONTRADICTION'} and r['blocking'] is not True:p.m(l+' open conflict/contradiction must be blocking')
  if r['status']=='OPEN' and r['blocking'] is True and r['resolution_phase']!='DESIGN':p.m(l+' open blocking unknown must resolve in DESIGN')

def structure(c,t,p):
 if not isinstance(c,dict):p.m('catalog root must be an object');return
 if set(c)!=set(TOP):p.m('top-level catalog fields are invalid')
 if c.get('model_version')!=V:p.m(f"unsupported model_version: {c.get('model_version')!r}")
 m=c.get('milestone')
 if exact(m,{'id','name','scope_state','scope_ref'},p,'milestone'):
  if not ne(m['id']) or not ne(m['name']) or not ne(m['scope_ref']):p.m('milestone string fields must be non-empty')
  en(m['scope_state'],{'OPEN','FROZEN'},p,'milestone.scope_state')
 cov=c.get('coverage'); exp=set(t)
 if not isinstance(cov,dict):p.m('coverage must be an object')
 else:
  if set(cov)!=exp:p.m('coverage taxonomy set mismatch')
  for k,e in cov.items():
   if k not in exp:continue
   l='coverage.'+k
   if not isinstance(e,dict):p.m(l+' must be an object');continue
   if e.get('applicability')=='NA':
    if exact(e,{'applicability','rationale'},p,l) and not ne(e['rationale']):p.m(l+' N/A requires a non-empty rationale')
   elif e.get('applicability')=='APPLICABLE':
    if exact(e,{'applicability','required_depth','actual_depth','evidence_refs','rationale'},p,l):
     en(e['required_depth'],{'L0','L1','L2'},p,l+'.required_depth');en(e['actual_depth'],set(DEP),p,l+'.actual_depth');sl(e['evidence_refs'],p,l+'.evidence_refs')
     if not isinstance(e['rationale'],str):p.m(l+'.rationale must be a string')
     if e['required_depth'] in {'L0','L2'} and not ne(e['rationale']):p.m(l+' requires non-empty rationale')
   else:p.m(l+'.applicability must be APPLICABLE or NA')
 for n in COL:
  if not isinstance(c.get(n),list):p.m(n+' must be an array')
 if p.f:return
 recs(c,p)
 seen={}
 for n,pfx in COL.items():
  for i,r in enumerate(c[n]):
   if not isinstance(r,dict):continue
   rid=r.get('id');l=f'{n}[{i}].id'
   if not isinstance(rid,str) or not PAT[pfx].fullmatch(rid):p.m(f'{l} does not match {pfx} identity class');continue
   if rid in seen:p.m(f'duplicate global id {rid}')
   seen[rid]=pfx

def doc(target,x,want,p,l,block=False):
 m=DREF.fullmatch(x) if isinstance(x,str) else None
 if not m:p.r(f'{l} has invalid document path',block);return
 dn,tok=m.groups()
 if want and dn!=want:p.r(f'{l} must reference docs/{want}.md',block);return
 path=target/'docs'/(dn+'.md')
 try:text=path.read_text(encoding='utf-8')
 except OSError as e:p.r(f'{l} cannot read {path}: {e}',True);return
 if not re.search(r'^#{1,6}\s+'+re.escape(tok)+r'(?:\s|$)',text,re.M):p.r(f'{l} missing heading token {tok}',True)

def ref(x,want,ids,p,l):
 if x not in ids:p.r(f'{l} references unknown id {x!r}');return
 if want and ids[x] not in set(want):p.r(f'{l} expects {want} but found {ids[x]}')

def references(c,target,p):
 ids={r['id']:COL[n] for n in COL for r in c[n]}; cc=set(c['coverage'])
 doc(target,c['milestone']['scope_ref'],'PRODUCT',p,'milestone.scope_ref',True)
 for k,e in c['coverage'].items():
  if e['applicability']=='APPLICABLE':
   for j,x in enumerate(e['evidence_refs']):doc(target,x,None,p,f'coverage.{k}.evidence_refs[{j}]',True)
 for r in c['actors']:doc(target,r['doc_ref'],'PRODUCT',p,r['id']+'.doc_ref')
 for r in c['roles']:
  doc(target,r['doc_ref'],'PRODUCT',p,r['id']+'.doc_ref');[ref(x,{'ACT'},ids,p,r['id']+'.actor_refs') for x in r['actor_refs']]
 for r in c['features']:
  doc(target,r['spec_ref'],'BEHAVIOR',p,r['id']+'.spec_ref');[ref(x,{'ACT'},ids,p,r['id']+'.actor_refs') for x in r['actor_refs']];[ref(x,{'ACC'},ids,p,r['id']+'.acceptance_refs') for x in r['acceptance_refs']];[ref(x,{'DEC'},ids,p,r['id']+'.decision_refs') for x in r['decision_refs']]
  for k,w in [('roles',{'ROL'}),('flows',{'FLW'}),('data',{'DAT'}),('interfaces',{'IFC'}),('dependencies',{'EXT'}),('capabilities',{'CAP'})]:[ref(x,w,ids,p,r['id']+'.relations.'+k) for x in refs(r['relations'][k])]
 for r in c['acceptance']:doc(target,r['doc_ref'],'BEHAVIOR',p,r['id']+'.doc_ref')
 for r in c['systems']:
  doc(target,r['doc_ref'],'ARCHITECTURE',p,r['id']+'.doc_ref');[ref(x,{'DEC'},ids,p,r['id']+'.decision_refs') for x in r['decision_refs']]
 for r in c['data']:ref(r['owner_system_ref'],{'SYS'},ids,p,r['id']+'.owner_system_ref');doc(target,r['doc_ref'],'DATA',p,r['id']+'.doc_ref')
 for r in c['interfaces']:
  ref(r['owner_system_ref'],{'SYS'},ids,p,r['id']+'.owner_system_ref');[ref(x,{'ACT','SYS','EXT'},ids,p,r['id']+'.peer_refs') for x in r['peer_refs']];doc(target,r['doc_ref'],'INTERFACES',p,r['id']+'.doc_ref')
 for r in c['flows']:
  doc(target,r['doc_ref'],'BEHAVIOR',p,r['id']+'.doc_ref')
  for k,w in [('system_refs',{'SYS'}),('interface_refs',{'IFC'}),('data_refs',{'DAT'}),('dependency_refs',{'EXT'})]:[ref(x,w,ids,p,r['id']+'.'+k) for x in r[k]]
 for r in c['dependencies']:doc(target,r['doc_ref'],'INTERFACES',p,r['id']+'.doc_ref')
 for r in c['capabilities']:
  [ref(x,{'SYS'},ids,p,r['id']+'.system_refs') for x in r['system_refs']];[ref(x,{'EXT'},ids,p,r['id']+'.dependency_refs') for x in r['dependency_refs']]
  if r['status']=='OPEN':ref(r['blocking_unknown_ref'],{'UNK'},ids,p,r['id']+'.blocking_unknown_ref')
  elif r['disposition']=='DEFER':doc(target,r['defer_ref'],'ARCHITECTURE',p,r['id']+'.defer_ref')
  else:
   ref(r['decision_ref'],{'DEC'},ids,p,r['id']+'.decision_ref');doc(target,r['boundary_ref'],'ARCHITECTURE',p,r['id']+'.boundary_ref')
   if 'ref' in r['exit']:doc(target,r['exit']['ref'],'ARCHITECTURE',p,r['id']+'.exit.ref')
 for r in c['decisions']:doc(target,r['doc_ref'],'DECISIONS',p,r['id']+'.doc_ref')
 for r in c['unknowns']:
  for x in r['affected_refs']:ref(x,None,ids,p,r['id']+'.affected_refs')
  for x in r['affected_coverage']:
   if x not in cc:p.r(f"{r['id']}.affected_coverage references unknown concern {x!r}")
  if r['status']=='RESOLVED':
   ref(r['resolved_by_ref'],None,ids,p,r['id']+'.resolved_by_ref')
   if r['kind']=='DECISION_REQUIRED' and ids.get(r['resolved_by_ref'])!='DEC':p.r(r['id']+' DECISION_REQUIRED resolution must point to DEC')

def closure(c,p):
 if c['milestone']['scope_state']!='FROZEN':p.x('SCOPE_OPEN','milestone scope_state must be FROZEN')
 for k,e in c['coverage'].items():
  if e['applicability']=='APPLICABLE':
   if e['actual_depth']=='NONE':p.x('COVERAGE_GAP',k+' is applicable but actual_depth is NONE')
   elif DEP[e['actual_depth']]<DEP[e['required_depth']]:p.x('COVERAGE_GAP',k+' actual depth below required depth')
 na=lambda k:c['coverage'][k]['applicability']=='NA'
 pairs=[(c['actors']or c['roles'],'product.actors_roles'),(c['features'],'product.features_capabilities'),(c['features'],'behavior.functional'),(c['features']or c['acceptance'],'behavior.acceptance'),(c['systems'],'architecture.components_ownership'),(c['data'],'data.entities_ownership'),(c['interfaces'],'interfaces.contracts'),([x for x in c['flows'] if x['critical']],'behavior.critical_flows'),(c['dependencies'],'interfaces.external_dependencies'),(c['capabilities'],'architecture.build_buy'),(c['decisions'],'decisions.material_choices'),(c['unknowns'],'unknowns.open_questions')]
 for a,k in pairs:
  if a and na(k):p.x('TRACEABILITY_GAP',k+' is N/A but matching inventory exists')
 fm={x['id']:x for x in c['flows']}
 for f in c['features']:
  for x in refs(f['relations']['flows']):
   q=fm.get(x)
   if not q:continue
   for field,rn in [('interface_refs','interfaces'),('data_refs','data'),('dependency_refs','dependencies')]:
    miss=set(q[field])-refs(f['relations'][rn])
    if miss:p.x('TRACEABILITY_GAP',f"{f['id']} relation {rn} omits {sorted(miss)} used by {x}")
 um={u['id']:u for u in c['unknowns']}; fc=set().union(*(refs(f['relations']['capabilities']) for f in c['features'])) if c['features'] else set()
 for x in c['capabilities']:
  if x['status']=='OPEN':
   u=um.get(x['blocking_unknown_ref'])
   if not u or u['status']!='OPEN' or u['blocking'] is not True:p.x('BUILD_BUY_GAP',x['id']+' OPEN capability lacks a matching open blocking unknown')
  else:
   d=x['disposition']
   if d=='BUY' and not x['dependency_refs']:p.x('BUILD_BUY_GAP',x['id']+' BUY requires at least one EXT dependency')
   if d=='BUILD' and not x['system_refs']:p.x('BUILD_BUY_GAP',x['id']+' BUILD requires at least one SYS system')
   if d=='HYBRID' and (not x['system_refs'] or not x['dependency_refs']):p.x('BUILD_BUY_GAP',x['id']+' HYBRID requires both SYS and EXT references')
   if d=='DEFER' and x['id'] in fc:p.x('BUILD_BUY_GAP',x['id']+' DEFER capability is referenced by an in-scope feature')
 for u in c['unknowns']:
  if u['status']=='OPEN' and u['blocking']:
   cat='AUTHORITY_CONFLICT' if u['kind']=='AUTHORITY_CONFLICT' else 'RESOLUTION_GAP' if u['kind']=='CONTRADICTION' else 'BLOCKING_UNKNOWN';p.x(cat,u['id']+' is unresolved')
 orphan(c,p)

def orphan(c,p):
 used={x:set() for x in COL.values()}
 for x in c['roles']:used['ACT'].update(x['actor_refs'])
 for f in c['features']:
  used['ACT'].update(f['actor_refs']);used['ACC'].update(f['acceptance_refs']);used['DEC'].update(f['decision_refs'])
  for k,pfx in [('roles','ROL'),('flows','FLW'),('data','DAT'),('interfaces','IFC'),('dependencies','EXT'),('capabilities','CAP')]:used[pfx].update(refs(f['relations'][k]))
 for x in c['systems']:used['DEC'].update(x['decision_refs'])
 for x in c['data']:used['SYS'].add(x['owner_system_ref'])
 for x in c['interfaces']:
  used['SYS'].add(x['owner_system_ref']);[used.get(y.split('-')[0],set()).add(y) for y in x['peer_refs']]
 for x in c['flows']:
  for k,pfx in [('system_refs','SYS'),('interface_refs','IFC'),('data_refs','DAT'),('dependency_refs','EXT')]:used[pfx].update(x[k])
 for x in c['capabilities']:
  used['SYS'].update(x['system_refs']);used['EXT'].update(x['dependency_refs'])
  if x['status']=='OPEN':used['UNK'].add(x['blocking_unknown_ref'])
  elif x['disposition']!='DEFER':used['DEC'].add(x['decision_ref'])
 for x in c['unknowns']:
  for y in x['affected_refs']:used.get(y.split('-')[0],set()).add(y)
  if x['status']=='RESOLVED':y=x['resolved_by_ref'];used.get(y.split('-')[0],set()).add(y)
 for n,pfx in COL.items():
  if pfx in {'FTR','UNK'}:continue
  for x in c[n]:
   if pfx=='CAP' and x.get('disposition')=='DEFER':continue
   if x['id'] not in used[pfx]:p.x('ORPHAN',x['id']+' is an orphan active '+n+' record')

def emit(p):
 print('DOCS_READY = '+('FALSE' if p.f or p.b else 'TRUE'))
 for c,x in p.f+p.b:print(f'[{c}] {x}')
 return 2 if p.f else 1 if p.b else 0

def main(a=None):
 a=sys.argv[1:] if a is None else a;p=P()
 if len(a)!=1:p.m('usage: validate.py <target-repository-root>');return emit(p)
 target=Path(a[0]).resolve()
 try:c=json.loads((target/'docs/catalog/project.json').read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError) as e:p.m('cannot load catalog: '+str(e));return emit(p)
 try:t=json.loads((Path(__file__).resolve().parents[1]/'model/coverage.v1.json').read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError) as e:p.m('validator taxonomy cannot be loaded: '+str(e));return emit(p)
 if not isinstance(t,dict) or t.get('model_version')!=V or not isinstance(t.get('concerns'),dict):p.m('validator taxonomy is malformed or unsupported');return emit(p)
 structure(c,t['concerns'],p)
 if p.f:return emit(p)
 references(c,target,p)
 if p.f:return emit(p)
 closure(c,p);return emit(p)
if __name__=='__main__':raise SystemExit(main())
