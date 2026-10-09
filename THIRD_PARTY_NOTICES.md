# Third-party notices

License review and publication preparation: 9 October 2026. All upstream attribution below is public provenance, rather than private deployment information. Original copyright and signed-off-by notices are preserved; `.license` sidecars record the source and local changes.

## OpenMPTCProuter tracker — GPL version 3

OpenMPTCProuter's tracker is a modified version of the OverTheBox tracker from OVH. Credit: Ycarus (Yannick Chabanois), OVH and the OverTheBox contributors. The tracker package declares GNU GPL version 3 in its [package metadata](https://github.com/Ysurac/openmptcprouter-feeds/blob/e23b7e0243d90a47819d75a7b44edcc184d6486c/omr-tracker/Makefile).

Included material comprises captured tracker/server/shadowsocks scripts, the instrumented tracker, the locally corrected server tracker, its patch, upstream pull request 335 and the extracted `test-server.sh` fixture. These are identified as `GPL-3.0-only`; see [the GPL v3 text](LICENSES/GPL-3.0-only.txt).

Upstream pull request 335 was authored by GitHub user `pylaterreur`. Its attribution and [upstream reference](https://github.com/Ysurac/openmptcprouter-feeds/pull/335) are retained. This toolkit does not claim authorship of that upstream contribution.

## OpenMPTCProuter scheduler, bypass and DSCP — GPL version 2

Credit: Ycarus (Yannick Chabanois) and the project contributors. The [scheduler](https://github.com/Ysurac/openmptcprouter-feeds/blob/e23b7e0243d90a47819d75a7b44edcc184d6486c/omr-schedule/Makefile), [bypass](https://github.com/Ysurac/openmptcprouter-feeds/blob/e23b7e0243d90a47819d75a7b44edcc184d6486c/omr-bypass/Makefile) and [DSCP](https://github.com/Ysurac/openmptcprouter-feeds/blob/e23b7e0243d90a47819d75a7b44edcc184d6486c/omr-dscp/Makefile) notices state GNU GPL version 2.

Included material comprises captured, modified and instrumented `010-services` sources, their patch, upstream pull request 326, instrumented bypass, DSCP patch and isolated DSCP tests. The build-fix helper contains a derived scheduler function. These files are identified as `GPL-2.0-only`; see [the GPL v2 text](LICENSES/GPL-2.0-only.txt).

Upstream pull request 326 was authored by `pylaterreur`; retain that credit and [reference](https://github.com/Ysurac/openmptcprouter-feeds/pull/326). The extracted `test-scheduler.sh` fixture is GPL-v2-only and executes separately from the tracker fixture.

## OpenWrt dnsmasq init script — GPL version 2

Copyright (C) 2007-2012 OpenWrt.org. The captured init script was instrumented with bounded diagnostic notifications and sanitized. The OpenWrt package declares GPL version 2; see [the package source](https://github.com/openwrt/openwrt/tree/0ef832f34e309fd060b1eb6b9aa78e6b4c5d1c77/package/network/services/dnsmasq). Its template is identified as `GPL-2.0-only`.

## OpenWrt firewall4 init script — ISC

Copyright (C) 2021 Jo-Philipp Wich. The firewall4 [package metadata](https://github.com/openwrt/openwrt/blob/0ef832f34e309fd060b1eb6b9aa78e6b4c5d1c77/package/network/config/firewall4/Makefile) identifies ISC. The instrumented init script retains this permissive license. The applicable copyright, permission and warranty notice is included in [firewall4-COPYRIGHT.txt](LICENSES/firewall4-COPYRIGHT.txt).

## Linux/mac80211 Fast Transition patches — GPL version 2

Patch author: Andrea Covelli. The original and locally adapted patches derive from Linux/mac80211 code and are identified as `GPL-2.0-only`. The Linux [COPYING file](https://github.com/torvalds/linux/blob/master/COPYING) identifies the kernel as GPL version 2 only and states that contributions are subject to that file. The syscall exception concerns use of the syscall interface and does not relicense internal mac80211 modifications.

Preserved references include [OpenWrt pull request 23181](https://github.com/openwrt/openwrt/pull/23181) and the mailing-list link in the patch header. Author and signed-off-by metadata remain intact. Local work consists of backports adaptation and preparation, not authorship of the upstream fix. Complete firmware build, installation and roaming validation are not established by this publication.

## MQVPN proposed MTU patch — Apache context and GPL version 3 derivative

Copyright (c) 2026 mp0rta and mqvpn contributors. The proposed patch includes context from MQVPN commit `ee78205d3db491ca7727b974bda0c91ae1523236`, whose [LICENSE](https://github.com/Ysurac/mqvpn/blob/ee78205d3db491ca7727b974bda0c91ae1523236/LICENSE) is Apache-2.0. The patch's new toolkit contribution uses the GPL version 3 option of the GPL-2.0-or-later grant when combined with that context. Its SPDX expression is `GPL-3.0-only AND Apache-2.0`.

Both [Apache-2.0](LICENSES/Apache-2.0.txt) and [GPL v3](LICENSES/GPL-3.0-only.txt) texts are supplied. The upstream [NOTICE](LICENSES/mqvpn-NOTICE.txt) is preserved. Entries concerning xquic, lwIP and Wintun are upstream provenance; those libraries are not included. The patch remains proposed, unbuilt and uninstalled.

## Dependencies obtained separately

Python packages, native utilities, complete OpenWrt/backports source trees and firmware images are not bundled. Calling or importing separately installed dependencies does not change their own licenses. When redistributing them, retain their applicable notices and follow their distribution terms.
