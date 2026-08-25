#!/usr/bin/env python3
"""Deterministic standard-library-only V1 documentation validator."""
import json,re,sys
from collections import deque
from pathlib import Path
V=1
TOP='model_version milestone coverage actors roles features acceptance systems data interfaces flows dependencies capabilities decisions unknowns'.split()
COL={'actors':'ACT','roles':'ROL','features':'FTR','acceptance':'ACC','systems':'SYS','data':'DAT','interfaces':'IFC','flows':'FLW','dependencies':'EXT','capabilities':'CAP','decisions':'DEC','unknowns':'UNK'}
DEP={'NONE':-1,'L0':0,'L1':1,'L2':2};DOM={'PRODUCT','BEHAVIOR','ARCHITECTURE','DATA','INTERFACES','QUALITY','DELIVERY','DECISIONS'};ROOT={'ACT','ROL','ACC','SYS','DAT','IFC','FLW','EXT','CAP','DEC'}
PAT={x:re.compile(r'^'+x+r'-[0-9]{3,}$') for x in COL.values()};SAFE=re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*\.md$');HEAD=re.compile(r'^(#{1,6})\s+(.+?)\s*$')
TC={};SC={}
def ne(x):return isinstance(x,str) and bool(x.strip())
def rr(x):return set(x.get('refs',[])) if isinstance(x,dict) and set(x)=={'refs'} and isinstance(x.get('refs'),list) else set()
class P:
 def __init__(s):s.e=[];s.b=[]
 def m(s,x):s.e.append(('MODEL_ERROR',x))
 def r(s,x,b=False):(s.b if b else s.e).append(('REFERENCE_ERROR',x))
 def x(s,c,x):s.b.append((c,x))
def exact(o,k,p,l):
 if not isinstance(o,dict):p.m(l+' must be an object');return False
 a=set(o);k=set(k)
 if a!=k:p.m(f"{l} has invalid fields (missing={','.join(sorted(k-a))}; extra={','.join(sorted(a-k))})");return False
 return True
def sl(x,p,l,n=0):
 if not isinstance(x,list):p.m(l+' must be an array');return False
 if len(x)<n:p.m(f'{l} must contain at least {n} item(s)');return False
 ok=True
 for i,v in enumerate(x):
  if not ne(v):p.m(f'{l}[{i}] must be a non-empty string');ok=False
 return ok
def en(v,a,p,l):
 if v not in a:p.m(l+' is invalid')
def rel(x,p,l):
 if not isinstance(x,dict) or set(x) not in ({'refs'},{'na'}):p.m(l+' must contain exactly one of refs or na');return False
 if 'refs' in x:return sl(x['refs'],p,l+'.refs',1)
 if not ne(x['na']):p.m(l+'.na must be a non-empty rationale');return False
 return True
def dparse(x):
 if not isinstance(x,str) or x.count('#')!=1:return None
 path,tok=x.split('#',1)
 if not tok or any(c.isspace() for c in tok):return None
 m=re.fullmatch(r'docs/([A-Z]+)\.md',path)
 if m:return (m.group(1),path[5:],tok) if m.group(1) in DOM else None
 m=re.fullmatch(r'docs/([a-z]+)/([^/]+)',path)
 if not m:return None
 low,f=m.groups();d=low.upper()
 return (d,f'{low}/{f}',tok) if d in DOM and SAFE.fullmatch(f) else None
def markdown(t):
 def drop(m):return '\n'*m.group(0).count('\n')
 lines=re.sub(r'<!--.*?(?:-->|$)',drop,t,flags=re.S).splitlines();heads=[];fence=None
 for i,line in enumerate(lines):
  if fence:
   ch,n=fence
   if re.fullmatch(rf'\s{{0,3}}{re.escape(ch)}{{{n},}}\s*',line):fence=None
   continue
  fm=re.match(r'^\s{0,3}(`{3,}|~{3,})',line)
  if fm:
   run=fm.group(1);fence=(run[0],len(run));continue
  m=HEAD.match(line)
  if m:heads.append((i,len(m.group(1)),m.group(2)))
 return lines,heads
def section(t,tok):
 lines,heads=markdown(t);matches=[h for h in heads if h[2]==tok or h[2].startswith(tok+' ')]
 if not matches:return 'MISSING',None
 if len(matches)!=1:return 'DUPLICATE',None
 st,lv,_=matches[0];end=len(lines)
 for i,n,_ in heads:
  if i>st and n<=lv:end=i;break
 return 'OK',lines[st+1:end]
def has_content(lines):
 return any(line.strip() and not HEAD.match(line) for line in lines)
def doc(target,x,want,p,l,support=False):
 q=dparse(x)
 if not q:p.r(l+' has invalid document path');return False
 d,path,tok=q
 if want and d!=want:p.r(f'{l} must reference authority domain {want}');return False
 fp=target/'docs'/path
 if fp not in TC:
  try:TC[fp]=fp.read_text(encoding='utf-8')
  except OSError as e:p.r(f'{l} cannot read {fp}: {e}',True);return False
 k=(fp,tok)
 if k not in SC:SC[k]=section(TC[fp],tok)
 status,s=SC[k]
 if status=='MISSING':p.r(f'{l} missing heading token {tok}',True);return False
 if status=='DUPLICATE':p.r(f'{l} heading token {tok} matches multiple canonical headings',True);return False
 if not has_content(s):
  if support:p.x('COVERAGE_GAP',l+' resolves to a section without support content')
  else:p.r(l+' resolves to a section without content',True)
  return False
 return True
def ref(x,want,ids,p,l):
 if x not in ids:p.r(f'{l} references unknown id {x!r}');return False
 if want and ids[x] not in set(want):p.r(f'{l} expects {sorted(want)} but found {ids[x]}');return False
 return True
def recs(c,p):
 specs={'actors':({'id','name','kind','doc_ref'},{'kind':{'HUMAN','SYSTEM','EXTERNAL'}}),'roles':({'id','name','actor_refs','doc_ref'},{}),'acceptance':({'id','doc_ref'},{}),'systems':({'id','name','doc_ref','decision_refs'},{}),'data':({'id','name','kind','owner_system_ref','doc_ref'},{'kind':{'PERSISTENT','MATERIAL_EPHEMERAL'}}),'interfaces':({'id','name','kind','owner_system_ref','peer_refs','doc_ref'},{'kind':{'API','EVENT','JOB','COMMAND','PROTOCOL','FILE','PUBLIC_LIBRARY'}}),'flows':({'id','name','kind','critical','doc_ref','system_refs','interface_refs','data_refs','dependency_refs'},{'kind':{'USER','SYSTEM','FAILURE'}}),'dependencies':({'id','name','kind','critical','doc_ref'},{'kind':{'SERVICE','API','VENDOR','LIBRARY','PLATFORM','DATA_SOURCE'}}),'decisions':({'id','kind','subject','outcome','reversibility','doc_ref'},{'kind':{'TECHNOLOGY','ARCHITECTURE','BUILD_BUY','DATA','INTERFACE','DELIVERY','OTHER'},'reversibility':{'REVERSIBLE','COSTLY','IRREVERSIBLE'}})}
 for n,(ks,es) in specs.items():
  for i,r in enumerate(c[n]):
   l=f'{n}[{i}]'
   if not exact(r,ks,p,l):continue
   for k in ('name','subject','outcome'):
    if k in r and not ne(r[k]):p.m(l+'.'+k+' must be non-empty')
   for k,v in es.items():en(r[k],v,p,l+'.'+k)
   if n=='roles':sl(r['actor_refs'],p,l+'.actor_refs')
   if n=='systems':sl(r['decision_refs'],p,l+'.decision_refs')
   if n=='interfaces':sl(r['peer_refs'],p,l+'.peer_refs')
   if n=='flows':
    if not isinstance(r['critical'],bool):p.m(l+'.critical must be boolean')
    for k in ('system_refs','interface_refs','data_refs','dependency_refs'):sl(r[k],p,l+'.'+k)
   if n=='dependencies' and not isinstance(r['critical'],bool):p.m(l+'.critical must be boolean')
 for i,r in enumerate(c['features']):
  l=f'features[{i}]';ks={'id','name','actor_refs','spec_ref','acceptance_refs','relations','decision_refs'}
  if not exact(r,ks,p,l):continue
  if not ne(r['name']):p.m(l+'.name must be non-empty')
  sl(r['actor_refs'],p,l+'.actor_refs',1);sl(r['acceptance_refs'],p,l+'.acceptance_refs',1);sl(r['decision_refs'],p,l+'.decision_refs')
  if not ne(r['spec_ref']):p.m(l+'.spec_ref must be non-empty')
  rk={'roles','flows','data','interfaces','dependencies','capabilities'}
  if exact(r['relations'],rk,p,l+'.relations'):
   for k in rk:rel(r['relations'][k],p,l+'.relations.'+k)
 for i,r in enumerate(c['capabilities']):
  l=f'capabilities[{i}]'
  if not isinstance(r,dict):p.m(l+' must be object');continue
  st,d=r.get('status'),r.get('disposition')
  if st=='OPEN':
   if exact(r,{'id','name','status','disposition','system_refs','dependency_refs','blocking_unknown_ref'},p,l) and d is not None:p.m(l+'.disposition must be null when OPEN')
  elif st=='RESOLVED' and d=='DEFER':exact(r,{'id','name','status','disposition','system_refs','dependency_refs','defer_ref'},p,l)
  elif st=='RESOLVED' and d in {'BUILD','BUY','HYBRID'}:
   if exact(r,{'id','name','status','disposition','system_refs','dependency_refs','decision_ref','boundary_ref','exit'},p,l):
    e=r['exit']
    if not isinstance(e,dict) or set(e) not in ({'ref'},{'na'}) or not ne(next(iter(e.values()),'')):p.m(l+'.exit must contain exactly one non-empty ref or na')
  else:p.m(l+'.status/disposition is invalid')
  if isinstance(r,dict):
   if 'name' in r and not ne(r['name']):p.m(l+'.name must be non-empty')
   for k in ('system_refs','dependency_refs'):
    if k in r:sl(r[k],p,l+'.'+k)
 K={'QUESTION','DECISION_REQUIRED','ASSUMPTION','AUTHORITY_CONFLICT','CONTRADICTION'};PH={'DESIGN','IMPLEMENTATION','VERIFICATION','POST_MILESTONE'}
 for i,r in enumerate(c['unknowns']):
  l=f'unknowns[{i}]';base={'id','kind','question','affected_refs','affected_coverage','blocking','reason','resolution_phase','status'}
  if not isinstance(r,dict):p.m(l+' must be object');continue
  if not exact(r,base|({'resolved_by_ref'} if r.get('status')=='RESOLVED' else set()),p,l):continue
  en(r['kind'],K,p,l+'.kind');en(r['resolution_phase'],PH,p,l+'.resolution_phase');en(r['status'],{'OPEN','RESOLVED'},p,l+'.status')
  if not ne(r['question']) or not ne(r['reason']):p.m(l+' question/reason must be non-empty')
  sl(r['affected_refs'],p,l+'.affected_refs');sl(r['affected_coverage'],p,l+'.affected_coverage')
  if not isinstance(r['blocking'],bool):p.m(l+'.blocking must be boolean')
  if r['status']=='OPEN' and r['kind'] in {'AUTHORITY_CONFLICT','CONTRADICTION'} and r['blocking'] is not True:p.m(l+' open conflict/contradiction must be blocking')
  if r['status']=='OPEN' and r['kind']=='DECISION_REQUIRED' and r['resolution_phase']=='DESIGN' and r['blocking'] is not True:p.m(l+' open DESIGN DECISION_REQUIRED must be blocking')
  if r['status']=='OPEN' and r['blocking'] is True and r['resolution_phase']!='DESIGN':p.m(l+' open blocking unknown must resolve in DESIGN')
def structure(c,t,p):
 if not isinstance(c,dict):p.m('catalog root must be an object');return
 if set(c)!=set(TOP):p.m('top-level catalog fields are invalid')
 if c.get('model_version')!=V:p.m(f"unsupported model_version: {c.get('model_version')!r}")
 m=c.get('milestone')
 if exact(m,{'id','name','scope_state','scope_ref','root_refs'},p,'milestone'):
  if not ne(m['id']) or not ne(m['name']) or not ne(m['scope_ref']):p.m('milestone string fields must be non-empty')
  en(m['scope_state'],{'OPEN','FROZEN'},p,'milestone.scope_state')
  if sl(m['root_refs'],p,'milestone.root_refs'):
   if len(m['root_refs'])!=len(set(m['root_refs'])):p.m('milestone.root_refs contains duplicates')
   for x in m['root_refs']:
    a=x.split('-',1)[0]
    if a not in ROOT or not PAT.get(a,re.compile('a^')).fullmatch(x):p.m('milestone.root_refs contains forbidden identity class: '+x)
 cov=c.get('coverage');exp=set(t)
 if not isinstance(cov,dict):p.m('coverage must be an object')
 else:
  if set(cov)!=exp:p.m('coverage taxonomy set mismatch')
  for k,e in cov.items():
   if k not in exp:continue
   l='coverage.'+k
   if not isinstance(e,dict):p.m(l+' must be an object');continue
   if e.get('applicability')=='NA':
    if k=='product.objective':p.m(l+' is always APPLICABLE in V1')
    elif exact(e,{'applicability','rationale'},p,l) and not ne(e['rationale']):p.m(l+' N/A requires a non-empty rationale')
   elif e.get('applicability')=='APPLICABLE':
    if exact(e,{'applicability','required_depth','actual_depth','support_refs','rationale'},p,l):
     en(e['required_depth'],{'L0','L1','L2'},p,l+'.required_depth');en(e['actual_depth'],set(DEP),p,l+'.actual_depth');sl(e['support_refs'],p,l+'.support_refs')
     if not isinstance(e['rationale'],str):p.m(l+'.rationale must be a string')
     if e['required_depth'] in {'L0','L2'} and not ne(e['rationale']):p.m(l+' requires non-empty rationale')
     if e['actual_depth']=='NONE' and e['support_refs']:p.m(l+' actual_depth NONE requires empty support_refs')
     if e['actual_depth']!='NONE' and not e['support_refs']:p.m(l+' resolved actual_depth requires at least one support_ref')
   else:p.m(l+'.applicability must be APPLICABLE or NA')
 for n in COL:
  if not isinstance(c.get(n),list):p.m(n+' must be an array')
 if p.e:return
 recs(c,p);seen={}
 for n,a in COL.items():
  for i,r in enumerate(c[n]):
   if not isinstance(r,dict):continue
   x=r.get('id');l=f'{n}[{i}].id'
   if not isinstance(x,str) or not PAT[a].fullmatch(x):p.m(f'{l} does not match {a} identity class');continue
   if x in seen:p.m('duplicate global id '+x)
   seen[x]=a
def references(c,t,target,p):
 ids={r['id']:COL[n] for n in COL for r in c[n]};cc=set(c['coverage']);doc(target,c['milestone']['scope_ref'],'PRODUCT',p,'milestone.scope_ref')
 for x in c['milestone']['root_refs']:
  if ref(x,ROOT,ids,p,'milestone.root_refs') and ids[x]=='CAP':
   q=next(z for z in c['capabilities'] if z['id']==x)
   if q.get('status')=='RESOLVED' and q.get('disposition')=='DEFER':p.m('milestone.root_refs cannot contain DEFER capability '+x)
 for k,e in c['coverage'].items():
  if e['applicability']=='APPLICABLE':
   for i,x in enumerate(e['support_refs']):doc(target,x,t[k]['authority_domain'],p,f'coverage.{k}.support_refs[{i}]',True)
 for r in c['actors']:doc(target,r['doc_ref'],'PRODUCT',p,r['id']+'.doc_ref')
 for r in c['roles']:
  doc(target,r['doc_ref'],'PRODUCT',p,r['id']+'.doc_ref');[ref(x,{'ACT'},ids,p,r['id']+'.actor_refs') for x in r['actor_refs']]
 for r in c['features']:
  doc(target,r['spec_ref'],'BEHAVIOR',p,r['id']+'.spec_ref');[ref(x,{'ACT'},ids,p,r['id']+'.actor_refs') for x in r['actor_refs']];[ref(x,{'ACC'},ids,p,r['id']+'.acceptance_refs') for x in r['acceptance_refs']];[ref(x,{'DEC'},ids,p,r['id']+'.decision_refs') for x in r['decision_refs']]
  for k,w in [('roles',{'ROL'}),('flows',{'FLW'}),('data',{'DAT'}),('interfaces',{'IFC'}),('dependencies',{'EXT'}),('capabilities',{'CAP'})]:[ref(x,w,ids,p,r['id']+'.relations.'+k) for x in rr(r['relations'][k])]
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
def edges(c):
 e={}
 def add(x,v):e.setdefault(x,set()).update(y for y in v if isinstance(y,str))
 for r in c['actors']:add(r['id'],[])
 for r in c['roles']:add(r['id'],r['actor_refs'])
 for r in c['features']:
  v=list(r['actor_refs'])+list(r['acceptance_refs'])+list(r['decision_refs'])
  for k in ('roles','flows','data','interfaces','dependencies','capabilities'):v+=list(rr(r['relations'][k]))
  add(r['id'],v)
 for r in c['acceptance']:add(r['id'],[])
 for r in c['systems']:add(r['id'],r['decision_refs'])
 for r in c['data']:add(r['id'],[r['owner_system_ref']])
 for r in c['interfaces']:add(r['id'],[r['owner_system_ref']]+list(r['peer_refs']))
 for r in c['flows']:add(r['id'],r['system_refs']+r['interface_refs']+r['data_refs']+r['dependency_refs'])
 for r in c['dependencies']:add(r['id'],[])
 for r in c['capabilities']:
  v=list(r['system_refs'])+list(r['dependency_refs'])
  if r['status']=='OPEN':v.append(r['blocking_unknown_ref'])
  elif r['disposition']!='DEFER':v.append(r['decision_ref'])
  add(r['id'],v)
 for r in c['decisions']:add(r['id'],[])
 for r in c['unknowns']:
  v=list(r['affected_refs'])+([r['resolved_by_ref']] if r['status']=='RESOLVED' else []);add(r['id'],v)
 return e
def orphan(c,p):
 e=edges(c);q=deque([r['id'] for r in c['features']]+c['milestone']['root_refs']);seen=set()
 while q:
  x=q.popleft()
  if x in seen:continue
  seen.add(x)
  for y in sorted(e.get(x,())):
   if y not in seen:q.append(y)
 for n,a in COL.items():
  if a in {'FTR','UNK'}:continue
  for r in c[n]:
   if a=='CAP' and r.get('status')=='RESOLVED' and r.get('disposition')=='DEFER':continue
   if r['id'] not in seen:p.x('ORPHAN',r['id']+' is an orphan active '+n+' record')
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
  for x in rr(f['relations']['flows']):
   q=fm.get(x)
   if not q:continue
   for field,rn in [('interface_refs','interfaces'),('data_refs','data'),('dependency_refs','dependencies')]:
    miss=set(q[field])-rr(f['relations'][rn])
    if miss:p.x('TRACEABILITY_GAP',f"{f['id']} relation {rn} omits {sorted(miss)} used by {x}")
 um={u['id']:u for u in c['unknowns']};fc=set().union(*(rr(f['relations']['capabilities']) for f in c['features'])) if c['features'] else set()
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
def tax(path,p):
 try:t=json.loads(path.read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError) as e:p.m('validator taxonomy cannot be loaded: '+str(e));return None
 if not isinstance(t,dict) or t.get('model_version')!=V or not isinstance(t.get('concerns'),dict):p.m('validator taxonomy is malformed or unsupported');return None
 c=t['concerns']
 if len(c)!=45:p.m('validator taxonomy must contain exactly 45 concerns');return None
 for k,m in c.items():
  if not ne(k) or not exact(m,{'authority_domain','description'},p,'taxonomy.'+k):continue
  if m['authority_domain'] not in DOM:p.m('taxonomy.'+k+'.authority_domain is invalid')
  if not ne(m['description']):p.m('taxonomy.'+k+'.description must be non-empty')
 return c
def emit(p):
 print('DOCS_READY = '+('FALSE' if p.e or p.b else 'TRUE'))
 for c,x in p.e+p.b:print(f'[{c}] {x}')
 return 2 if p.e else 1 if p.b else 0
def main(a=None):
 TC.clear();SC.clear();a=sys.argv[1:] if a is None else a;p=P()
 if len(a)!=1:p.m('usage: validate.py <target-repository-root>');return emit(p)
 target=Path(a[0]).resolve()
 try:c=json.loads((target/'docs/catalog/project.json').read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError) as e:p.m('cannot load catalog: '+str(e));return emit(p)
 t=tax(Path(__file__).resolve().parents[1]/'model/coverage.v1.json',p)
 if t is None or p.e:return emit(p)
 structure(c,t,p)
 if p.e:return emit(p)
 references(c,t,target,p)
 if p.e:return emit(p)
 closure(c,p);return emit(p)
if __name__=='__main__':raise SystemExit(main())
