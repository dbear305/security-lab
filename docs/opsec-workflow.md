# OPSEC and evidence workflow

## 1. Choose a workspace for the investigation

Use a dedicated browser profile and case directory. Keep credentials in the tool's supported secret store or local environment, not scripts or command history. Write the question, scope, and source plan first. Third-party DNS, CT, archive, and GitHub providers see requests sent to them; public-source research is not anonymous by default.

The [catalog](../toolkit/README.md) records each tool's data exposure and limitations. Start with the smallest tool set that answers the question.

## 2. Capture and preserve originals

Use the existing [domain collector](../README.md#domain-evidence) for DNS/CT observations. Use [Auto Archiver](https://github.com/bellingcat/auto-archiver) when webpage or media preservation is needed. Review its storage and archiver configuration first. Keep timestamps, source URLs, and collection errors alongside original files.

From the repository root, after collection finishes:

```bash
python3 src/manifest.py create reports/case-001 reports/case-001.manifest.json
python3 src/manifest.py verify reports/case-001 reports/case-001.manifest.json
```

Verification reports **added, missing, and changed** files. Exit codes: `0` success/match, `2` differences, `1` invalid input or I/O failure. Creating a manifest never overwrites an existing one. It rejects symlinks and special files and reads files in chunks. It inventories files, not empty directories, permissions, extended attributes, or filesystem timestamps.

Use a quiescent directory you control. This is not a race-proof forensic acquisition system: concurrent writers can invalidate a snapshot. A hash manifest detects byte changes relative to a trusted baseline; it does not prove when a source existed or authenticate a collector. Keep the baseline in a separately protected location, or sign it using your established signing workflow. Someone who can alter both files and manifest can replace the baseline.

## 3. Inspect your device and agent traffic

For Android, [PCAPdroid](https://github.com/emanuele-f/PCAPdroid) can capture app traffic without root in its normal mode. That mode occupies Android's VPN interface, so plan around Proton or another VPN. Analyze exported captures locally with Wireshark. Disable network name resolution when you want to avoid analysis-time DNS lookups. Encryption limits payload visibility.

For agent/MCP work, start with the [Cisco MCP Scanner](https://github.com/cisco-ai-defense/mcp-scanner) documentation and choose an analysis engine explicitly. Static analysis and external AI services have different exposure. Do not feed private skill content to an external engine without accounting for that transfer. Scan results are review leads, not certification that a server is safe.

## 4. Prepare a publication copy

Keep raw originals unchanged and make a separate sharing copy. Remove tokens, cookies, identifiers unrelated to the finding, and private engagement details. Inspect screenshots and embedded links. [ExifCleaner](https://github.com/szTheory/exifcleaner) helps with supported media; its PDF metadata removal is reversible and is not a redaction workflow.

Review files and Git history with [Gitleaks](https://github.com/gitleaks/gitleaks) installed from upstream. From the repository root:

```bash
gitleaks git . --redact
gitleaks dir . --redact
git diff --cached
```

Check the installed version's help if commands differ. Automated scans can miss secrets. Rotate any real exposed credentials. Ignored files already tracked by Git remain tracked.

## 5. Publish a reproducible finding

Use the [finding template](../research/FINDING.md), link primary evidence, distinguish observed facts from inferences, and state what the evidence cannot establish. Publish sanitized examples rather than raw case directories.
