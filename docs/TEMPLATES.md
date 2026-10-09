# Using the complete source collection

Historical sources are stored under `templates/` with the suffix `.tmpl`. Every published source is listed in [the catalog](CATALOG.md). These files are deliberately rendered before use, so no private address or account value can become a silent default.

## Inspect and configure

From the repository root:

```sh
python tools/run.py list
python tools/run.py inspect Skripte/Diagnose/phi12-router-monitor.sh
```

`inspect` lists parameter names and types. Search the selected template for each marker, such as `@@IPV4_012@@`, to identify its role. Numbered names provide consistency across related sources without publishing the removed values. They are not an inventory of the original environment.

Supply values in a private JSON object or through repeatable startup options:

```sh
python tools/run.py render Skripte/Diagnose/phi5-vps-probes.py \
  --config .local/parameters.json \
  --output .local/vps-source
```

The resulting file is `.local/vps-source/Skripte/Diagnose/phi5-vps-probes.py`. `render` writes files and performs no network operation. The output directory must be new.

Use `examples/parameters.example.json` to explore the complete rendering process. Its values are synthetic, including documentation addresses, invented MACs and generic text; it is not an operational configuration.

```sh
python tools/run.py render Skripte \
  --include Analyse --include openwrt_patch \
  --config examples/parameters.example.json \
  --output .local/example-tree
```

## Run and pass native arguments

```sh
python tools/run.py run Skripte/Diagnose/phi5-vps-probes.py \
  --config .local/parameters.json \
  -- --target 192.0.2.2 --interface vpn0 \
  --internet-target 198.51.100.10 --samples 10
```

Arguments after `--` are forwarded unchanged to the rendered script. `--set NAME=VALUE` overrides a configured value. Supply network options through the script's existing environment variables or native arguments where possible. Avoid command-line credentials; use private credential files or the mechanisms already supported by the source.

The runner uses Python for `.py`, PowerShell for `.ps1`, and the script's shell family for shell sources. It preserves the original directory hierarchy and sets the working directory to the rendered tree root. Support files such as patches, service units and nftables fragments are rendered for manual review, rather than automatically installed.

OpenWrt devices often lack Python. Render on a workstation, then copy the reviewed shell script and its required helpers to the router. Invoke it there with `sh` or `bash` and explicit runtime inputs.

## Helpers and external inputs

Use `--include` for each helper file or directory that a selected script imports or calls. For example, many telemetry scripts import `Skripte/Diagnose/central_observability.py`, and issue scripts import `Skripte/Linear/linear_api.py` and `linear_sync.py`. The runner does not infer dependency graphs or copy local secrets and evidence.

Some report generators need analysis files, device inventories or Markdown documents from the original workflow. Those private inputs are excluded. Provide your own input files in the rendered hierarchy or adapt the relevant source paths. Some patches and build helpers also need matching upstream sources, which are not vendored here.

Legacy scheduling scripts contain date-specific workflows. Replace epoch and schedule parameters and review any remaining textual dates and event labels before use. Historical event labels retained in filenames do not imply an active schedule.

## Parameter behavior

IPv4, MAC, VLAN, interface, hostname, epoch and UUID parameters are validated. Python narrative parameters become quoted string literals. Other inline parameters reject quote characters and shell control characters. Inline substitution is intended for trusted operator configuration; it is not a general templating service for untrusted inputs.

Credentials requiring arbitrary quoting should remain in external credential files, not inline source parameters. The runner neither prints configuration values nor overwrites an existing output directory. Rendered files use restrictive file modes on platforms that support them; Windows users should use a suitably protected local directory.

Template checksums validate the published source. They are separate from the historical router installation checksums embedded in the installers. If template substitution changes a deployment payload, regenerate its deployment manifest and checksums from the exact reviewed payload and target version before use.

Every source template has an accompanying `.license` notice. Rendering copies that notice next to the generated file. Preserve it and the applicable license texts when distributing generated sources. Tracker and scheduler tests are generated and executed as separate programs because their upstream licenses differ.
