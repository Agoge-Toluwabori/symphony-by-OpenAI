"""Pinned tools and credential-free dependency staging; app commands stay sandboxed."""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
import control

def read_request(workspace,name):
    p=workspace/name
    if p.is_symlink() or not p.is_file() or p.stat().st_size>8192:raise ValueError('Invalid request file')
    return json.loads(p.read_text())

def prepare(c,workspace,modules=True):
    runtime=workspace/'.factory-runtime';binary=runtime/'bin';binary.mkdir(parents=True,exist_ok=True)
    for name in ('node','pnpm'):
        shutil.copy2(c[name],binary/name)
    if modules:
        src=Path(c['runtime_source'])/'node_modules'
        if not src.is_dir():raise ValueError('Existing dependency foundation absent')
        shutil.copytree(src,workspace/'node_modules',symlinks=True,dirs_exist_ok=True)
        original=Path(c['runtime_source'])
        for group in ('apps','packages'):
            for modules_path in (original/group).glob('*/node_modules'):
                shutil.copytree(modules_path,workspace/modules_path.relative_to(original),symlinks=True,dirs_exist_ok=True)
        store=original/'.tools/pnpm-store'
        if store.exists():shutil.copytree(store,workspace/'.tools/pnpm-store',symlinks=True,dirs_exist_ok=True)
        for name in ('.modules.yaml','.package-map.json','.pnpm-workspace-state-v1.json'):
            metadata=workspace/'node_modules'/name
            if metadata.is_file():metadata.write_text(metadata.read_text().replace(str(original),str(workspace)))

    env='export PATH='+shlex.quote(str(binary))+':/usr/bin:/bin\nexport PLAYWRIGHT_BROWSERS_PATH='+shlex.quote(c['browser_cache'])+'\n'
    (runtime/'tmp').mkdir(exist_ok=True)
    env+='export npm_config_store_dir='+shlex.quote(str(workspace/'.tools/pnpm-store'))+'\n'
    env+='export TMPDIR='+shlex.quote(str(runtime/'tmp'))+'\nexport NEXT_TELEMETRY_DISABLED=1\nexport NO_PROXY=127.0.0.1,localhost,::1\nexport no_proxy=127.0.0.1,localhost,::1\n'
    (runtime/'env.sh').write_text(env)
    (runtime/'README.md').write_text('Source .factory-runtime/env.sh before node/pnpm checks. Tools are pinned. No credentials or provider access. Full CI: pnpm check:ci.\n')
    exclude=workspace/'.git/info/exclude'
    exclude.parent.mkdir(parents=True,exist_ok=True)
    with exclude.open('a') as f:f.write('\n.factory-runtime/\n.factory-delivery.json\n.factory-blocker.json\n.factory-dependencies*.json\n')

def manifests_safe(manifests):
    for name,d in manifests.items():
        if not re.fullmatch(r'(?:package.json|(?:apps|packages)/[\w-]+/package.json)',name):return False
        for group in ('dependencies','devDependencies','optionalDependencies','peerDependencies'):
            for pkg,version in d.get(group,{}).items():
                if not re.fullmatch(r'(?:@[a-z0-9_.-]+/)?[a-z0-9_.-]+',pkg):return False
                if not isinstance(version,str) or not re.fullmatch(r'(?:workspace:)?[0-9xX*.^~|<>=+ -]+',version):return False
        if any(k in d for k in ('pnpm','resolutions','overrides')):return False
    return True

def dependencies(c,workspace,state):
    request=read_request(workspace,'.factory-dependencies.json')
    if request!={'requested':True}:raise ValueError('Invalid dependency request')
    names=control.command(['git','-C',str(workspace),'ls-files','*package.json']).splitlines()
    manifests={}
    for name in names:
        p=workspace/name
        if p.is_symlink() or not p.resolve().is_relative_to(workspace.resolve()):raise ValueError('Manifest escaped workspace')
        if re.fullmatch(r'(?:package.json|(?:apps|packages)/[\w-]+/package.json)',name):manifests[name]=json.loads(p.read_text())
    if not manifests_safe(manifests):raise ValueError('Only zero-cost npm registry semver/workspace dependencies permitted')
    with tempfile.TemporaryDirectory(dir=state,prefix='dependencies-') as directory:
        root=Path(directory)
        for name,data in manifests.items():
            clean={k:v for k,v in data.items() if k in ('name','version','private','dependencies','devDependencies','optionalDependencies','peerDependencies')}
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(clean))
        (root/'pnpm-workspace.yaml').write_text('packages:\n  - apps/*\n  - packages/*\n')
        # No worker config, hooks, lifecycle scripts, GitHub token or host HOME.
        # Only pinned pnpm resolves semver names through the fixed npm registry.
        from registry_proxy import serving
        with serving() as proxy:
            args=['/usr/bin/bwrap','--unshare-user','--unshare-pid','--unshare-ipc','--unshare-uts',
                  '--cap-drop','ALL','--die-with-parent','--new-session',
                  '--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib',
                  '--symlink','usr/lib64','/lib64','--ro-bind','/etc/ssl/certs','/etc/ssl/certs',
                  '--ro-bind','/etc/resolv.conf','/etc/resolv.conf','--proc','/proc','--dev','/dev',
                  '--tmpfs','/tmp','--bind',str(root),'/work','--dir','/tools',
                  '--ro-bind',c['node'],'/tools/node','--ro-bind',c['pnpm'],'/tools/pnpm',
                  '--ro-bind','/usr/bin/false','/usr/bin/git','--ro-bind','/usr/bin/false','/usr/bin/ssh',
                  '--clearenv','--setenv','HOME','/work','--setenv','PATH','/tools:/usr/bin:/bin',
                  '--setenv','CI','true','--setenv','HTTPS_PROXY',proxy,'--setenv','HTTP_PROXY',proxy,
                  '--setenv','npm_config_https_proxy',proxy,'--setenv','npm_config_registry','https://registry.npmjs.org',
                  '--chdir','/work','/tools/pnpm','install','--ignore-scripts','--ignore-pnpmfile','--registry=https://registry.npmjs.org']
            control.command(args,timeout=600)
        lock=(root/'pnpm-lock.yaml').read_text()
        if re.search(r'https?://(?!registry\.npmjs\.org/)',lock):raise ValueError('Non-registry dependency resolution rejected')
        shutil.copy2(root/'pnpm-lock.yaml',workspace/'pnpm-lock.yaml')
        shutil.copytree(root/'node_modules',workspace/'node_modules',symlinks=True,dirs_exist_ok=True)
        for name in manifests:
            if name!='package.json' and (root/Path(name).parent/'node_modules').exists():
                shutil.copytree(root/Path(name).parent/'node_modules',workspace/Path(name).parent/'node_modules',symlinks=True,dirs_exist_ok=True)
        store=root/'.local/share/pnpm/store'
        if store.exists():shutil.copytree(store,workspace/'.tools/pnpm-store',symlinks=True,dirs_exist_ok=True)
        for name in ('.modules.yaml','.package-map.json','.pnpm-workspace-state-v1.json'):
            metadata=workspace/'node_modules'/name
            if metadata.exists():metadata.write_text(metadata.read_text().replace('/work/.local/share/pnpm/store',str(workspace/'.tools/pnpm-store')).replace('/work',str(workspace)))

    (workspace/'.factory-dependencies.json').unlink()
    control.write(workspace/'.factory-dependencies-result.json',{'status':'ready','scripts_executed':False})
