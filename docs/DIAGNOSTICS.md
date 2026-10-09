# Running the main diagnostics

All network-specific values below are startup inputs. Example addresses and MACs are synthetic. No commands in this guide install a router fix.

## Router paths

`scripts/diagnostics/router-monitor.sh` collects bounded parallel ping observations, route and interface snapshots, service state and counters. It compares each WAN gateway, two external targets, the VPS and the tunnel peer. Optional client and application targets can be added.

Run directly on the router with `ip`, `ping`, `awk`, `nft`, `ubus`, `jsonfilter`, `logread` and the other OpenWrt tools used in the source:

```sh
WAN1_INTERFACE=wan_a WAN2_INTERFACE=wan_b TUNNEL_INTERFACE=vpn0 \
WAN1_GATEWAY=192.0.2.1 WAN2_GATEWAY=198.51.100.1 \
VPS_IP=203.0.113.10 TUNNEL_PEER=192.0.2.2 \
INTERNET_TARGET1=198.51.100.10 INTERNET_TARGET2=203.0.113.20 \
DURATION=300 SNAPSHOT_INTERVAL=60 MAX_KB=65536 \
sh scripts/diagnostics/router-monitor.sh
```

Supply a VLAN interface name such as `wan_a.100` through the interface parameter if that is the actual route device. No production VLAN ID is assumed.

| Input | Meaning |
| --- | --- |
| `WAN1_INTERFACE`, `WAN2_INTERFACE` | Kernel devices for the two WANs |
| `TUNNEL_INTERFACE` | Current kernel tunnel device |
| `WAN1_GATEWAY`, `WAN2_GATEWAY` | Reachable upstream gateway addresses |
| `VPS_IP`, `TUNNEL_PEER` | Current server address and router-side tunnel peer |
| `INTERNET_TARGET1`, `INTERNET_TARGET2` | Two operator-selected external targets |
| `CLIENT_IP`, `CITRIX_IP` | Optional local client and application endpoint |
| `CITRIX_ICMP` | Set to `0` if application ICMP probes should be disabled |
| `DURATION`, `SNAPSHOT_INTERVAL`, `MAX_KB` | Collection duration, snapshot frequency and storage bound |
| `PING_INTERVAL` | One of `0.1`, `0.2`, `0.5`, `1` seconds |
| `OUT_DIR` | New directory immediately below `/tmp/`, starting with `phi12-` |

The output directory is unique by default. Stop with a signal or the script's documented stop file. Route/device selection must match the actual running topology.

## One local device

`device-monitor.sh` requires an explicit IP/MAC pair, verifies it against the neighbor table, discovers the route device and collects device-scoped connection metadata. It exits if identity verification fails or changes.

```sh
DEVICE_IP=192.0.2.50 DEVICE_MAC=02:00:00:00:00:50 \
WAN1_TABLE=100 WAN2_TABLE=200 DURATION=300 \
sh scripts/diagnostics/device-monitor.sh
```

Requirements include `ip`, `conntrack`, `tcpdump`, `nft`, `awk` and permission to inspect connections and capture traffic. `WAN1_TABLE` and `WAN2_TABLE` are your actual numeric policy route tables. The script samples headers and connection metadata; the output still identifies devices and destinations and should stay private.

`OUT_DIR`, if set, must be a new directory directly below `/tmp/` beginning with `phi12-device-`. Create an empty `trigger` file there to record a user event or a `stop` file to end collection.

## VPS tunnel

`vps-probes.py` binds tunnel probes to the supplied interface and distinguishes an unanswered ICMP probe from a local command or timeout error:

```sh
python3 scripts/diagnostics/vps-probes.py \
  --target 192.0.2.2 --interface vpn0 \
  --internet-target 198.51.100.10 \
  --samples 60 --interval 2 --duration-seconds 180 \
  --log-root .local/vps-probes
```

Requirements: Linux `ip`, compatible `ping`, and `journalctl`. Reading the MQVPN journal may require additional permissions. Confirm the current router session address before starting. A historical tunnel address can silently produce misleading loss measurements.

Outputs include session metadata, route lookup, every probe with its exit status, summary counts and the MQVPN journal for the collection window. Inspect `--help` for the full interface.

## Windows client

Run `client-monitor.ps1` in Windows PowerShell with your own gateway and two Internet targets:

```powershell
& .\scripts\diagnostics\client-monitor.ps1 `
  -Gateway 192.0.2.1 `
  -InternetTarget1 198.51.100.10 -InternetTarget2 203.0.113.20 `
  -DurationSeconds 300 -OutputDirectory .\.local\client-session
```

If `-Gateway` is omitted, it is detected from the route to `-InternetTarget1`. Optional `-CitrixHost`, `-CitrixPort` and `-CitrixSessionName` add application endpoint checks. The existing process checks also observe Citrix and Zscaler processes when present. The monitor records adapter, route and transport state; it does not require an application login.

The output directory must be new. Ensure its parent exists. An empty `trigger` file records an outage event; a `stop` file ends collection. Some adapter and transport observations may require elevated privileges.

## Compare an archive

```sh
python3 scripts/diagnostics/compare.py input.tar.gz .local/comparison.json
```

The archive must use the layout produced by the historical collection package. The comparison correlates ping sequences, delayed replies, configuration hashes, service IDs and firewall/DNS events. It uses the named Europe/Berlin timezone when interpreting the relevant legacy timestamps, including daylight saving changes. It reads archive members without extracting them to disk.

Event proximity is a correlation, not a demonstrated cause. A reply arriving later for the same ICMP sequence is not counted as a final unanswered probe.
