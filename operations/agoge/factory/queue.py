#!/usr/bin/env python3
"""Host-only deterministic batch reconciler. Never starts an agent.
Authority lives in an owner-controlled manifest outside worker mounts.
GitHub labels are derived outputs; Project status is planning only.
"""
import argparse
import fcntl
import json
import os
import pathlib
import re
import subprocess
import urllib.request

AUTHORITIES = {'Autonomous Development', 'Owner Gate', 'Prohibited'}
TERMINAL = {'human-review', 'accepted', 'done'}

def validate(batch):
    if batch['version'] != 1 or batch['max_concurrency'] != 1:
        raise ValueError('Unsupported version or concurrency')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', batch['repository']):
        raise ValueError('Invalid repository')
    if not isinstance(batch['approved'], bool) or not batch['approval_source']:
        raise ValueError('Missing explicit approval')
    numbers = [t['number'] for t in batch['tasks']]
    if len(numbers) != len(set(numbers)):
        raise ValueError('Duplicate issue/workspace')
    for task in batch['tasks']:
        if type(task['number']) is not int or task['number'] < 1 or task['authority'] not in AUTHORITIES:
            raise ValueError('Invalid task')
        if any(type(n) is not int or n < 1 or n == task['number'] for n in task['dependencies']):
            raise ValueError('Invalid dependency')
    return batch

def labels(issue):
    return {x['name'] if isinstance(x, dict) else x for x in issue.get('labels', [])}

def accepted(issue):
    return issue.get('state', '').lower() == 'closed' and 'accepted' in labels(issue)

def select(batch, issues, active=()):
    validate(batch)
    if not batch.get('execution_enabled', False) or not batch['approved'] or active or any('symphony-running' in labels(i) for i in issues.values()):
        return None
    for task in batch['tasks']:  # owner-defined order, never issue query order
        issue = issues.get(task['number'], {})
        ls = labels(issue)
        if task['authority'] != 'Autonomous Development' or issue.get('state', '').lower() != 'open':
            continue
        if ls & (TERMINAL | {'symphony-blocked', 'authority:owner-gate', 'authority:prohibited'}):
            continue
        if issue.get('dependencies_verified') is not True:
            continue
        deps = set(task['dependencies']) | set(issue.get('blocked_by', []))
        if not all(accepted(issues.get(n, {})) for n in deps):
            continue
        return task['number']
    return None

def plan(batch, issues, active=()):
    selected = select(batch, issues, active)
    # Preserve actively claimed labels until the worker releases its claim.
    running = set(active) | {n for n, i in issues.items() if 'symphony-running' in labels(i)}
    return {'selected': selected, 'add_ready': [selected] if selected and 'symphony-ready' not in labels(issues[selected]) else [],
            'remove_ready': sorted(n for n, i in issues.items() if 'symphony-ready' in labels(i) and n != selected and n not in running),
            'batch': batch['batch'], 'boundary': selected is None and not running}

def gh(path, method='GET', body=None):
    cmd = ['gh', 'api', '--method', method, path]
    if body is not None:
        cmd += ['--input', '-']
    proc = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                          capture_output=True, text=True, timeout=45)
    if proc.returncode:
        # Never propagate CLI stderr, headers or credentials to logs.
        raise RuntimeError('GitHub request failed; details suppressed')
    return json.loads(proc.stdout) if proc.stdout.strip() else None

def pages(path):
    result = []
    for page in range(1, 101):
        data = gh(f'{path}{"&" if "?" in path else "?"}per_page=100&page={page}')
        if not isinstance(data, list):
            raise RuntimeError('Unexpected GitHub response')
        result.extend(data)
        if len(data) < 100:
            return result
    raise RuntimeError('Pagination limit; fail closed')

def snapshot(batch):
    prefix = '/repos/' + batch['repository']
    issues = {i['number']: i for i in pages(prefix + '/issues?state=all') if 'pull_request' not in i}
    for task in batch['tasks']:
        n = task['number']
        issue = issues.get(n)
        if issue is None:
            raise RuntimeError('Batch issue missing')
        deps = pages(f'{prefix}/issues/{n}/dependencies/blocked_by')
        if any(d.get('repository_url') != 'https://api.github.com' + prefix for d in deps):
            raise RuntimeError('Cross-repository dependency requires verified owner evidence')
        issue['blocked_by'] = [d['number'] for d in deps]
        issue['dependencies_verified'] = True
    return issues

def exhausted_retries(state, batch):
    approved = {t['number'] for t in batch['tasks']}
    return sorted(int(r['issue_id']) for r in state['retrying']
                  if int(r['issue_id']) in approved and r['attempt'] >= 3)


def recover_canary(batch, issues, directory):
    """One repair-specific reset of the documented pre-claim evidence failure."""
    from attestation import REPAIR
    receipt = directory/('recovery-'+REPAIR+'.json')
    if receipt.exists():
        return
    proof = json.loads((directory/'service-preflight.json').read_text())
    if proof.get('repair') != REPAIR or proof.get('invocation_id') != os.environ.get('INVOCATION_ID'):
        raise ValueError('Missing current repaired service preflight')
    if not proof.get('preflight') or any(v != 'verified' for v in proof['preflight'].values()):
        raise ValueError('Invalid repaired service preflight')
    if [t['number'] for t in batch['tasks']] != [236]:
        raise ValueError('Recovery is restricted to canary 236')
    current = issues[236]
    if 'symphony-blocked' not in labels(current):
        return
    candidate = dict(current, labels=sorted(labels(current)-{'symphony-blocked'}))
    if select(batch, issues | {236:candidate}) != 236:
        raise ValueError('Canary remains ineligible for a reason other than repaired blocker')
    prefix = '/repos/'+batch['repository']+'/issues/236'
    comments = pages(prefix+'/comments')
    latest = comments[-1]['body'] if comments else ''
    if 'controller-evidence' not in latest or 'before Claimed' not in latest:
        raise ValueError('Unknown canary blocker; not automatically clearing it')
    gh(prefix+'/comments','POST',{'body':'Factory dispatch-context repair: current host preflight passed. Prior controller-evidence failure and all local archives are retained. The repaired controller now supplies factory_context with service, batch, workspace and actual App Server session IDs. Restoring only #236 for one service invocation; batch stop verification belongs after completion. #235 remains untouched.'})
    gh(prefix+'/labels/symphony-blocked','DELETE')
    current['labels'] = candidate['labels']
    receipt.write_text(json.dumps({'repair':REPAIR,'invocation_id':proof['invocation_id'],'issue':236})+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', default=str(pathlib.Path(__file__).with_name('batch.json')))
    parser.add_argument('--snapshot')
    parser.add_argument('--repair-canary', action='store_true')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--prepare', action='store_true', help='Only under supervisor lifetime lock before controller starts')
    parser.add_argument('--state-dir', default='/tmp/agoge-factory-state')
    args = parser.parse_args()
    if (args.apply or args.prepare) and args.snapshot:
        parser.error('Cannot apply a fixture')
    batch = validate(json.loads(pathlib.Path(args.batch).read_text()))
    directory = pathlib.Path(args.state_dir)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (directory / 'queue.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        issues = {int(n): i for n, i in json.loads(pathlib.Path(args.snapshot).read_text()).items()} if args.snapshot else snapshot(batch)
        if args.repair_canary:
            if not args.prepare or args.snapshot:
                raise ValueError('Canary recovery requires the service prepare phase')
            recover_canary(batch, issues, directory)
        active = []
        if args.apply:
            # An unreachable controller is never interpreted as idle.
            with urllib.request.urlopen('http://127.0.0.1:4000/api/v1/state', timeout=5) as response:
                state = json.load(response)
            for n in exhausted_retries(state, batch):
                prefix = '/repos/' + batch['repository']
                if 'symphony-blocked' not in labels(issues[n]):
                    gh(f'{prefix}/issues/{n}/comments', 'POST', {'body': 'Factory runtime retry budget exhausted (three attempts). External execution environment requires repair; no per-command approval requested. Prior workspaces and evidence retained.'})
                    gh(f'{prefix}/issues/{n}/labels', 'POST', {'labels': ['symphony-blocked']})
                for label in ('symphony-ready', 'symphony-running'):
                    if label in labels(issues[n]):
                        gh(f'{prefix}/issues/{n}/labels/{label}', 'DELETE')
                issues[n]['labels'] = sorted((labels(issues[n]) - {'symphony-ready', 'symphony-running'}) | {'symphony-blocked'})
            active = [int(i['issue_id']) for key in ('running', 'retrying') for i in state[key]]
        result = plan(batch, issues, active)
        # A completed/failed first launch closes this service invocation, even if
        # the orchestrator has queued a retry. The launcher rejects any second launch.
        invocation = os.environ.get('INVOCATION_ID', '')
        if args.apply and invocation and (directory/('attempt-'+invocation+'.json')).exists() and not state['running']:
            result.update(selected=None, add_ready=[], boundary=True,
                          remove_ready=[t['number'] for t in batch['tasks'] if 'symphony-ready' in labels(issues[t['number']])])
        if args.apply or args.prepare:
            prefix = '/repos/' + batch['repository']
            for n in result['remove_ready']:
                if n not in {t['number'] for t in batch['tasks']}:
                    continue
                gh(f'{prefix}/issues/{n}/labels/symphony-ready', 'DELETE')
            for n in result['add_ready']:
                gh(f'{prefix}/issues/{n}/labels', 'POST', {'labels': ['symphony-ready']})
        # Consolidated report contains IDs/states only, never issue bodies or credentials.
        report = dict(result, tasks=[{'number': t['number'], 'authority': t['authority'],
                    'evidence_url': f"https://github.com/{batch['repository']}/issues/{t['number']}",
                    'state': issues[t['number']]['state'], 'labels': sorted(labels(issues[t['number']]))} for t in batch['tasks']])
        temp = directory / 'batch-report.tmp'
        temp.write_text(json.dumps(report, indent=2) + '\n')
        temp.replace(directory / 'batch-report.json')
        print(json.dumps(result, sort_keys=True))
        if (args.apply or args.prepare) and result["boundary"]:
            raise SystemExit(10)

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, KeyError, OSError, subprocess.TimeoutExpired):
        raise SystemExit('Factory reconciliation failed closed; inspect host health without printing credentials')
