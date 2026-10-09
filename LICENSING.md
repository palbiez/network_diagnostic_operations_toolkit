# Licensing

Copyright (C) 2026 palbiez, for the original toolkit contributions.

The independently developed scripts, tools, tests, examples and English documentation in this repository are licensed under the **GNU General Public License, version 2 or (at your option) any later version**, identified as `GPL-2.0-or-later`, except for the explicitly identified third-party and derivative files below.

This software is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See [LICENSE](LICENSE) for the GNU General Public License version 2 text.

This repository is a collection of independently distributed tools and source artifacts. The default license does not replace upstream licenses. A `.license` file accompanies each source or template and specifies its SPDX license identifier, attribution, source and modification notice. [licensing.json](licensing.json) provides the machine-readable mapping, and the [source catalog](docs/CATALOG.md) displays template licenses.

## Exceptions

| Material | Applicable license |
| --- | --- |
| OpenMPTCProuter tracker sources, tracker patches and extracted tracker tests | `GPL-3.0-only` |
| OpenMPTCProuter scheduler, bypass and DSCP sources or derived excerpts | `GPL-2.0-only` |
| OpenWrt dnsmasq init source and the mac80211 patch artifacts | `GPL-2.0-only` |
| OpenWrt firewall4 init source | `ISC` |
| MQVPN proposed MTU patch | `GPL-3.0-only AND Apache-2.0` |

The MQVPN patch includes Apache-2.0 source context. For the combined derivative, the toolkit's GPL-2.0-or-later additions are distributed under the permitted GPL version 3 option. Apache-2.0 notices and conditions remain applicable to the upstream context. No MQVPN binary or bundled third-party library is distributed here.

GPL-v2-only scheduler tests and GPL-v3 tracker tests run as separate programs. The orchestration wrapper and build helper do not concatenate those sources into a single shell program.

## License texts and attribution

- [GPL version 2](LICENSES/GPL-2.0-only.txt).
- [GPL version 2 or later](LICENSES/GPL-2.0-or-later.txt).
- [GPL version 3](LICENSES/GPL-3.0-only.txt).
- [Apache License 2.0](LICENSES/Apache-2.0.txt).
- [ISC](LICENSES/ISC.txt) and the [firewall4 copyright notice](LICENSES/firewall4-COPYRIGHT.txt).
- [MQVPN NOTICE](LICENSES/mqvpn-NOTICE.txt).
- [Detailed third-party notices](THIRD_PARTY_NOTICES.md).

Retain these notices and applicable license texts when redistributing the corresponding sources. The renderer copies each source's `.license` notice alongside its generated file. Sanitization and local patches do not grant permission to relicense upstream code under the repository default.
