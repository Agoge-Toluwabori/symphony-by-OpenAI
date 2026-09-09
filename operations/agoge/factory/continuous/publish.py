"""Trusted exact-repository publication; never runs application code on the host."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import uuid
import control as q
import runtime

SAFE_GIT=['git','-c','core.hooksPath=/dev/null','-c','core.fsmonitor=false','-c','gc.auto=0']
def git(root,*args):
    env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_NO_REPLACE_OBJECTS='1',GIT_TERMINAL_PROMPT='0')
    return q.command(SAFE_GIT+['-C',str(root),*args],env=env)

def inspect(c, workspace, lease, request):
    if set(request)!={'commit','summary'} or not re.fullmatch(r'[0-9a-f]{40}',request['commit']) or not isinstance(request['summary'],str):raise ValueError('Invalid delivery request')
    if workspace.resolve()!=Path(c['workspace_root'])/f"GH-{lease['number']}":raise ValueError('Wrong workspace')
    if (workspace/'.git').is_symlink() or (workspace/'.git/objects/info/alternates').exists():raise ValueError('Unsafe Git metadata')
    branch=git(workspace,'branch','--show-current').strip()
    if not q.permitted_ref(c,'refs/heads/'+branch) or not branch.startswith(f"symphony/GH-{lease['number']}-"):raise ValueError('Forbidden ref')
    if git(workspace,'rev-parse','HEAD').strip()!=request['commit']:raise ValueError('HEAD mismatch')
    git(workspace,'diff','--exit-code');git(workspace,'diff','--cached','--exit-code')
    return branch

def deliver(c,workspace,lease,state):
    request=runtime.read_request(workspace,'.factory-delivery.json');branch=inspect(c,workspace,lease,request)
    sha=request['commit'];base=q.api(c,'branches/'+c['integration_branch'])['commit']['sha']
    existing=q.api(c,'pulls?state=all&head='+c['repository'].split('/')[0]+':'+branch+'&base='+c['integration_branch'])
    for pr in existing:
        detail=q.api(c,f"pulls/{pr['number']}")
        if detail.get('merged') and detail['head']['sha']==sha and detail['base']['ref']==c['integration_branch']:
            comparison=q.api(c,'compare/'+detail['merge_commit_sha']+'...'+c['integration_branch'])
            if comparison['status'] not in ('ahead','identical'):raise ValueError('Previously merged delivery no longer integrated')
            q.phase(c,lease,'Completed')
            q.api(c,f"issues/{lease['number']}",'PATCH',{'state':'closed','state_reason':'completed'})
            q.write(state/('completed-'+str(lease['number'])+'.json'),{'issue':lease['number'],'sha':sha,'merge':detail['merge_commit_sha'],'pr':detail['html_url'],'recovered':True})
            return {'merged':True,'sha':detail['merge_commit_sha']}
    destination=state/('validation-'+str(lease['number'])+'-'+uuid.uuid4().hex)
    # Local clone does not inherit worker hooks, aliases, config or credentials.
    q.command(SAFE_GIT+['clone','--no-hardlinks','--no-checkout',str(workspace),str(destination)])
    git(destination,'checkout','--detach',sha)
    git(destination,'merge-base','--is-ancestor',c['foundation'],sha)
    # Require current develop ancestry; let the worker repair scoped conflicts on retry.
    fetch(c,destination,c['integration_branch'])
    git(destination,'merge-base','--is-ancestor',base,sha)
    names=git(destination,'diff','--name-only',base,sha).splitlines()
    if not names or not q.safe_changes(c,names):raise ValueError('Protected path or empty delivery')
    if any(line.startswith('120000 ') for line in git(destination,'ls-tree','-r',sha).splitlines()):raise ValueError('Symlink publication requires reviewed policy')
    for name in names:
        if Path(name).suffix in ('.json','.ts','.tsx','.js','.py','.md','.yml','.yaml','.toml','.txt','.sql') and (destination/name).is_file():
            if re.search(rb'(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)',(destination/name).read_bytes()):raise ValueError('Secret-pattern publication rejected')
    # A task cannot change the CI command definitions to manufacture green checks.
    for name in ('package.json',):
        old=json.loads(git(destination,'show',base+':'+name));new=json.loads((destination/name).read_text())
        if old.get('scripts')!=new.get('scripts'):raise ValueError('Acceptance/CI script modification requires gate review')
    q.phase(c,lease,'Validating');q.write(state/'lease.json',lease)
    runtime.prepare(c,destination)
    # Dependencies are checked against the submitted lock, not silently reused on mismatch.
    canonical=Path(c['runtime_source'])/'pnpm-lock.yaml'
    if (destination/'pnpm-lock.yaml').read_bytes()!=canonical.read_bytes():
        q.write(destination/'.factory-dependencies.json',{'requested':True});runtime.dependencies(c,destination,state)
        if git(destination,'diff','--name-only').strip():raise ValueError('Dependency resolution changed committed lockfile; worker must commit it')
    command=['/usr/bin/env','-i','HOME=/home/toluadmin','CODEX_HOME='+str(state/'codex-home'),'PATH=/usr/bin:/bin',
             '/home/toluadmin/.local/bin/codex','sandbox','-P','factory-canary','-C',str(destination),
             '/bin/bash','-c','source .factory-runtime/env.sh; exec "$@"','ci',*c['tests']]
    result=subprocess.run(command,capture_output=True,text=True,timeout=1800)
    log=re.sub(r'(?:ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|sk-proj-[A-Za-z0-9_-]+)','[REDACTED]',result.stdout+result.stderr)
    (state/('ci-'+sha+'.log')).write_text(log)
    if result.returncode:raise RuntimeError('FULL_CI_FAILED:'+sha)
    if git(destination,'diff','--name-only').strip():raise ValueError('CI modified tracked input')
    # Re-read the issue: revocation/blocking before publication stops this delivery.
    issue=q.api(c,f"issues/{lease['number']}")
    if issue['state']!='open' or q.labels(issue)&q.EXCLUDED:raise ValueError('Issue no longer authorized')
    assert_authority(c,lease)
    push(c,destination,sha,branch)
    q.api(c,'statuses/'+sha,'POST',{'state':'success','context':'agoge-factory/ci','description':'Isolated full required CI passed; exact commit verified'})
    prs=q.api(c,'pulls?state=open&head='+c['repository'].split('/')[0]+':'+branch+'&base='+c['integration_branch'])
    pr=prs[0] if prs else q.api(c,'pulls','POST',{'title':f"GH-{lease['number']}: "+issue['title'][:180],'head':branch,'base':c['integration_branch'],
         'body':f"Implements #{lease['number']} acceptance criteria.\n\n{request['summary'][:4000]}\n\nValidation: isolated full CI passed at `{sha}`. No production acceptance. Rollback: a new revert PR into develop; no shared-history rewrite."})
    q.phase(c,lease,'GitHub Integrated');q.write(state/'lease.json',lease)
    for attempt in range(20):
        statuses=q.api(c,'commits/'+sha+'/status')['statuses'];checks=q.api(c,'commits/'+sha+'/check-runs')['check_runs']
        if q.checks_pass(c,statuses,checks):break
        time.sleep(min(15*(attempt+1),60))
    else:raise RuntimeError('REQUIRED_CHECKS_NOT_GREEN')
    current=q.api(c,f"pulls/{pr['number']}")
    if current['head']['sha']!=sha or current['head']['repo']['full_name']!=c['repository'] or current['base']['ref']!=c['integration_branch']:raise ValueError('PR identity changed')
    if q.api(c,'branches/'+c['integration_branch'])['commit']['sha']!=base:raise ValueError('Integration base changed; revalidate')
    assert_authority(c,lease)
    merged=q.api(c,f"pulls/{pr['number']}/merge",'PUT',{'sha':sha,'merge_method':c['merge_method']})
    if not merged.get('merged'):raise RuntimeError('MERGE_NOT_CONFIRMED')
    q.comment(c,lease['number'],f"GitHub Integrated → Completed. PR {pr['html_url']}; tested commit `{sha}`; integration `{merged['sha']}`. Full isolated CI and required checks passed. Rollback: new revert PR into develop. GitHub completion is not production deployment/acceptance.")
    q.phase(c,lease,'Completed');q.api(c,f"issues/{lease['number']}",'PATCH',{'state':'closed','state_reason':'completed'})
    q.write(state/('completed-'+str(lease['number'])+'.json'),{'issue':lease['number'],'sha':sha,'merge':merged['sha'],'pr':pr['html_url']})
    return merged

def credentials(c,root):
    git(root,'remote','set-url','origin','https://github.com/'+c['repository']+'.git')
    git(root,'config','credential.helper','!gh auth git-credential')

def fetch(c,root,branch):
    if branch!=c['integration_branch']:raise ValueError('Invalid fetch branch')
    credentials(c,root);git(root,'fetch','origin',branch)

def push(c,root,sha,branch):
    if not q.permitted_ref(c,'refs/heads/'+branch):raise ValueError('Forbidden push')
    credentials(c,root)
    git(root,'push','origin',sha+':refs/heads/'+branch) # never force, delete, main, tags or develop


def assert_authority(c,lease):
    item=next((i for i in q.snapshot(c) if i['id']==lease['item_id']),None)
    if not item or item.get(c['authority_key'])!='Autonomous Development' or item.get('status') not in ('In Progress','In Review'):
        raise ValueError('Project authority/lifecycle changed; publication stopped')
