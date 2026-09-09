"""Render the pinned runtime read grant and validate Codex-owned trust metadata."""
import json
from pathlib import Path
import tomllib

FACTORY = Path(__file__).resolve().parent
CODEX = Path('/home/toluadmin/.local/bin/codex')
WORKSPACES = Path('/home/toluadmin/services/symphony-workspaces/agoge-business-systems')


def render():
    executable = CODEX.resolve(strict=True)
    return (FACTORY / 'native-policy.toml').read_text().replace(
        '"@CODEX_EXECUTABLE@"', json.dumps(str(executable))).encode()


def split(data):
    config = tomllib.loads(data.decode())
    projects = config.pop('projects', {})
    for name, settings in projects.items():
        path = Path(name)
        if (path.parent != WORKSPACES or not path.name.startswith('GH-')
                or not path.name[3:].isdigit()
                or settings not in ({'trust_level': 'trusted'}, {'trust_level': 'untrusted'})):
            raise ValueError('Unexpected project trust metadata; preserve and review installed policy')
    return config, projects


def with_trust(data, projects):
    suffix = ''.join('\n[projects.' + json.dumps(name) + ']\ntrust_level = '
                     + json.dumps(settings['trust_level']) + '\n'
                     for name, settings in sorted(projects.items()))
    return data + suffix.encode()


def matches(data):
    return split(data)[0] == split(render())[0]
