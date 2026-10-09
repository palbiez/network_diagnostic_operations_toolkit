#!/bin/sh
# Finite read-only network diagnosis. No UCI/service/routing changes.
set -eu
umask 077
WAN1_INTERFACE=${WAN1_INTERFACE:?Supply WAN1_INTERFACE}
WAN2_INTERFACE=${WAN2_INTERFACE:?Supply WAN2_INTERFACE}
TUNNEL_INTERFACE=${TUNNEL_INTERFACE:?Supply TUNNEL_INTERFACE}
WAN1_GATEWAY=${WAN1_GATEWAY:?Supply WAN1_GATEWAY}
WAN2_GATEWAY=${WAN2_GATEWAY:?Supply WAN2_GATEWAY}
INTERNET_TARGET1=${INTERNET_TARGET1:?Supply INTERNET_TARGET1}
INTERNET_TARGET2=${INTERNET_TARGET2:?Supply INTERNET_TARGET2}
DURATION=${DURATION:-3600}
SNAPSHOT_INTERVAL=${SNAPSHOT_INTERVAL:-60}
PING_INTERVAL=${PING_INTERVAL:-0.2}
MAX_KB=${MAX_KB:-65536}
CLIENT_IP=${CLIENT_IP:-}
CITRIX_IP=${CITRIX_IP:-}
CITRIX_ICMP=${CITRIX_ICMP:-1}
case "$CITRIX_ICMP" in 0|1) ;; *) echo 'CITRIX_ICMP must be 0 or 1'; exit 2;; esac
VPS_IP=${VPS_IP:?Supply VPS_IP}
TUNNEL_PEER=${TUNNEL_PEER:?Supply TUNNEL_PEER}
for interface in "$WAN1_INTERFACE" "$WAN2_INTERFACE" "$TUNNEL_INTERFACE"; do
 case "$interface" in ''|*[!a-zA-Z0-9_.-]*) echo 'Invalid interface'; exit 2;; esac
done
for number in "$DURATION" "$SNAPSHOT_INTERVAL" "$MAX_KB"; do
 case "$number" in ''|*[!0-9]*) echo 'Duration, snapshot interval and limit must be integers' >&2; exit 2;; esac
done
[ "$DURATION" -ge 5 ] && [ "$DURATION" -le 86400 ] || exit 2
[ "$SNAPSHOT_INTERVAL" -ge 10 ] && [ "$MAX_KB" -ge 1024 ] || exit 2
case "$PING_INTERVAL" in 0.1|0.2|0.5|1) ;; *) echo 'PING_INTERVAL: use 0.1, 0.2, 0.5 or 1'; exit 2;; esac
for addr in "$CLIENT_IP" "$CITRIX_IP" "$VPS_IP" "$TUNNEL_PEER" "$WAN1_GATEWAY" "$WAN2_GATEWAY" "$INTERNET_TARGET1" "$INTERNET_TARGET2"; do
 case "$addr" in *[!0-9.]*|.*|-*) echo 'Targets must be IPv4 addresses'; exit 2;; esac
done
OUT_DIR=${OUT_DIR:-/tmp/phi12-$(date -u +%Y%m%dT%H%M%SZ)-$$}
case "$OUT_DIR" in /tmp/phi12-*) ;; *) echo 'OUT_DIR must start with /tmp/phi12-'; exit 2;; esac
case "${OUT_DIR#/tmp/}" in */*) echo 'OUT_DIR must be one directory directly below /tmp'; exit 2;; esac
[ ! -e "$OUT_DIR" ] || { echo 'Use a new OUT_DIR'; exit 2; }
mkdir -p "$OUT_DIR/snapshots"
pids=''
start=$(date +%s)
stop_reason=duration
printf 'utc,event,detail\n' > "$OUT_DIR/events.csv"
printf 'utc,interface,carrier,carrier_changes,rx_packets,tx_packets,rx_errors,tx_errors,rx_dropped,tx_dropped\n' > "$OUT_DIR/nic.csv"
printf 'label,interface,target,route_check_exit\n' > "$OUT_DIR/probes.csv"
printf 'duration=%s\nping_interval=%s\nmax_kb=%s\nclient=%s\ncitrix=%s\n' "$DURATION" "$PING_INTERVAL" "$MAX_KB" "$CLIENT_IP" "$CITRIX_IP" > "$OUT_DIR/run-settings.txt"
echo "STARTED: $OUT_DIR"
echo "Mark an outage from another SSH session: touch $OUT_DIR/trigger"
echo "Stop cleanly: touch $OUT_DIR/stop"

utc() { date -u +%Y-%m-%dT%H:%M:%SZ; }
event() { printf '%s,%s,%s\n' "$(utc)" "$1" "$2" >> "$OUT_DIR/events.csv"; }
snapshot_count=0
snapshot() {
 snapshot_count=$((snapshot_count + 1))
 dir="$OUT_DIR/snapshots/$(printf '%04d' "$snapshot_count")-$1"
 mkdir -p "$dir"
 utc > "$dir/time-utc.txt"
 ip -details addr > "$dir/addresses.txt" 2>&1 || true
 ip -s link > "$dir/links.txt" 2>&1 || true
 ip rule > "$dir/rules.txt" 2>&1 || true
 ip route show table all > "$dir/routes.txt" 2>&1 || true
 ip neigh > "$dir/neighbours.txt" 2>&1 || true
 if [ -n "$CLIENT_IP" ] && command -v conntrack >/dev/null 2>&1; then
  conntrack -L -s "$CLIENT_IP" > "$dir/client-conntrack.txt" 2>&1 || true
 fi
 nft list ruleset > "$dir/nft-ruleset.txt" 2>&1 || true
 logread -l 200 > "$dir/local-syslog.txt" 2>&1 || true
 for service in mqvpn shadowsocks-rust log; do
  ubus call service list "{\"name\":\"$service\"}" > "$dir/$service-service.json" 2>&1 || true
 done
 for dev in "${WAN1_INTERFACE}" "${WAN2_INTERFACE}"; do
  ethtool -S "$dev" > "$dir/$dev-ethtool-stats.txt" 2>&1 || true
 done
 if [ -n "$CITRIX_IP" ]; then
  ip route get "$CITRIX_IP" > "$dir/citrix-route-router.txt" 2>&1 || true
  if [ -n "$CLIENT_IP" ]; then
   lan_dev=$(ip route get "$CLIENT_IP" 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="dev") {print $(i+1);exit}}')
   if [ -n "$lan_dev" ]; then
    for mark in 0 0x45392 0x45393 0x45391500; do
     ip route get "$CITRIX_IP" from "$CLIENT_IP" iif "$lan_dev" mark "$mark" > "$dir/client-route-$mark.txt" 2>&1 || true
    done
   fi
  fi
 fi
 event snapshot "$1-$snapshot_count"
}
probe() {
 label=$1; dev=$2; target=$3
 rc=0
 if [ -n "$dev" ]; then
  ip route get "$target" oif "$dev" > "$OUT_DIR/route-$label.txt" 2>&1 || rc=$?
 else
  ip route get "$target" > "$OUT_DIR/route-$label.txt" 2>&1 || rc=$?
 fi
 printf '%s,%s,%s,%s\n' "$label" "$dev" "$target" "$rc" >> "$OUT_DIR/probes.csv"
 if [ "$rc" -ne 0 ]; then
  event probe_route_error "$label"
  return
 fi
 if [ -n "$dev" ]; then
  ping -n -D -O -I "$dev" -i "$PING_INTERVAL" -W 1 -w "$DURATION" "$target" > "$OUT_DIR/ping-$label.log" 2>&1 &
 else
  ping -n -D -O -i "$PING_INTERVAL" -W 1 -w "$DURATION" "$target" > "$OUT_DIR/ping-$label.log" 2>&1 &
 fi
 pids="$pids $!"
}
cleanup() {
 trap - EXIT INT TERM HUP
 for pid in $pids; do kill -INT "$pid" 2>/dev/null || true; done
 sleep 1
 for pid in $pids; do kill -TERM "$pid" 2>/dev/null || true; done
 for pid in $pids; do wait "$pid" 2>/dev/null || true; done
 event stopped "$stop_reason"
 echo "STOPPED: $OUT_DIR ($stop_reason)"
}
trap cleanup EXIT
trap 'stop_reason=signal; exit 0' INT TERM HUP
event started read_only
snapshot before
ip monitor link address route > "$OUT_DIR/ip-monitor.log" 2>&1 &
pids="$pids $!"
probe wan1_gateway "${WAN1_INTERFACE}" "${WAN1_GATEWAY}"
probe wan2_gateway "${WAN2_INTERFACE}" "${WAN2_GATEWAY}"
probe wan1_internet1 "${WAN1_INTERFACE}" "${INTERNET_TARGET1}"
probe wan2_internet1 "${WAN2_INTERFACE}" "${INTERNET_TARGET1}"
probe wan1_internet2 "${WAN1_INTERFACE}" "${INTERNET_TARGET2}"
probe wan2_internet2 "${WAN2_INTERFACE}" "${INTERNET_TARGET2}"
probe wan1_vps "${WAN1_INTERFACE}" "$VPS_IP"
probe wan2_vps "${WAN2_INTERFACE}" "$VPS_IP"
probe tunnel "${TUNNEL_INTERFACE}" "$TUNNEL_PEER"
[ -z "$CLIENT_IP" ] || probe client '' "$CLIENT_IP"
if [ -n "$CITRIX_IP" ] && [ "$CITRIX_ICMP" = 1 ]; then
 probe wan1_citrix "${WAN1_INTERFACE}" "$CITRIX_IP"
 probe wan2_citrix "${WAN2_INTERFACE}" "$CITRIX_IP"
fi
last_snapshot=$(date +%s)
previous=''
while [ "$(date +%s)" -lt "$((start + DURATION))" ]; do
 if [ -e "$OUT_DIR/stop" ]; then stop_reason=stop_file; break; fi
 used=$(du -sk "$OUT_DIR" | awk '{print $1}')
 if [ "$used" -ge "$MAX_KB" ]; then stop_reason=size_limit; break; fi
 state="$(pidof mqvpn 2>/dev/null || true)|$(ip -o addr show "${TUNNEL_INTERFACE}" 2>/dev/null || true)"
 for dev in "${WAN1_INTERFACE}" "${WAN2_INTERFACE}"; do
  base=/sys/class/net/$dev
  values=''
  for field in carrier carrier_changes statistics/rx_packets statistics/tx_packets statistics/rx_errors statistics/tx_errors statistics/rx_dropped statistics/tx_dropped; do
   val=$(cat "$base/$field" 2>/dev/null || echo NA)
   values="$values,$val"
  done
  printf '%s,%s%s\n' "$(utc)" "$dev" "$values" >> "$OUT_DIR/nic.csv"
  state="$state|$(cat "$base/carrier" "$base/carrier_changes" 2>/dev/null || true)"
 done
 reason=''
 if [ -e "$OUT_DIR/trigger" ]; then reason=user_event; rm -f "$OUT_DIR/trigger"; fi
 if [ -n "$previous" ] && [ "$previous" != "$state" ]; then reason=pid_address_or_link_change; fi
 previous=$state
 now=$(date +%s)
 if [ -n "$reason" ]; then event detected "$reason"; fi
 # Rate limit full state captures; manual markers always get their timestamp.
 if { [ -n "$reason" ] && [ "$((now-last_snapshot))" -ge 5 ]; } || [ "$((now-last_snapshot))" -ge "$SNAPSHOT_INTERVAL" ]; then
  snapshot "${reason:-periodic}"
  last_snapshot=$now
 fi
 sleep 2
done
snapshot final
