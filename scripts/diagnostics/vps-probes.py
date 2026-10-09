#!/usr/bin/env python3
"""Bounded, interface-bound probes; every result is retained. No service changes."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import time

def probe(target, interface=None):
    command = ['ping', '-n', '-c', '1', '-W', '1']
    if interface:
        command += ['-I', interface]
    command.append(target)
    start = time.monotonic()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        return {'status': 'local_process_timeout', 'exit': None, 'elapsed_ms': round((time.monotonic()-start)*1000, 3), 'error': str(exc)}
    match = re.search(r'time([=<])([0-9.]+)\s*ms', stdout)
    return {'status': 'reply' if code == 0 else ('no_reply' if code == 1 else 'local_error'),
            'exit': code, 'rtt_ms': float(match[2]) if match else None,
            'rtt_bound': match[1] if match else None,
            'elapsed_ms': round((time.monotonic()-start)*1000, 3),
            'stdout': stdout, 'stderr': stderr}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', required=True, help='Confirmed current router tunnel IP; no stale default')
    parser.add_argument('--interface', required=True)
    parser.add_argument('--internet-target', required=True)
    parser.add_argument('--samples', type=int, default=30)
    parser.add_argument('--interval', type=float, default=2)
    parser.add_argument('--duration-seconds', type=int, default=0, help='Optional overall time limit')
    parser.add_argument('--log-root', default='./vps-probes')
    args = parser.parse_args()
    if args.samples < 1 or args.interval < 0:
        parser.error('samples must be positive and interval nonnegative')
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = Path(args.log_root) / (stamp + '-' + str(os.getpid()))
    out.mkdir(parents=True, mode=0o700, exist_ok=False)
    begin = datetime.datetime.now(datetime.timezone.utc).isoformat()
    meta = dict(vars(args), started_utc=begin, session_target=args.target)
    (out/'session.json').write_text(json.dumps(meta, indent=2))
    route = subprocess.run(['ip', 'route', 'get', args.target, 'oif', args.interface], capture_output=True, text=True)
    (out/'route.json').write_text(json.dumps({'exit': route.returncode, 'stdout': route.stdout, 'stderr': route.stderr}))
    counts = {path: {'reply': 0, 'no_reply': 0, 'local_error': 0, 'local_process_timeout': 0} for path in ('internet', 'tunnel')}
    previous = None
    deadline = time.monotonic()+args.duration_seconds if args.duration_seconds else None
    try:
        with (out/'probes.jsonl').open('w', buffering=1) as log:
            for sequence in range(1, args.samples+1):
                if deadline is not None and time.monotonic() >= deadline:
                    break
                state_path = Path('/sys/class/net') / args.interface / 'operstate'
                state = state_path.read_text().strip() if state_path.exists() else 'missing'
                if state != previous:
                    log.write(json.dumps({'event': 'interface_state', 'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'state': state, 'interface': args.interface})+'\n')
                    previous = state
                for path, target, interface in [('internet', args.internet_target, None), ('tunnel', args.target, args.interface)]:
                    row = dict(probe(target, interface), path=path, target=target, interface=interface, sequence=sequence,
                               time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
                    counts[path][row['status']] += 1
                    log.write(json.dumps(row)+'\n')
                if sequence < args.samples:
                    time.sleep(args.interval)
    finally:
        summary = {'started_utc': begin, 'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'counts': counts,
                   'note': 'no_reply is missing ICMP response, not proof of tunnel failure; local errors excluded from ICMP loss denominator'}
        (out/'summary.json').write_text(json.dumps(summary, indent=2))
        journal = subprocess.run(['journalctl', '-u', 'mqvpn', '--since', begin, '--no-pager', '-o', 'short-iso-precise'], capture_output=True, text=True)
        (out/'mqvpn-journal.log').write_text(journal.stdout+journal.stderr)
        print(json.dumps({'directory': str(out), **summary}))

if __name__ == '__main__':
    main()
