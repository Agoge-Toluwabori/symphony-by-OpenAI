#!/usr/bin/env python3
"""One persistent Symphony controller; empty queues poll, task failures are isolated."""
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request
import uuid
import control as q
import publish
import runtime

FACTORY=Path(__file__).resolve().parents[1]
STATE=Path(os.environ['AGOGE_FACTORY_STATE'])

def release(c,lease):
    for label in ('factory-dispatch','symphony-ready','symphony-running'):q.remove_label(c,lease['number'],label)
    q.write(STATE/('lease-history-'+lease['nonce']+'.json'),lease)
    (STATE/'lease.json').unlink(missing_ok=True)

def block(c,lease,reason):
    q.comment(c,lease['number'],'Blocked after preserved investigation. '+reason[:2000]+'\nOther eligible issues continue. No per-command approval requested.')
    q.add_labels(c,lease['number'],['symphony-blocked']);q.phase(c,lease,'Blocked');release(c,lease)

def tick(c, running):
    lease_path=STATE/'lease.json'
    lease=json.loads(lease_path.read_text()) if lease_path.exists() else None
    if lease:
        workspace=Path(c['workspace_root'])/f"GH-{lease['number']}"
        if (workspace/'.factory-dependencies.json').exists() and not (workspace/'.factory-dependencies-result.json').exists():
            try:runtime.dependencies(c,workspace,STATE)
            except (ValueError,RuntimeError,subprocess.SubprocessError,OSError) as e:
                q.write(workspace/'.factory-dependencies-result.json',{'status':'failed','reason':type(e).__name__})
        if running:return
        receipt=STATE/('attempt-'+os.environ['INVOCATION_ID']+'-'+lease['nonce']+'.json')
        if not receipt.exists():
            if time.time()-lease.get('created_at',time.time())>600:
                block(c,lease,'Worker failed to launch within ten minutes; preserved hook/runtime diagnostics require technical recovery.')
            return
        pid=json.loads(receipt.read_text()).get('pid')
        if pid:
            try:os.kill(pid,0);return
            except ProcessLookupError:pass
        q.remove_label(c,lease['number'],'factory-dispatch')
        if q.api(c,f"issues/{lease['number']}")['state']=='closed':release(c,lease);return
        try:
            if (workspace/'.factory-blocker.json').exists():
                reason=runtime.read_request(workspace,'.factory-blocker.json').get('reason','Missing blocker evidence')
                block(c,lease,str(reason));return
            if not (workspace/'.factory-delivery.json').exists():raise RuntimeError('WORKER_RETURNED_WITHOUT_DELIVERY')
            publish.deliver(c,workspace,lease,STATE);release(c,lease)
        except (ValueError,RuntimeError,subprocess.SubprocessError,OSError) as error:
            code=str(error) if isinstance(error,(ValueError,RuntimeError)) else type(error).__name__
            # Never print subprocess stderr, request headers or auth configuration.
            if lease['attempt']>=c['attempts']:
                block(c,lease,'Bounded technical recovery exhausted: '+code);return
            q.comment(c,lease['number'],f"Recoverable delivery failure `{code}`. Preserve work, repair within acceptance scope; attempt {lease['attempt']+1}/{c['attempts']}. See prior local CI log and PR evidence.")
            q.remove_label(c,lease['number'],'factory-dispatch')
            lease.update(attempt=lease['attempt']+1,nonce=uuid.uuid4().hex,created_at=time.time(),not_before=time.time()+30*2**(lease['attempt']-1))
            q.write(lease_path,lease)
            # A restart or retry gets a fresh receipt and workspace while preserving old work.
            q.add_labels(c,lease['number'],['factory-dispatch'])
        return
    if running:return
    items=q.snapshot(c);selected=q.select(c,items)
    # Derived readiness never grants authority; remove stale dispatch labels on idle issues.
    for issue in q.pages(c,'issues?state=open&labels=factory-dispatch'):
        q.remove_label(c,issue['number'],'factory-dispatch')
    if selected:
        q.phase(c,selected,'Claimed');q.write(lease_path,selected)
        q.comment(c,selected['number'],'Ready → Claimed. Standing Project authority verified; isolated development into develop, concurrency one. Vercel/production excluded.')
        q.add_labels(c,selected['number'],['symphony-ready','factory-dispatch'])
    q.write(STATE/'continuous-health.json',{'time':time.time(),'selected':selected,'eligible_count':1 if selected else 0,'status':'working' if selected else 'idle','concurrency':1})
    print(json.dumps({'queue':'claimed' if selected else 'idle','issue':selected['number'] if selected else None}),flush=True)

def main():
    c=q.validate(json.loads((STATE/'batch.json').read_text()))
    lock=(STATE/'continuous.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    old=STATE/'lease.json'
    if old.exists():
        lease=json.loads(old.read_text());lease['nonce']=uuid.uuid4().hex;q.write(old,lease)
    command=[str(FACTORY.parents[2]/'elixir/bin/symphony'),str(STATE/'WORKFLOW.md'),'--port','4000','--logs-root',str(STATE/'logs'),'--i-understand-that-this-will-be-running-without-the-usual-guardrails']
    child=subprocess.Popen(command,cwd=FACTORY.parents[2]/'elixir')
    def stop(*_):raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    failures=0
    try:
        while child.poll() is None:
            try:
                with urllib.request.urlopen('http://127.0.0.1:4000/api/v1/state',timeout=5) as r:data=json.load(r)
                tick(c,data['running']);failures=0
            except (ValueError,RuntimeError,OSError,KeyError,subprocess.SubprocessError) as e:
                failures+=1;print(json.dumps({'queue_error':type(e).__name__,'retry':failures}),flush=True)
            time.sleep(min(c['poll_seconds']*max(1,failures),120))
    except KeyboardInterrupt:pass
    finally:
        child.terminate()
        try:child.wait(timeout=25)
        except subprocess.TimeoutExpired:child.kill();child.wait()
    if child.returncode not in (0,-signal.SIGTERM):raise SystemExit(1)

if __name__=='__main__':main()
