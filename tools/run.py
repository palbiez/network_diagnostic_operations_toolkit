#!/usr/bin/env python3
"""Inspect, render and run sanitized source templates with explicit runtime values."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
MARKER = re.compile(r'@@([A-Z][A-Z0-9_]*_\d+)@@')

def load_manifest():
    return json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))

def select(manifest, scopes):
    selected = {}
    for scope in scopes:
        scope = scope.replace('\\', '/').rstrip('/')
        matches = {k: v for k, v in manifest['files'].items()
                   if k == scope or k.startswith(scope + '/')}
        if not matches:
            raise ValueError(f'Unknown source or directory: {scope}')
        selected.update(matches)
    return selected

def validate(name, value, metadata):
    kind = metadata['type']
    if not isinstance(value, (str, int)) or isinstance(value, bool):
        raise ValueError(f'{name}: use a string or integer')
    value = str(value)
    if MARKER.search(value):
        raise ValueError(f'{name}: nested template markers are not allowed')
    if kind == 'ipv4':
        ipaddress.IPv4Address(value)
    elif kind == 'mac' and not re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', value):
        raise ValueError(f'{name}: expected a MAC address')
    elif kind == 'vlan' and (not value.isdigit() or not 1 <= int(value) <= 4094):
        raise ValueError(f'{name}: expected a VLAN ID in 1..4094')
    elif kind == 'epoch' and (not value.isdigit() or int(value) <= 0):
        raise ValueError(f'{name}: expected positive Unix seconds')
    elif kind in ('interface', 'section') and not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]*', value):
        raise ValueError(f'{name}: invalid interface/section name')
    elif kind == 'hostname' and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*', value):
        raise ValueError(f'{name}: invalid hostname')
    elif kind == 'identifier':
        uuid.UUID(value)
    if kind == 'python_string':
        return repr(value)
    # Inline values appear in source code. Reject quote/control characters rather
    # than silently producing broken quoting or introducing executable commands.
    if any(c in value for c in ('\n', '\r', '\x00', '"', "'", '`', '$', ';', '&', '|', '<', '>')):
        raise ValueError(f'{name}: unsafe inline character; use a native runtime argument or external credential file')
    return value

def render(manifest, selected, supplied, output):
    needed = sorted({p for info in selected.values() for p in info['parameters']})
    missing = [p for p in needed if p not in supplied]
    if missing:
        raise ValueError('Missing runtime values: ' + ', '.join(missing) + '. Run inspect for details.')
    unknown = set(supplied) - set(manifest['parameters'])
    if unknown:
        raise ValueError('Unknown parameters: ' + ', '.join(sorted(unknown)))
    replacements = {p: validate(p, supplied[p], manifest['parameters'][p]) for p in needed}
    result = {}
    for source, info in selected.items():
        template = ROOT / 'templates' / (source + '.tmpl')
        data = template.read_bytes()
        if hashlib.sha256(data).hexdigest() != info['sha256']:
            raise ValueError(f'Template checksum mismatch: {source}')
        text = data.decode('utf-8')
        if set(MARKER.findall(text)) != set(info['parameters']):
            raise ValueError(f'Parameter manifest mismatch: {source}')
        result[source] = MARKER.sub(lambda m: replacements[m[1]], text)
    output = output.resolve()
    # A new directory keeps existing files and the public sources intact.
    if output.exists():
        raise ValueError('Output directory already exists; choose a new directory')
    public = ROOT.resolve()
    if output == public or (public in output.parents and public / '.local' not in output.parents):
        raise ValueError('Inside the repository, use a new directory below .local/')
    output.mkdir(parents=True, mode=0o700)
    for source, text in result.items():
        target = (output / source).resolve()
        if output not in target.parents:
            raise ValueError('Source path leaves the output directory')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8', newline='\n')
        target.chmod(0o600)
        notice_source = ROOT / 'templates' / (source + '.tmpl.license')
        if notice_source.is_file():
            notice_target = target.with_name(target.name + '.license')
            notice_target.write_bytes(notice_source.read_bytes())
            notice_target.chmod(0o600)
    return output

def interpreter(path):
    if path.suffix == '.py':
        return [sys.executable, str(path)]
    if path.suffix == '.ps1':
        return ['powershell.exe' if os.name == 'nt' else 'pwsh', '-NoProfile', '-File', str(path)]
    if path.suffix in ('.nft', '.patch', '.service', '.json', '.sha256') or path.name == 'settings':
        raise ValueError('This is a support file. Use render, then review and install it manually.')
    first_line = path.read_text(encoding='utf-8').splitlines()[0]
    shell = 'bash' if 'bash' in first_line or path.name == 'omr-tracker-server' else 'sh'
    return [shell, str(path)]

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('list', 'inspect', 'render', 'run'))
    parser.add_argument('source', nargs='?', help='Catalog path or directory (run requires one file)')
    parser.add_argument('--include', action='append', default=[], help='Additional helper file or directory')
    parser.add_argument('--config', type=Path, help='Private JSON object mapping parameter names to values')
    parser.add_argument('--set', action='append', default=[], metavar='NAME=VALUE')
    parser.add_argument('--output', type=Path, help='New private output directory')
    actual = sys.argv[1:] if argv is None else argv
    separator = actual.index('--') if '--' in actual else len(actual)
    args = parser.parse_args(actual[:separator])
    native = actual[separator+1:]
    manifest = load_manifest()
    try:
        if args.action == 'list':
            print('\n'.join(manifest['files']))
            return 0
        if not args.source:
            raise ValueError('Provide a source path from the catalog')
        selected = select(manifest, [args.source] + args.include)
        if args.action == 'inspect':
            needed = sorted({p for info in selected.values() for p in info['parameters']})
            details = {}
            for name in needed:
                usage = []
                for source, info in selected.items():
                    if name not in info['parameters']: continue
                    lines = (ROOT / 'templates' / (source + '.tmpl')).read_text(encoding='utf-8').splitlines()
                    for number, line in enumerate(lines, 1):
                        if '@@' + name + '@@' in line:
                            usage.append({'source': source, 'line': number, 'context': line.strip()[:180]})
                            break
                details[name] = dict(manifest['parameters'][name], used_in=usage)
            print(json.dumps(details, indent=2))
            return 0
        supplied = json.loads(args.config.read_text(encoding='utf-8')) if args.config else {}
        if not isinstance(supplied, dict):
            raise ValueError('Configuration must be a JSON object')
        for item in args.set:
            key, separator, value = item.partition('=')
            if not separator:
                raise ValueError('--set requires NAME=VALUE')
            supplied[key] = value
        if args.action == 'run' and args.source not in manifest['files']:
            raise ValueError('run requires one source file, not a directory')
        output = args.output or ROOT / '.local' / ('rendered-' + uuid.uuid4().hex)
        directory = render(manifest, selected, supplied, output)
        print(f'Rendered {len(selected)} files to {directory}', flush=True)
        if args.action == 'run':
            return subprocess.call(interpreter(directory / args.source) + native, cwd=directory)
        return 0
    except (ValueError, OSError, KeyError) as error:
        # Never echo supplied config values, which may include private material.
        message = str(error) if not isinstance(error, ipaddress.AddressValueError) else 'Invalid IPv4 parameter'
        print(message, file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
