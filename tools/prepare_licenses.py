#!/usr/bin/env python3
"""Maintain per-file license notices for this toolkit's independently distributed sources."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
YEAR = '2026'
OWNER = 'palbiez'
FEEDS_REV = 'e23b7e0243d90a47819d75a7b44edcc184d6486c'
OPENWRT_REV = '0ef832f34e309fd060b1eb6b9aa78e6b4c5d1c77'
MQVPN_REV = 'ee78205d3db491ca7727b974bda0c91ae1523236'

def download(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'network-toolkit-license-preparation'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode('utf-8').replace('\r\n', '\n')

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')

def split_historical_tests():
    directory = ROOT / 'templates/Skripte/Router-Fixes/PHI12-UCI-Race-20261003'
    builder = directory / 'build-tests.py.tmpl'
    text = builder.read_text(encoding='utf-8')
    if "common+functions+server_tests+'\\n'+lan_functions+lan_tests" not in text:
        return
    # Read string literals from the original template, preserving marker spelling.
    strings = {}
    for assignment in ast.parse(text).body:
        if isinstance(assignment, ast.Assign) and isinstance(assignment.value, ast.Constant):
            for target in assignment.targets:
                if isinstance(target, ast.Name) and isinstance(assignment.value.value, str):
                    strings[target.id] = assignment.value.value
    combined = (directory / 'test-functions.sh.tmpl').read_text(encoding='utf-8')
    common = strings['common']
    server_test = strings['server_tests']
    lan_test = strings['lan_tests']
    assert combined.startswith(common)
    start_server_tests = combined.index(server_test, len(common))
    start_lan_tests = combined.rindex(lan_test)
    server_functions = combined[len(common):start_server_tests]
    lan_functions = combined[start_server_tests+len(server_test):start_lan_tests].lstrip('\n')
    write(directory / 'test-server.sh.tmpl', common + server_functions + server_test)
    write(directory / 'test-scheduler.sh.tmpl', common + lan_functions + lan_test)
    wrapper = '''#!/bin/sh
# Run the separately licensed tracker and scheduler tests as independent programs.
set -eu
test_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bash "$test_dir/test-server.sh"
bash "$test_dir/test-scheduler.sh"
echo 'ALL TESTS PASSED (independent tracker and scheduler test programs)'
'''
    write(directory / 'test-functions.sh.tmpl', wrapper)
    old = "(P/'test-functions.sh').write_text(common+functions+server_tests+'\\n'+lan_functions+lan_tests, encoding='utf-8', newline='\\n')"
    replacement = """(P/'test-server.sh').write_text(common+functions+server_tests, encoding='utf-8', newline='\\n')
(P/'test-scheduler.sh').write_text(common+lan_functions+lan_tests, encoding='utf-8', newline='\\n')
(P/'test-functions.sh').write_text(""" + repr(wrapper) + ", encoding='utf-8', newline='\\n')"
    assert text.count(old) == 1
    write(builder, text.replace(old, replacement).replace('Generated isolated tests from actual patched functions.', 'Generated separate tracker and scheduler test programs.'))

def classify(source):
    own = {'license': 'GPL-2.0-or-later', 'copyright': [f'{YEAR} {OWNER}'], 'origin': 'Original toolkit source or documentation'}
    upstream = []
    if ('servertracker-upstream.sh' in source or 'omr-tracker-server' in source
        or 'omr-tracker-ss-current.sh' in source or source.endswith('/omr-tracker.instrumented')
        or source.endswith('/test-server.sh') or source.endswith('/upstream-pr335-20261006/335.patch')):
        upstream = ['Ycarus (Yannick Chabanois)', 'OVH and the OverTheBox contributors']
        own.update(license='GPL-3.0-only', origin=f'https://github.com/Ysurac/openmptcprouter-feeds/tree/{FEEDS_REV}/omr-tracker')
    elif ('010-services' in source or source.endswith('/services-upstream.sh')
          or source.endswith('/test-scheduler.sh') or source.endswith('/upstream-pr335-20261006/326.patch')):
        upstream = ['Ycarus (Yannick Chabanois)']
        own.update(license='GPL-2.0-only', origin=f'https://github.com/Ysurac/openmptcprouter-feeds/tree/{FEEDS_REV}/omr-schedule')
    elif source.endswith('/build-fix.py'):
        upstream = ['Ycarus (Yannick Chabanois)']
        own.update(license='GPL-2.0-only', origin=f'https://github.com/Ysurac/openmptcprouter-feeds/tree/{FEEDS_REV}/omr-schedule')
    elif source.endswith('/omr-bypass.instrumented') or source.endswith('/omr-dscp.patch') or source.endswith('/test-dscp-isolated.sh'):
        upstream = ['Ycarus (Yannick Chabanois)']
        package = 'omr-bypass' if 'bypass' in source else 'omr-dscp'
        own.update(license='GPL-2.0-only', origin=f'https://github.com/Ysurac/openmptcprouter-feeds/tree/{FEEDS_REV}/{package}')
    elif source.endswith('/dnsmasq.instrumented'):
        upstream = ['2007-2012 OpenWrt.org']
        own.update(license='GPL-2.0-only', origin=f'https://github.com/openwrt/openwrt/blob/{OPENWRT_REV}/package/network/services/dnsmasq/files/dnsmasq.init')
    elif source.endswith('/firewall.instrumented'):
        upstream = ['2021 Jo-Philipp Wich']
        own.update(license='ISC', origin='https://git.openwrt.org/project/firewall4.git')
    elif source.startswith('openwrt_patch/') and source.endswith('.patch'):
        upstream = ['Andrea Covelli', 'The Linux/mac80211 contributors']
        own.update(license='GPL-2.0-only', origin='https://github.com/openwrt/openwrt/pull/23181')
    elif source.endswith('/PHI14-live-mtu-check.proposed.patch'):
        upstream = ['2026 mp0rta and mqvpn contributors']
        # The patch contains Apache-licensed context. Select GPLv3 for the
        # combined derivative while retaining Apache obligations for that context.
        own.update(license='GPL-3.0-only AND Apache-2.0', origin=f'https://github.com/Ysurac/mqvpn/tree/{MQVPN_REV}')
    if source.endswith('/326.patch') or source.endswith('/335.patch'):
        upstream.append('pylaterreur (upstream pull-request author)')
    own['copyright'] = upstream + own['copyright']
    if upstream:
        own['modifications'] = 'Sanitized/parameterized source; local instrumentation or fix where present. Preparation and notices updated 2026-10-09. Original upstream notices retained.'
    return own

def main():
    licenses = ROOT / 'LICENSES'
    licenses.mkdir(exist_ok=True)
    # Keep the existing repository license text, rather than replacing its history.
    original = subprocess.run(['git', '-C', str(ROOT), 'show', 'origin/main:LICENSE'], capture_output=True, check=True).stdout.decode('utf-8')
    write(ROOT / 'LICENSE', original)
    spdx = 'https://raw.githubusercontent.com/spdx/license-list-data/main/text/'
    for name in ('GPL-2.0-only', 'GPL-2.0-or-later', 'GPL-3.0-only', 'Apache-2.0', 'ISC'):
        write(licenses / (name + '.txt'), download(spdx + name + '.txt'))
    isc_text = (licenses / 'ISC.txt').read_text(encoding='utf-8')
    write(licenses / 'firewall4-COPYRIGHT.txt', isc_text.replace('Copyright <year> <owner>', 'Copyright (C) 2021 Jo-Philipp Wich <jo@mein.io>'))
    write(licenses / 'mqvpn-NOTICE.txt', download(f'https://raw.githubusercontent.com/Ysurac/mqvpn/{MQVPN_REV}/NOTICE'))
    split_historical_tests()
    # Restore public attribution metadata and protocol identifiers accidentally
    # generalized by the earlier broad network-name sanitizer.
    for path in (ROOT / 'templates').rglob('*.tmpl'):
        text = path.read_text(encoding='utf-8')
        text = text.replace('ycarus@@@HOSTNAME_004@@', 'ycarus@zugaina.org')
        text = text.replace('andcov23@@@HOSTNAME_020@@', 'andcov23@gmail.com')
        if 'openwrt_patch' in path.parts:
            text = text.replace('RX_@@SECTION_007@@', 'RX_MGMT').replace('IEEE80211_KEY_FLAG_RX_@@SECTION_007@@', 'IEEE80211_KEY_FLAG_RX_MGMT')
        write(path, text)
    manifest_path = ROOT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['files'] = {}
    records = {}
    for path in sorted((ROOT / 'templates').rglob('*.tmpl')):
        source = path.relative_to(ROOT / 'templates').as_posix()[:-5]
        data = path.read_bytes()
        manifest['files'][source] = {'parameters': sorted(set(re.findall(r'@@([A-Z][A-Z0-9_]*_\d+)@@', data.decode('utf-8')))), 'sha256': hashlib.sha256(data).hexdigest()}
        records[path.relative_to(ROOT).as_posix()] = classify(source)
    write(manifest_path, json.dumps(manifest, indent=2) + '\n')
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(part in ('.git', '.local', '__pycache__', 'LICENSES') for part in path.relative_to(ROOT).parts): continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in records or path.name.endswith('.license') or path.name == 'LICENSE': continue
        records[rel] = classify(rel)
    records['licensing.json'] = classify('licensing.json')
    for rel, info in records.items():
        notice = '\n'.join('SPDX-FileCopyrightText: ' + author for author in info['copyright'])
        notice += '\nSPDX-License-Identifier: ' + info['license'] + '\n'
        notice += '\nSource: ' + info['origin'] + '\n'
        if 'modifications' in info: notice += 'Changes: ' + info['modifications'] + '\n'
        write(ROOT / (rel + '.license'), notice)
    write(ROOT / 'licensing.json', json.dumps({'default_license': 'GPL-2.0-or-later', 'copyright_holder': OWNER, 'files': dict(sorted(records.items()))}, indent=2) + '\n')
    catalog = ['# Source catalog', '', 'Each row is a sanitized source template. Use `tools/run.py inspect PATH` to list runtime values. Per-file license notices accompany every template.', '', '| Source | Required values | License |', '| --- | ---: | --- |']
    for rel, info in manifest['files'].items():
        license_id = records['templates/' + rel + '.tmpl']['license']
        catalog.append(f'| [{rel}](../templates/{rel}.tmpl) | {len(info["parameters"])} | {license_id} |')
    write(ROOT / 'docs/CATALOG.md', '\n'.join(catalog) + '\n')
    print(f'Prepared license notices for {len(records)} files and {len(manifest["files"])} templates.')

if __name__ == '__main__':
    main()
