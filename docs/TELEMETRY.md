# Verify central logs and metrics from source to archive

A configured sender or a running service does not prove that current telemetry reaches its destination. Verify each stage independently: source, transport, receiver, processing and retained data.

## Syslog

Inventory the active sender command and configured destination. Compare runtime arguments with configuration files; a daemon can still use an older destination. Send a unique harmless test marker from each source and locate that marker in the receiver's actual daily file.

For application files, verify that the collector can read the real file under its service identity. Check directory traversal permissions, supplementary groups, ACLs and daemon confinement. Prefer narrowly scoped access over globally readable logs.

Validate sender-to-receiver transport separately from archive processing. Inspect listener addresses, protocol, route selection, firewall and any tunnel or NAT translation. A log entry on the sender alone proves only local generation.

## Prometheus and restricted exporters

Check scrape status and fresh sample timestamps for every intended target. An exporter responding locally is only the first hop. If an exporter is exposed through SSH forwarding, verify both its loopback listener and the forwarded endpoint from the scraper host.

Keep the public exposure appropriate to the deployment. SSH forwarding and restricted keys can provide access to a loopback-only exporter. The installer templates require your own endpoint, account and authentication inputs.

## Collectd and MQTT

Check installed plugins, generated configuration, broker authentication, subscribed topics and archived payloads. Preserve original payload bytes when maintaining an evidence archive.

Compare source timestamps with receipt timestamps. A live connection and increasing archive size can conceal a backlog. QoS 1 may retain messages during disruption and therefore increase observable delay; QoS 0 trades delivery guarantees for reduced queueing. Choose behavior based on the intended data use and verify it with fresh timestamps.

The source collection includes a switch web-statistics poller for devices without an exposed event-log interface. Port statistics can supplement diagnostics but do not replace native syslog or SNMP events.

## Storage and retention

Compress completed, inactive daily files rather than files that writers still hold open. Verify compressed contents before deleting the corresponding uncompressed file. Preserve ownership and modes, use a temporary output and check that the source did not change during compression.

Separate compression from retention deletion. Define retention by data type and ensure that the downstream database protocol, authentication, organization and bucket match the client configuration. Confirm current incoming samples after any repair.
