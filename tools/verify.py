#!/usr/bin/env python3
"""Offline integrity and privacy checks for the publication directory."""
import argparse
import ast
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import run

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-values', type=Path, help='Optional external JSON list of strings to reject; values are never printed')
    parser.add_argument('--shell-syntax', action='store_true', help='Also run Linux sh/bash syntax checks (requires those interpreters)')
    args = parser.parse_args()
    manifest = run.load_manifest()
    forbidden = json.loads(args.private_values.read_text(encoding='utf-8')) if args.private_values else []
    failures = []
    licensing = json.loads((ROOT / 'licensing.json').read_text(encoding='utf-8'))
    known_licenses = {'GPL-2.0-only', 'GPL-2.0-or-later', 'GPL-3.0-only', 'ISC', 'Apache-2.0'}
    for relative, info in licensing['files'].items():
        if not (ROOT / relative).is_file(): failures.append(f'Missing licensed file: {relative}')
        notice_path = ROOT / (relative + '.license')
        if not notice_path.is_file():
            failures.append(f'Missing license notice: {relative}')
            continue
        notice = notice_path.read_text(encoding='utf-8')
        if 'SPDX-License-Identifier: ' + info['license'] not in notice:
            failures.append(f'License notice mismatch: {relative}')
        for name in info['license'].split(' AND '):
            if name not in known_licenses or not (ROOT / 'LICENSES' / (name + '.txt')).is_file():
                failures.append(f'Missing/unknown license text: {relative}')
    templates = {p.relative_to(ROOT / 'templates').as_posix()[:-5]: p for p in (ROOT / 'templates').rglob('*.tmpl')}
    if set(templates) != set(manifest['files']):
        failures.append('Template inventory does not match manifest')
    for source, metadata in manifest['files'].items():
        path = templates.get(source)
        if path is None: continue
        raw = path.read_bytes()
        text = raw.decode('utf-8')
        if hashlib.sha256(raw).hexdigest() != metadata['sha256']:
            failures.append(f'Checksum: {source}')
        if sorted(set(run.MARKER.findall(text))) != metadata['parameters']:
            failures.append(f'Parameter list: {source}')
        if set(metadata['parameters']) - set(manifest['parameters']):
            failures.append(f'Undefined parameters: {source}')
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(part in ('.local', '.git', '__pycache__') for part in p.relative_to(ROOT).parts): continue
        rel = p.relative_to(ROOT).as_posix()
        if 'LICENSES' not in p.relative_to(ROOT).parts and p.name != 'LICENSE' and not p.name.endswith('.license') and rel not in licensing['files']:
            failures.append(f'File has no license assignment: {rel}')
        if p.suffix in ('.ppk', '.pem', '.dpapi', '.pcap', '.pcapng', '.pyc'):
            failures.append(f'Private/generated file type: {rel}')
            continue
        text = p.read_text(encoding='utf-8', errors='replace')
        if any(value and value in text for value in forbidden):
            failures.append(f'Private value found: {rel}')
        if re.search(r'lin_api_[A-Za-z0-9]{12,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ssh-(?:rsa|ed25519) [A-Za-z0-9+/=]{40,}', text):
            failures.append(f'Credential material: {rel}')
        for match in re.finditer(r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?!\d|\.\d)', text):
            literal = match[0]
            try: addr = ipaddress.IPv4Address(literal)
            except ipaddress.AddressValueError: continue
            examples = any(addr in ipaddress.IPv4Network(net) for net in ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24'))
            if literal not in ('0.0.0.0', '127.0.0.1', '255.255.255.0', '255.255.255.255') and not examples:
                failures.append(f'Literal deployment/Internet IPv4 address: {rel}')
                break
    supplied = json.loads((ROOT / 'examples/parameters.example.json').read_text(encoding='utf-8'))
    # No scripts are executed. Rendering and compilation stay completely offline.
    with tempfile.TemporaryDirectory(prefix='network-toolkit-verify-') as temp:
        rendered = run.render(manifest, manifest['files'], supplied, Path(temp) / 'rendered')
        python_count = 0
        for path in rendered.rglob('*.py'):
            python_count += 1
            try: ast.parse(path.read_text(encoding='utf-8'), filename=path.name)
            except SyntaxError: failures.append(f'Python template syntax: {path.relative_to(rendered).as_posix()}')
        shell_count = 0
        if args.shell_syntax:
            for base in (rendered, ROOT / 'scripts'):
                for path in base.rglob('*'):
                    if not path.is_file(): continue
                    if path.suffix not in ('.sh', '.init', '.instrumented') and path.name not in ('omr-tracker-server', '010-services'): continue
                    shell_count += 1
                    first = path.read_text(encoding='utf-8').splitlines()[0]
                    shell = 'bash' if 'bash' in first or 'omr-tracker' in path.name else 'sh'
                    result = subprocess.run([shell, '-n', str(path)], capture_output=True)
                    if result.returncode: failures.append(f'Shell syntax: {path.name}')
    for path in (ROOT / 'scripts').rglob('*.py'):
        try: ast.parse(path.read_text(encoding='utf-8'))
        except SyntaxError: failures.append(f'Python syntax: {path.relative_to(ROOT).as_posix()}')
    if failures:
        print('\n'.join(sorted(set(failures))), file=sys.stderr)
        return 1
    print(f'PASS: {len(templates)} template checksums, parameter inventory, {python_count} Python templates, {len(licensing["files"])} license assignments and publication privacy checks. No network operations performed.')
    if args.shell_syntax: print(f'PASS: {shell_count} shell syntax checks.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
