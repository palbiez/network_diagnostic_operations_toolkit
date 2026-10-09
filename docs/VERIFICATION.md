# Preparation verification

Prepared on 9 October 2026. Checks were performed offline against the publication artifacts; no network diagnostics, router modifications or deployments were executed.

| Check | Result |
| --- | --- |
| Sanitized template inventory and SHA256 values | 357 files, passed |
| Required template parameters | 326 definitions, consistent with source markers |
| Python template parsing after synthetic rendering | 94 files, passed |
| Main Python diagnostics | Syntax and VPS command help checked |
| Linux shell syntax on rendered sources and main shell diagnostics | 242 files, passed using POSIX shell or Bash as appropriate |
| Windows PowerShell syntax | 8 files, passed using the PowerShell parser |
| Template runner regression tests | 6 tests, passed, including notice preservation |
| Known private credential/account values | Compared in memory against publication files; no remaining matches |
| Literal deployment IPv4 addresses and credential markers | Publication scan passed |
| Additional path, name and IPv6 review | Remaining home paths use placeholders; remaining IPv6 constants describe generic dnsmasq behavior |
| Template execution smoke check | VPS template rendered and its `--help` ran successfully |
| License notices | Every publishable source and document has a per-file license assignment; applicable license texts and upstream notices included |

Checks do not establish live connectivity, dependency availability, successful firmware builds or compatibility with a new router. Historical installer checksums must be reviewed and regenerated for any changed payload. Private evidence dependencies are intentionally excluded.

Temporary rendered examples and syntax-check outputs were removed after verification. Repeat the offline checks in [publication notes](PUBLICATION.md) when changing the collection.

License preparation added separate tracker and scheduler test programs, retained the existing GitHub GPL-v2 license file, restored public upstream attribution metadata and corrected a protocol constant that had been over-generalized during sanitization. The tracker remains GPL v3, scheduler/bypass/DSCP remain GPL v2, firewall4 remains ISC, and the proposed MQVPN patch retains its Apache context with the GPL-v3 option for the combined derivative.
