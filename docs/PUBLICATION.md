# Publication scope, provenance and verification

## What is included

The template collection contains 357 source and support files: shell, Python and PowerShell scripts, nftables fragments, service/init definitions, patches, instrumentation payloads and the manifests required to understand them. It includes scripts stored under both the original script directory and analysis directories. Original issue labels and dates remain in many source paths as historical references. Separate tracker and scheduler test fixtures were added during license preparation.

Five main diagnostics are additionally provided as directly runnable files with native startup parameters. The English guides adapt the general methods from the existing troubleshooting, telemetry, migration, patch preparation, work-package and recovery documentation.

Reports that describe private deployments, credentials, personal narratives, unrelated commercial material and inventories are not republished as original documents. Their reusable technical methods are summarized in the English guides. Full logs, analysis outputs, backups, credential files, binary caches, images and complete third-party build trees are excluded.

## Sanitization

Original IPv4 targets, MAC addresses, interface names, VLAN references, personal account values, workspace identifiers, non-public endpoint hostnames and date-specific epochs become runtime template inputs. Known local credentials are compared in memory during preparation; no value-to-parameter mapping is published. Site-specific narrative inputs in report generators are also replaced where appropriate.

The main diagnostics require targets and interfaces explicitly. Device identity is supplied as an IP/MAC pair. Route table IDs are inputs. VLAN-specific devices are supplied by the operator through interface parameters.

Loopback, unspecified addresses, standard netmasks, public software endpoints and historical upstream author names may remain where they express protocol behavior, software provenance or generic mechanics. Example parameters use documentation addresses and invented values. Remaining historical labels are not operational defaults.

Some captured helpers need private input files that are intentionally absent. They preserve reusable source logic and require adaptation to the new operator's environment. A rendered historical installer remains subject to its target-version and checksum checks.

## Offline verification

```sh
python tools/verify.py
python -m unittest discover -s tests -v
```

The verifier checks the full template inventory, SHA256 integrity, parameter definitions, Python template syntax with synthetic values, disallowed file types, credential markers and literal deployment addresses. An optional external JSON list of private strings can extend the scan:

It also verifies per-file license assignments and matching license notices and texts. On Linux, `python tools/verify.py --shell-syntax` additionally checks rendered shell sources without executing their commands.

```sh
python tools/verify.py --private-values /protected/location/private-values.json
```

Values from that list are not printed. Keep the list outside the publication directory.

The tests exercise missing inputs, invalid parameters, source scope boundaries, safe Python string serialization and protection against overwriting output. These checks do not prove network behavior or firmware compatibility. Syntax checks and rendering never require a router connection.

See [the preparation verification record](VERIFICATION.md) for the checks completed on this publication package.

## Publish only this folder

Use `open_source` as the Git repository root, rather than committing its parent workspace. Keep rendered sources, local configuration, diagnostic results and credentials under the ignored `.local/` directory or outside the repository. Check the actual Git staging list before uploading; ignore rules do not remove files already tracked by Git.

Only sanitized published artifacts belong in this repository. Newly collected logs and rendered source can contain the operator's private values, so repeat the publication check before sharing future changes.

## Licensing and attribution

The original toolkit contributions use GPL-2.0-or-later. Copied and derived OpenWrt/OpenMPTCProuter components and upstream patches retain their applicable licenses. See [licensing](../LICENSING.md), [third-party notices](../THIRD_PARTY_NOTICES.md) and each file's `.license` sidecar for the exact assignment.

Public upstream copyright, author and signed-off-by contact metadata is preserved, including Andrea Covelli's attribution. The renderer copies license notices alongside generated files. GPL-v2 scheduler tests and GPL-v3 tracker tests execute as separate programs, avoiding a combined fixture with incompatible licenses.
