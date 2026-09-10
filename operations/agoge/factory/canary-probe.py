#!/usr/bin/env python3
"""Run inside the canary. Inspect identities/mappings, never credential bytes."""
import errno
import json
import os
from pathlib import Path
import socket


def identity():
    uids = os.getresuid()
    rows = [tuple(map(int, line.split())) for line in Path('/proc/self/uid_map').read_text().splitlines()]
    if not rows or any(len(row) != 3 or min(row) < 0 or row[2] <= 0 for row in rows):
        raise ValueError('Invalid UID mapping')
    # Project only UID 0 and this process's UIDs; omit unrelated mapping ranges.
    mapping = {}
    for uid in sorted({0, *uids}):
        matches = [outside + uid - inside for inside, outside, count in rows if inside <= uid < inside + count]
        if len(matches) > 1:
            raise ValueError('Ambiguous UID mapping')
        mapping[str(uid)] = matches[0] if matches else None
    return {'real':uids[0], 'effective':uids[1], 'saved':uids[2],
            'user_namespace':os.readlink('/proc/self/ns/user'),
            'parent_uid_mapping':mapping}


def unprivileged(snapshot):
    # IDs in uid_map's second column belong to the immediate parent namespace,
    # not necessarily the host. Parent UID 0 alone does not establish host root.
    # The full before/after comparison also rejects mapping or namespace changes.
    return all(type(snapshot[key]) is int and snapshot[key] > 0
               and snapshot['parent_uid_mapping'].get(str(snapshot[key])) is not None
               for key in ('real', 'effective', 'saved'))


def root_probe():
    evidence = {'before':None, 'after':None, 'errno':None, 'status':'UNPROVEN'}
    try:
        evidence['before'] = identity()
        if not unprivileged(evidence['before']):
            evidence['after'] = identity()
            evidence['status'] = 'FAIL'
            return evidence
        try:
            os.setuid(0)
        except OSError as error:
            evidence['errno'] = error.errno
        evidence['after'] = identity()
        if evidence['after'] != evidence['before'] or not unprivileged(evidence['after']):
            evidence['status'] = 'FAIL'
        elif evidence['errno'] in (errno.EPERM, errno.EACCES, errno.EINVAL):
            # EINVAL is expected only when UID 0 is unmapped in this namespace.
            if evidence['errno'] != errno.EINVAL or evidence['after']['parent_uid_mapping']['0'] is None:
                evidence['status'] = 'DENIED'
    except (OSError, ValueError, AttributeError):
        pass  # Missing identity/mapping evidence is never a passing denial.
    return evidence


def main():
    results = {}
    for name, path in {
        'unrelated_repository': '/home/toluadmin/services/symphony/README.md',
        'protected_credentials': '/home/toluadmin/.config/symphony/agoge.env',
        'codex_credentials': '/home/toluadmin/.codex/auth.json',
    }.items():
        try:
            descriptor = os.open(path, os.O_RDONLY)
        except OSError:
            results[name] = 'DENIED'
        else:
            os.close(descriptor)
            results[name] = 'FAIL: open succeeded; no bytes read'
    root = root_probe()
    results['root'] = root['status']
    try:
        sock = socket.socket()
        sock.settimeout(0.2)
        sock.connect(('192.0.2.1', 443))
    except PermissionError:
        results['direct_network'] = 'DENIED'
    except OSError as error:
        # A managed network namespace has only loopback, with no route to host/public networks.
        routes = Path('/proc/net/route').read_text().splitlines()[1:]
        host = Path('host-netns.txt').read_text() if Path('host-netns.txt').is_file() else None
        isolated = not routes and host is not None and os.readlink('/proc/self/ns/net') != host
        results['direct_network'] = 'DENIED' if error.errno == errno.ENETUNREACH and isolated else 'UNPROVEN: errno ' + str(error.errno)
    else:
        results['direct_network'] = 'FAIL: connection succeeded'
    finally:
        if 'sock' in locals(): sock.close()
    evidence = {'version':2, 'checks':results, 'root_identity':root}
    Path('factory-containment-results.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(json.dumps(evidence, sort_keys=True))
    return 0 if all(v == 'DENIED' for v in results.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
