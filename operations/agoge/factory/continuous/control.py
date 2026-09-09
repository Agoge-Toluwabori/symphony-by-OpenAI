"""Reusable host control plane. Only configured repository/Project; no provider tools."""
import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

EXCLUDED = {'delivery:planning-only','planning-only','symphony-blocked','human-review','status:human-review','authority:owner-gate','authority:prohibited','symphony-canary','canary'}

def validate(c):
    if c['version'] != 2 or c['mode'] != 'continuous' or c['max_concurrency'] != 1:
        raise ValueError('Unsupported continuous policy or concurrency')
    if not re.fullmatch(r'[\w.-]+/[\w.-]+',c['repository']) or (c['integration_branch'] in ('main','master') or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]*',c['integration_branch'])):
        raise ValueError('Invalid repository or integration branch')
    if c['merge_method'] not in ('merge','squash') or not c['required_checks'] or not c['tests']:
        raise ValueError('Missing merge/validation gate')
    return c

def command(args, **kwargs):
    r=subprocess.run(args,capture_output=True,text=True,timeout=kwargs.pop('timeout',120),**kwargs)
    if r.returncode: raise RuntimeError('COMMAND_FAILED:'+Path(args[0]).name+':'+str(r.returncode))
    return r.stdout

def gh(args, body=None):
    text=command(['gh',*args],input=json.dumps(body) if body is not None else None)
    return json.loads(text) if text.strip() else None

def api(c, route, method='GET', body=None):
    # This is a host library, not an arbitrary route tool exposed to a model.
    return gh(['api','--method',method,'repos/'+c['repository']+'/'+route]+(['--input','-'] if body is not None else []),body)

def pages(c, route):
    result=[]
    for page in range(1,101):
        data=api(c,route+('&' if '?' in route else '?')+f'per_page=100&page={page}')
        if not isinstance(data,list): raise ValueError('Invalid page')
        result+=data
        if len(data)<100:return result
    raise ValueError('Pagination limit')

def labels(issue):return {i['name'] if isinstance(i,dict) else i for i in issue.get('labels',[])}

def eligible(c, item, issue, dependencies):
    n=issue.get('number')
    if n in c['excluded_issues'] or issue.get('state')!='open' or item.get('status')!='Ready':return False
    if item.get('content',{}).get('repository')!=c['repository'] or item.get(c['authority_key'])!='Autonomous Development':return False
    if labels(issue)&EXCLUDED or item.get('task Type','').lower() in ('planning','decision','deployment','canonical epic','work package'):return False
    # Both native GitHub dependencies and explicit Project issue references count.
    text=item.get('depends On','')
    ids={int(x) for x in re.findall(r'#(\d+)',text)}
    if text.strip() and not ids and not re.match(r'(?i)^(none|no (delivery )?predecessor|n/a)',text.strip()):return False
    if any(d.get('repository_url')!='https://api.github.com/repos/'+c['repository'] for d in dependencies):return False
    ids|={d['number'] for d in dependencies}
    by_id={d['number']:d for d in dependencies}
    for ident in sorted(ids):
        d=by_id.get(ident) or api(c,f'issues/{ident}')
        if d.get('state')!='closed' or d.get('state_reason') not in ('completed',None):return False
        if labels(d)&{'symphony-blocked','human-review','withdrawn','superseded'}:return False
    return True

def snapshot(c):
    data=gh(['project','item-list',str(c['project_number']),'--owner',c['project_owner'],'--limit','10000','--format','json'])
    if data.get('totalCount',len(data['items']))>len(data['items']):raise ValueError('Incomplete Project snapshot')
    return [i for i in data['items'] if i.get('content',{}).get('repository')==c['repository']]

def select(c, items, active=None):
    if active:return None
    for item in sorted(items,key=lambda x:x.get('content',{}).get('number',10**12)):
        if item.get('status')!='Ready' or item.get(c['authority_key'])!='Autonomous Development':continue
        n=item['content']['number'];issue=api(c,f'issues/{n}')
        deps=pages(c,f'issues/{n}/dependencies/blocked_by')
        if eligible(c,item,issue,deps):return {'number':n,'item_id':item['id'],'nonce':uuid.uuid4().hex,'phase':'Claimed','attempt':1,'created_at':time.time()}
    return None

def phase(c, lease, name):
    gh(['project','item-edit','--id',lease['item_id'],'--project-id',c['project_id'],'--field-id',c['status_field'],'--single-select-option-id',c['status_options'][name]])
    lease['phase']=name

def comment(c,n,text):api(c,f'issues/{n}/comments','POST',{'body':text})
def add_labels(c,n,names):api(c,f'issues/{n}/labels','POST',{'labels':names})
def remove_label(c,n,name):
    if name in labels(api(c,f'issues/{n}')):api(c,f'issues/{n}/labels/{name}','DELETE')

def write(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.chmod(0o600);tmp.replace(path)

def permitted_ref(c,ref,force=False,delete=False):
    return not force and not delete and bool(re.fullmatch(r'refs/heads/symphony/GH-[1-9][0-9]*-[A-Za-z0-9-]+',ref))

def safe_changes(c, names):
    return all(not any(fnmatch.fnmatch(n,p) for p in c['protected_paths']) and not re.search(r'(^|/)(\.env(?:\.|$)|[^/]*\.(pem|key)$)',n) for n in names)

def checks_pass(c,statuses,checks):
    values={}
    # API returns newest first; an old successful status must not override failure.
    for s in statuses:values.setdefault(s['context'],s['state']=='success')
    for s in checks:values.setdefault(s['name'],s['status']=='completed' and s['conclusion']=='success')
    return all(values.get(name) is True for name in c['required_checks'])
