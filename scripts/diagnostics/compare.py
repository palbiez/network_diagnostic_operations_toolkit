"""Correlate timestamped ping observations with firewall/DNS events, not causation."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from collections import Counter
from bisect import bisect_left,bisect_right
import tarfile,re,json,hashlib,csv,io
from zoneinfo import ZoneInfo
BERLIN=ZoneInfo("Europe/Berlin")
def compare(archive,output):
 probes={};events=[];snapshots=[];snapshot_data={};config_events=[]
 with tarfile.open(archive) as t:
  for member in t:
   if not member.isfile():continue
   name=Path(member.name).name
   if '/snapshots/' in member.name and '.partial/' not in member.name:
    key=str(Path(member.name).parent)
    state=snapshot_data.setdefault(key,{'path':key,'config_hashes':{},'pids':{},'dns_config_hashes':{}})
    if name in ['time.txt','config-hashes.txt','services.json','fw4-print.nft','uci-changes.txt'] or name.startswith('dnsmasq.conf'):
     body=t.extractfile(member).read()
     if name=='time.txt':
      state['epoch']=datetime.fromisoformat(body.decode().strip()).timestamp()
     elif name=='config-hashes.txt':
      for line in body.decode().splitlines():
       parts=line.split()
       if len(parts)==2:state['config_hashes'][Path(parts[1]).name]=parts[0]
     elif name=='services.json':
      try:
       services=json.loads(body)
       state['pids']={k:{i:v.get('pid') for i,v in s.get('instances',{}).items()} for k,s in services.items() if k in ['dnsmasq','unbound','omr-tracker','shadowsocks-rust','mqvpn']}
      except (ValueError,TypeError):pass
     elif name=='fw4-print.nft':state['fw4_print_sha256']=hashlib.sha256(body).hexdigest()
     elif name=='uci-changes.txt':state['uci_pending_line_count']=len(body.splitlines())
     else:state['dns_config_hashes'][name]=hashlib.sha256(body).hexdigest()
   if name=='config-hashes.csv':
    for row in csv.DictReader(io.StringIO(t.extractfile(member).read().decode())):
     try:config_events.append({**row,'epoch':datetime.fromisoformat(row['utc'].replace('Z','+00:00')).timestamp()})
     except (ValueError,KeyError):pass
   elif name.startswith('ping-') and name.endswith('.log'):
    times=[];rtts=[];response_seqs=set();late=[];mobile_failures=[];maxseq=0;summary=None;session=0
    for raw in t.extractfile(member):
     line=raw.decode(errors='replace')
     if line.startswith('SESSION_START '):session+=1
     m=re.search(r'\[(\d+\.\d+)\].*icmp_seq[= ](\d+).*time[=<]([0-9.]+)',line)
     if m:
      ts,seq,rtt=float(m[1]),int(m[2]),float(m[3]);times.append(ts);rtts.append(rtt);response_seqs.add((session,seq));maxseq=max(maxseq,seq)
     m=re.search(r'\[(\d+\.\d+)\].*no answer yet for icmp_seq=(\d+)',line)
     if m:late.append((float(m[1]),(session,int(m[2]))))
     m=re.search(r'(\d+) packets transmitted, (\d+) received',line)
     if m:
      if summary is None:summary={'transmitted':0,'received':0}
      summary['transmitted']+=int(m[1]);summary['received']+=int(m[2])
     m=re.search(r'result_utc=(\S+) rc=(\d+)',line)
     if m and m[2]!='0':mobile_failures.append(datetime.fromisoformat(m[1].replace('Z','+00:00')).timestamp())
    pending=[ts for ts,seq in late if seq not in response_seqs]+mobile_failures
    probes[name]={'reply_timestamps':times,'rtts':rtts,'unanswered_timestamps':pending,'summary':summary,'recorded_session_starts':session,'max_observed_sequence':maxseq,'responses':len(times),'max_rtt_ms':max(rtts,default=None),'timeouts_without_later_reply':len(pending),'max_reply_gap_s':max([b-a for a,b in zip(times,times[1:])] or [0])}
   elif '/logs/services-' in member.name:
    for raw in t.extractfile(member):
     line=raw.decode(errors='replace').strip()
     if not re.search(r'Firewall reload|dnsmasq.*(?:exiting on receipt|started, version)|Firewall bypass rules regenerated|Restart OMR-ByPass',line):continue
     m=re.match(r'\w{3} (\w{3})\s+(\d+) (\d\d:\d\d:\d\d) (\d{4})',line)
     if not m:continue
     dt=datetime.strptime(f'{m[4]} {m[1]} {m[2]} {m[3]}','%Y %b %d %H:%M:%S').replace(tzinfo=BERLIN)
     events.append({'utc':dt.astimezone(timezone.utc).isoformat(),'epoch':dt.timestamp(),'message':line})
   elif name in ['fw4-check.exit','fw4-print.exit','dns-local-test.exit'] and '.partial/' not in member.name:
    snapshots.append({'file':member.name,'exit_code':t.extractfile(member).read().decode().strip()})
 states=sorted([s for s in snapshot_data.values() if 'epoch' in s],key=lambda s:s['epoch'])
 previous=None
 for state in states:
  state['changed_config_packages_since_previous']=[k for k,v in state['config_hashes'].items() if previous and previous['config_hashes'].get(k)!=v]
  state['changed_service_pids_since_previous']=[k for k,v in state['pids'].items() if previous and previous['pids'].get(k)!=v]
  state['fw4_print_changed_since_previous']=bool(previous and previous.get('fw4_print_sha256')!=state.get('fw4_print_sha256'))
  previous=state
 event_rows=[]
 for event in events:
  window={}
  for name,p in probes.items():
   lo,hi=event['epoch']-15,event['epoch']+15
   i,j=bisect_left(p['reply_timestamps'],lo),bisect_right(p['reply_timestamps'],hi)
   times=p['reply_timestamps'][i:j];rtt=p['rtts'][i:j]
   window[name]={'replies':j-i,'max_rtt_ms':max(rtt,default=None),'unanswered_without_later_reply':sum(lo<=ts<=hi for ts in p['unanswered_timestamps']),'max_reply_gap_s':max([b-a for a,b in zip(times,times[1:])] or [0])}
  nearest=min(states,key=lambda s:abs(s['epoch']-event['epoch'])) if states else None
  event_rows.append({**event,'window_seconds_each_side':15,'probes':window,'config_events':[c for c in config_events if abs(c['epoch']-event['epoch'])<=15],'nearest_snapshot_within_60s':nearest if nearest and abs(nearest['epoch']-event['epoch'])<=60 else None})
 summary={k:{n:v for n,v in p.items() if n not in ['reply_timestamps','rtts','unanswered_timestamps']} for k,p in probes.items()}
 result={'archive':str(archive),'generated_utc':datetime.now(timezone.utc).isoformat(),'limitations':['Temporal correlation does not prove causation','No response from a mobile or ICMP-blocking client does not prove network loss','Unanswered ping is counted only if no later reply for that sequence exists in this snapshot','Archive can be a partial live collection; no final transmitted count until process exit','Default event window is15 seconds each side'],'probes':summary,'events':event_rows,'snapshot_states':states,'snapshot_check_failures':[x for x in snapshots if x['exit_code']!='0'],'snapshot_check_count':len(snapshots)}
 Path(output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return result
if __name__=='__main__':
 import sys
 r=compare(sys.argv[1],sys.argv[2]);print(json.dumps({'probes':len(r['probes']),'events':len(r['events']),'failed_checks':len(r['snapshot_check_failures'])}))
