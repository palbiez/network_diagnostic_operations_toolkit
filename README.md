# Network diagnostics and operations toolkit

Reusable diagnostics and sanitized source templates developed while investigating OpenWrt, OpenMPTCProuter, MQVPN and central telemetry.

The main diagnostic scripts accept network details at startup. The complete source collection is distributed as templates: original addresses, MAC addresses, VLAN identifiers, interface names, account identifiers and site-specific text have been removed. Original logs, credentials, inventory exports and configuration backups are excluded.

## Start here

- [Run the diagnostics](docs/DIAGNOSTICS.md): Windows client, Linux router, device and VPS monitoring.
- [Use the source templates](docs/TEMPLATES.md): supply your own parameters, render and run a selected script.
- [Full source catalog](docs/CATALOG.md): every included source and support file.
- [Troubleshoot multiple network paths](docs/TROUBLESHOOTING.md).
- [Verify central telemetry](docs/TELEMETRY.md).
- [Plan backups and recovery](docs/BACKUP-AND-RECOVERY.md).
- [Migrate an OpenWrt access point](docs/ACCESS-POINT-MIGRATION.md).
- [Understand the tracker and Wi-Fi patches](docs/PATCHES.md).
- [Synchronize work packages](docs/ISSUE-SYNC.md).
- [Publication scope and provenance](docs/PUBLICATION.md).

## Layout

```text
scripts/diagnostics/   Ready-to-run diagnostics with native startup parameters
templates/            Complete sanitized source collection (*.tmpl)
tools/run.py          Offline template inspection, rendering and execution
tools/verify.py       Offline publication checks
examples/             Synthetic parameters; documentation-only network addresses
tests/                Offline tests for the template runner
docs/                 English documentation
manifest.json         Template checksums and required parameter names
```

For example, on a Linux VPS:

```sh
python3 scripts/diagnostics/vps-probes.py \
  --target 192.0.2.2 --interface vpn0 \
  --internet-target 198.51.100.1 --samples 30 --interval 2
```

The example addresses throughout this repository are documentation addresses. Replace them with your own reachable targets.

The archive also contains scripts that install packages, change configuration, restart services, schedule tasks, write to Linear or deploy patches. Inspect a selected source before executing it. Historical installers require a version-specific review and fresh checksums; they are preserved for adaptation, rather than presented as universal installers.

## Requirements and checks

The offline tools use Python 3.9+ and its standard library. Individual scripts have additional dependencies documented in the guides. PowerShell scripts require Windows networking cmdlets; Linux scripts require the appropriate diagnostic utilities and permissions.

```sh
python tools/verify.py
python -m unittest discover -s tests -v
```

Publish this folder as the repository root. Keep local parameters, generated files and diagnostic output under `.local/`, which is ignored by Git. Generated logs can contain your own private network information.

## Licensing

Original toolkit scripts, tools and documentation are licensed under **GPL-2.0-or-later**. Upstream and derivative material retains its applicable GPL v2, GPL v3, ISC or Apache terms. See [licensing](LICENSING.md), [third-party notices](THIRD_PARTY_NOTICES.md) and the per-file `.license` notices. Rendering copies the applicable notice alongside each generated source file.
