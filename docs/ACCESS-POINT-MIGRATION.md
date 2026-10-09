# Convert an OpenWrt router to a VLAN access point

The collection includes an access-point conversion source under `Skripte/Bestand/`. Its topology values are template parameters. It represents a particular device and configuration structure; adapt that structure to the target rather than assuming all OpenWrt devices use the same bridge and port names.

## Preparation

Inventory the target device, firmware, management address, bridge, physical ports, VLAN IDs, UCI sections and wireless network assignments. Identify the intended management VLAN and which ports should carry tagged or untagged traffic. Save a configuration backup and a readable before-state.

Arrange a recovery access path before changing the bridge or management configuration. Define how to return to the earlier state if management access fails.

## Conversion approach

Retain the desired wireless assignments and configure the bridge VLAN membership deliberately. Remove obsolete layer-three addresses from interfaces intended only to bridge traffic. Set the management address from an explicit operator input.

Disable routing services only when the target role no longer requires them. Review DHCP, firewall, WAN interfaces, VPNs and routing policies separately. Service assumptions are device-specific and should remain visible in the reviewed source.

Prefer one bounded change followed by a functional check. Verify management reachability, correct tag handling, client DHCP acquisition and traffic through the intended upstream router. A correct-looking UCI configuration is insufficient without these checks.

The archived migration source retains an interactive confirmation and creates a backup. Review its fixed service list, port mapping and section logic in addition to supplying runtime network parameters.
