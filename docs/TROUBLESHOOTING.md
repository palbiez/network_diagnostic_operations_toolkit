# Diagnose intermittent failures across several network paths

A useful investigation distinguishes the local client, Ethernet link, upstream gateway, Internet path, VPS, tunnel and application. Simultaneous observations help identify the earliest shared failure boundary.

## Establish the path

Record current interface addresses, route rules and route tables before measuring. Verify which kernel device reaches each target. Confirm the current tunnel session address on both ends. A remembered tunnel address or unbound ping can measure an unintended path.

For each WAN, probe its gateway and at least two independent external targets while recording interface counters. Observe the VPS directly and the tunnel peer separately. On the client, measure the local gateway and the application connection at the same time.

Use synchronized clocks and record UTC timestamps. Preserve sequence numbers, successful replies, round-trip times, command exit codes and local errors. A log containing only failures cannot establish a reliable denominator or distinguish packet loss from a failed local command.

## Interpret the observations

| Observation | Useful next check |
| --- | --- |
| Client-to-gateway degrades | LAN route, Wi-Fi, switch port and adapter counters |
| WAN gateway degrades with rising carrier or CRC errors | Cable, NIC, switch port and upstream Ethernet link |
| Gateway stays responsive but several external targets degrade on one WAN | Upstream WAN, ISP path, load and queueing |
| Direct WAN paths stay healthy while tunnel probes degrade | Current tunnel route, peer state and bounded MQVPN journal |
| Network probes stay healthy during an application outage | Application transport, endpoint, proxy and session state |

Gateway ICMP may be rate limited. A sleeping mobile device or an endpoint blocking ICMP is not a network loss detector. Compare several signals rather than treating one timeout as an outage.

## Collect bounded evidence

Start with a modest duration and storage bound. Capture configuration hashes, service PIDs, route snapshots and counter deltas alongside packet observations. Record user-visible outage times with a trigger file. Use short, scoped captures for the relevant device or connection when packet evidence is needed.

Separate idle observations from controlled load tests. Counter differences over the exact event window are more useful than cumulative values read at unrelated times. Keep stdout and stderr from diagnostic commands.

## Test one proposed cause

Preserve a backup, identify a reversible change and define its expected observable effect. Repeat the same measurements after the change. Distinguish a temporal correlation from evidence of cause. Do not use a broad network restart as a diagnostic probe: it changes multiple conditions and can invalidate the observations.

Generated data may contain routing details, destinations, device identifiers and application metadata. Retain it locally and sanitize any excerpts intended for an issue or public report.
