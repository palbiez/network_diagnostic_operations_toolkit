# Backups and recovery planning

Maintain a configuration backup and a separate support archive. They serve different purposes: a configuration backup restores supported settings, while a support archive preserves custom files, package versions, logs and the evidence needed to understand a change.

## Router backup scope

Inventory custom nftables fragments, firewall hooks, hotplug scripts, init scripts, monitoring services and local scheduler changes. Check the actual backup file list; do not assume a configuration backup includes every custom path.

Record installed package versions and relevant firmware details. Include an explicit rollback procedure and before/after checksums for modified package files. Keep historical originals separately from the newly generated archive.

Verify archive checksums after transfer and read every regular member. An archive that lists correctly may still contain unreadable or damaged content. Verify that the intended additional paths really exist in the archive.

Configuration archives often contain private keys, passwords and tokens. They belong in protected storage and are excluded from this public collection. Publish a sanitized description of the scope and verification results instead.

## Restore compatibility

Match the destination firmware and package version to the recorded source. Do not automatically restore a locally patched package file into a different release. Keep package corrections in a separate archive with an explicit version check and review their applicability before installation.

A successful backup is not proof of a successful restore. Validate recovery in an appropriate test environment and record technical and functional checks.

## A reusable recovery document

Prepare a recovery plan containing the failure scenario, dependencies, responsible roles, prerequisites, restore order, application startup, verification and return-to-service criteria. State recovery time and recovery point objectives and identify which assumptions still need confirmation.

A corresponding test record should contain:

- Test environment and its differences from production.
- Backup identity and integrity verification.
- Each restore step, expected result and actual result.
- Start and finish times, deviations and corrective actions.
- Technical checks and functional acceptance by the relevant owner.
- Rollback criteria and cleanup of the test environment.

Mark missing facts explicitly. Prepared documentation and scripts are a working result; measured recovery times and confirmed recovery objectives require an actual test.
