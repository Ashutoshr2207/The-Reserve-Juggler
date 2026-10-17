"""Dependency-free blueprint/fixture checks, not a full OpenAPI validator or product test."""
from pathlib import Path
import copy,hashlib,json,re
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return f.read()
def load(p):return json.loads(read(p))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(doc,ref):
    if not ref.startswith('#/'):raise ValueError('Only local refs supported by this check: '+ref)
    node=doc
    for k in ref[2:].split('/'):node=node[k.replace('~1','/').replace('~0','~')]
    return node
def validate(v,s,doc,loc='$'):
    if '$ref' in s:return validate(v,resolve(doc,s['$ref']),doc,loc)
    for key in ['anyOf','oneOf']:
        if key in s:
            matched=0
            for branch in s[key]:
                try:validate(v,branch,doc,loc);matched+=1
                except (ValueError,TypeError,AssertionError):pass
            if (key=='anyOf' and matched<1) or (key=='oneOf' and matched!=1):raise ValueError(loc+' '+key)
    if 'const' in s and v!=s['const']:raise ValueError(loc+' const')
    if 'enum' in s and v not in s['enum']:raise ValueError(loc+' enum')
    t=s.get('type')
    if t=='object':
        if not isinstance(v,dict):raise ValueError(loc+' object')
        for k in s.get('required',[]):
            if k not in v:raise ValueError(loc+' required '+k)
        for k,x in v.items():
            if k not in s.get('properties',{}):
                if s.get('additionalProperties') is False:raise ValueError(loc+' undeclared '+k)
            else:validate(x,s['properties'][k],doc,loc+'.'+k)
    elif t=='array':
        if not isinstance(v,list):raise ValueError(loc+' array')
        if len(v)<s.get('minItems',0):raise ValueError(loc+' minItems')
        if 'maxItems' in s and len(v)>s['maxItems']:raise ValueError(loc+' maxItems')
        for i,x in enumerate(v):validate(x,s['items'],doc,loc+f'[{i}]')
    elif t=='string':
        if not isinstance(v,str):raise ValueError(loc+' string')
        if len(v)<s.get('minLength',0) or len(v)>s.get('maxLength',10**9):raise ValueError(loc+' length')
        if 'pattern' in s and re.search(s['pattern'],v) is None:raise ValueError(loc+' pattern')
    elif t in ['integer','number']:
        if isinstance(v,bool) or not isinstance(v,int if t=='integer' else (int,float)):raise ValueError(loc+' numeric')
        if 'minimum' in s and v<s['minimum']:raise ValueError(loc+' minimum')
        if 'maximum' in s and v>s['maximum']:raise ValueError(loc+' maximum')
        if 'exclusiveMinimum' in s and v<=s['exclusiveMinimum']:raise ValueError(loc+' exclusiveMinimum')
        if 'exclusiveMaximum' in s and v>=s['exclusiveMaximum']:raise ValueError(loc+' exclusiveMaximum')
    elif t=='boolean' and not isinstance(v,bool):raise ValueError(loc+' boolean')
    elif t=='null' and v is not None:raise ValueError(loc+' null')
def refs(doc):
    count=0
    def visit(v):
        nonlocal count
        if isinstance(v,dict):
            if '$ref' in v:resolve(doc,v['$ref']);count+=1
            for x in v.values():visit(x)
        elif isinstance(v,list):
            for x in v:visit(x)
    visit(doc);return count
def main():
    checks=[]
    required=['README.md','AGENTS.md','PROJECT_CONTEXT.md']+['docs/'+x+'.md' for x in ['PRD','FLOW','DESIGN','ARCHITECTURE','API_CONTRACT','AUTH_SECURITY','TEAM_PLAN','TESTING','DECISIONS','RELEASE_RUNBOOK','AI_DESIGN','AI_EVALUATION','MODEL_TRAINING_PLAN','PROJECT_STATUS','INTEGRATION_HANDOFF']]
    for name in required:assert (ROOT/name).is_file(),name
    checks.append(('Blueprint document inventory',True,str(len(required))+' required current documents'))
    selection=load(ROOT/'docs/SELECTION_RECORD.json')
    assert selection['status']=='ACCEPTED' and selection['acceptance_type']=='human_delegated_selection'
    assert selection['decision_sha256']==digest(ROOT/'docs/SOLUTION_DECISION.md')
    old=read(ROOT/'docs/history/phase02/SOLUTION_DECISION.md')
    now=read(ROOT/'docs/SOLUTION_DECISION.md')
    a=old.split('## 6. Exact proposed scope v0.2.0',1)[1].split('## 10. Selection record',1)[0]
    b=now.split('## 6. Exact proposed scope v0.2.0',1)[1].split('## 10. Selection record',1)[0]
    assert a==b and hashlib.sha256(b.encode()).hexdigest()==selection['accepted_scope_region_sha256']
    checks.append(('Acceptance and unchanged scope',True,'Explicit delegation recorded; scope 0.2.0 Sections 6–9 unchanged'))
    manifest=load(ROOT/'docs/sources/phase02/MANIFEST.json')
    for item in manifest['sources']:assert digest(ROOT/item['archive_path'])==item['sha256']
    for item in load(ROOT/'docs/sources/SOURCE_MANIFEST.json')['sources']:
        # Manifest retains original absolute provenance; verify the local archive after extraction.
        archived=ROOT/'docs/sources'/item['preservedPath'].replace('\\','/').split('/')[-1]
        assert digest(archived).upper()==item['sha256'].upper()
    checks.append(('Original source integrity',True,'S1–S5 and D07 hashes unchanged'))
    api=load(ROOT/'contracts/openapi.json');adapter=load(ROOT/'contracts/forecast-adapter.schema.json');fixture=load(ROOT/'contracts/examples/first_slice.json')
    count=refs(api)+refs(adapter)
    assert api['openapi']=='3.1.1' and adapter['$schema'].endswith('2020-12/schema')
    operations=[]
    for path,items in api['paths'].items():
        for method,op in items.items():
            operations.append(op['operationId']);assert op['x-local-roles']
            for p in re.findall(r'\{([^}]+)\}',path):assert any(x['name']==p and x['in']=='path' and x['required'] for x in op['parameters'])
            assert any(code.startswith('2') for code in op['responses'])
    assert len(operations)==len(set(operations))==12
    checks.append(('Executable specification structure/references',True,f'{len(operations)} HTTP operations; {count} local refs resolved; full standards validation pending'))
    for case in fixture['http_cases']:validate(case['value'],api['components']['schemas'][case['schema']],api)
    for value in fixture['adapter_cases']:validate(value,adapter,adapter)
    by={c['schema']:c['value'] for c in fixture['http_cases']}
    assert by['Scenario']['dataset_id']==by['Dataset']['dataset_id']==by['ScenarioCreate']['dataset_id']
    assert by['Run']['scenario_id']==by['Scenario']['scenario_id']==by['RunCreate']['scenario_id']
    assert by['MetricSet']['run_id']==by['Run']['run_id']==by['Decision']['run_id']
    assert by['MetricSet']['scenario_fingerprint']==by['Run']['scenario_fingerprint']==by['Scenario']['fingerprint']
    request=fixture['adapter_cases'][0]
    assert all(datetime.fromisoformat(r['timestamp'])<datetime.fromisoformat(request['origin']) for r in request['history'])
    checks.append(('First integrated contract fixture',True,f"{len(fixture['http_cases'])} HTTP + {len(fixture['adapter_cases'])} adapter examples; entity hashes/origin links agree; illustrative only"))
    bad=[]
    x=copy.deepcopy(by['ScenarioCreate']);x['settings']['opening_cash_cents']=50;bad.append(('ScenarioCreate',x))
    x=copy.deepcopy(by['ScenarioCreate']);x['settings']['opening_cash_cents']='1.01';bad.append(('ScenarioCreate',x))
    x=copy.deepcopy(by['RunCreate']);x['forecast_mode']='magical';bad.append(('RunCreate',x))
    x=copy.deepcopy(by['Run']);x['unexpected']=True;bad.append(('Run',x))
    x=copy.deepcopy(by['ScenarioCreate']);del x['settings']['reserve_floor_cents'];bad.append(('ScenarioCreate',x))
    for name,x in bad:
        try:validate(x,api['components']['schemas'][name],api)
        except ValueError:pass
        else:raise AssertionError('Invalid fixture accepted: '+name)
    x=copy.deepcopy(request);x['horizons_hours']=[25]
    try:validate(x,adapter,adapter)
    except ValueError:pass
    else:raise AssertionError('Invalid adapter horizon')
    assert re.search(api['components']['schemas']['Settings']['properties']['bond_units']['pattern'],'1.5')
    checks.append(('Negative contract examples',True,'6 malformed/unknown/missing/type/horizon cases rejected; decimal quantity format checked'))
    prd=read(ROOT/'docs/PRD.md');reqs=set(re.findall(r'\b(?:FR|NFR|AC)-\d{2}\b',prd))
    task_ids=[]
    for role in ['FRONTEND','BACKEND','AI_ML']:
        assignment=read(ROOT/'docs/assignments'/f'{role}.md')
        assert role in assignment and 'DESIGN' in assignment
        for ident in re.findall(r'\b(?:FR|NFR|AC)-\d{2}\b',assignment):assert ident in reqs,ident
        task_ids.extend(re.findall(r'\| ((?:FE|BE|AIM)-\d{2}) ',assignment))
        assert (ROOT/'docs/module_status'/f'{role}.md').exists()
    assert len(set(task_ids))==11
    checks.append(('Separate teammate traceability',True,'3 role assignments/status records, 11 owned task IDs, referenced requirement/acceptance IDs exist'))
    # Ignore archived originals/history: their legacy links are provenance, not blueprint defects.
    current=[ROOT/'README.md',ROOT/'AGENTS.md']+list((ROOT/'docs').glob('*.md'))+list((ROOT/'docs/assignments').glob('*.md'))+list((ROOT/'docs/module_status').glob('*.md'))
    localcount=0
    for p in current:
        if p.name in ['PHASE_00_CHECKS.md','PHASE_01_CHECKS.md','PHASE_02_CHECKS.md']:continue
        for match in re.finditer(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',read(p)):
            target=match.group(1).strip('<>')
            if target.startswith(('http:','https:','codex:','#','C:/','C:\\')):continue
            target=target.split('#')[0]
            assert (p.parent/target).exists(),(str(p),target)
            localcount+=1
    checks.append(('Local blueprint links',True,f'{localcount} relative targets resolved'))
    report={'version':'1.0','date':'2026-10-17','timezone':'Asia/Calcutta','checks':[{'check':a,'pass':b,'evidence':c} for a,b,c in checks],
      'limitations':['Supported-schema-subset checks only, no full OpenAPI/JSON-Schema standards validator installed.','No application server/client/browser, ledger replay, security, accessibility, performance or model-training test executed.','Original synthetic data is not institutional validation; open decisions remain.']}
    (ROOT/'docs/BLUEPRINT_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# Phase 03 / 03A actual blueprint checks','','Version: 1.0 | 2026-10-17 (Asia/Calcutta)','','Command: `python tools/check_blueprint.py`','','| Actual check | Result | Evidence |','|---|---|---|']
    lines.extend(f'| {a} | PASS | {c} |' for a,b,c in checks)
    lines+=['','These checks validate the blueprint and illustrative fixture, not a running app, financially correct replay or trained model. No standards-complete OpenAPI/JSON-Schema validator is installed; Phase 04 must add it and actual generated-client/server tests. No user/security/accessibility/performance test or training was performed. Packet/ZIP checks are separately recorded in PACKAGING_CHECKS.json.']
    (ROOT/'docs/BLUEPRINT_CHECKS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    for a,b,c in checks:print('PASS: '+a+' — '+c)
if __name__=='__main__':main()
