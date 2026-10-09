# Tracker and Wi-Fi patch notes

## Shared UCI changes and service restarts

The tracker correction under `Skripte/Router-Fixes/` addresses a distinction between shared configuration deltas and changes actually made by the tracker process. Scheduler and user-interface operations can leave UCI deltas; their presence alone does not show that a tracker changed a server or proxy option.

The patch uses a helper that reads the current option, writes only a changed value and records actual writes made by that process. Restart requests follow those writes rather than unrelated shared deltas. The accompanying isolated shell tests use stubs and fixtures to exercise the relevant branches.

The archived installer checks the exact source version using before/after SHA256 values, preserves originals and includes a rollback script. Those checksums describe the historical payload. Template rendering can change bytes: rebuild the deployment manifest and reviewed checksums for the actual target and payload before installation. Do not bypass a version check merely to make the installer proceed.

Build helpers expect matching captured sources. Supply suitable upstream or installed source files in place of the excluded private evidence. Retest the resulting correction in isolation before any live deployment.

## Deferred AP-side Fast Transition key upload

The Wi-Fi patch originated with Andrea Covelli. The collection includes the original patch and the locally adapted backports variant; authorship notices must remain attached to both. This collection does not claim authorship of the upstream fix.

The patch addresses an AP-side 802.11r timing window: userspace may attempt to install a pairwise key after a station entry exists but before the station is marked associated. Rejecting that installation with `-ENOENT` can interrupt roaming.

The proposed mechanism permits qualifying pre-association pairwise keys when software cryptography fallback is allowed, marks them for deferred hardware upload and attempts that upload after the association state transition. It updates association-dependent key flags before the upload and preserves the permitted software fallback if hardware installation fails.

The local variant was adapted for the recorded OpenWrt/backports source combination. Its preparation is evidenced by source artifacts; a successful complete firmware build, installation and roaming test are not established by this package. Before considering deployment, reproduce the build for the precise target, preserve firmware checksums and test the affected roaming scenario.

The complete OpenWrt and backports source trees are not included. Obtain the matching source versions separately and preserve their licensing requirements.
