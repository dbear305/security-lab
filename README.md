# Security Lab | Daniel Berriel IV

[![Security research checks](https://github.com/dbear305/security-lab/actions/workflows/security-research.yml/badge.svg)](https://github.com/dbear305/security-lab/actions/workflows/security-research.yml)

**OSINT, OPSEC, hacking tools, and reproducible security research.** A practical workbench for infrastructure investigations, local web testing, Android traffic analysis, and agent security.

Includes three dependency-free Python utilities, a searchable catalog of 24 upstream projects, and local hacking lab configurations. An independent project maintained by [Daniel Berriel IV](https://github.com/dbear305).

## Start here

| Goal | Start with | Result |
| --- | --- | --- |
| Find hacking tools | [Tool catalog](toolkit/README.md#hacking) | Nmap, ffuf, ZAP, Nuclei, Metasploit, sqlmap, mitmproxy |
| Practice web hacking | [Local web lab](labs/02-web-hacking.md) | Juice Shop + discovery, fuzzing, baseline scanning, template checks |
| Learn exploitation tooling | [Metasploit and sqlmap](labs/03-exploitation-tools.md) | Scoped module and injection-testing exercises |
| Investigate infrastructure | [Domain evidence lab](labs/01-domain-evidence.md) | DNS/CT evidence and change comparison |
| Find specialized OSINT tools | [Catalog CLI](#browse-the-toolkit) | Filter hidden gems, categories, and use cases |
| Preserve and share findings | [OPSEC workflow](docs/opsec-workflow.md) | File hashes, traffic review, sanitized evidence |

Start with the offline demo, then complete one local lab and publish one manually verified finding. Install other tools when an investigation needs them.

## Quick start

Requires Python 3.10 or newer. No packages, API keys, or installation steps are required.

Clone this standalone repository, then run:

```bash
git clone https://github.com/dbear305/security-lab.git
cd security-lab
python3 src/evidence.py example.com --fixture examples/fixture.json
```

On Windows, use `py -3` in place of `python3`.
The offline demo uses clearly labeled synthetic responses and makes no network requests. It prints a new directory containing `report.json` and `report.md`.

[Read the sample report](examples/report.md) or [inspect the JSON](examples/report.json).

## Browse the toolkit

From the repository root:

```bash
python3 src/toolkit.py list --starter
python3 src/toolkit.py list --category hacking
python3 src/toolkit.py list --gems
python3 src/toolkit.py list --search Android --json
python3 src/toolkit.py show metasploit
python3 src/toolkit.py doctor --category hacking
```

The catalog and CLI work offline. `show` includes the upstream installation link, practical use, setup estimate, network exposure, and limitations. `doctor` only checks executable names on PATH; it does not run or install tools, inspect versions, or guarantee that a binary is authentic. GUI, Android, and some source-based tools require manual setup checks.

Catalog exit codes: `0` success, `1` catalog/input error, `2` missing PATH tools from `doctor`. A `manual` result means no automatic readiness check was performed.

Third-party projects are linked and documented, not copied into this repo. The core Python utilities require no packages; optional labs and external tools have their own dependencies.

## Domain evidence

```bash
python3 src/evidence.py example.com
```

The tool makes six DNS-over-HTTPS requests and one certificate-transparency query, with a 15-second timeout per request and a short pause between requests. It contacts Google and crt.sh, not target web servers. DNS resolution can cause Google's resolver to query authoritative nameservers. The providers see the queried domain. There are no port scans, authentication attempts, or automatic retries.

Run again later and compare against the JSON file from the earlier run:

```bash
python3 src/evidence.py example.com --previous reports/REPLACE_WITH_PRIOR_RUN/report.json
```

Use the actual path printed by your earlier run. Synthetic and live reports cannot be mixed in a comparison. Sources must succeed in both runs to be compared. TTL changes and certificate-ID changes are excluded from the observation comparison.

Exit codes: `0` all configured source requests succeeded; `2` partial collection with reports saved; `1` invalid input, comparison, or output failure. Success does not imply complete Internet coverage. HTTP 429, timeouts, malformed responses, and DNS failures appear in the source records.

## Explore

| Location | Contents |
| --- | --- |
| [src/evidence.py](src/evidence.py) | Dependency-free command-line collector |
| [src/toolkit.py](src/toolkit.py) | Search, filter, inspect, and check tool availability |
| [src/manifest.py](src/manifest.py) | Create and verify SHA-256 evidence inventories |
| [toolkit](toolkit/README.md) | 24 curated tools, including specialized OSINT finds |
| [tests](tests/) | Offline parsing, integrity, catalog, and CLI tests |
| [examples](examples/README.md) | Synthetic source data and generated reports |
| [labs](labs/02-web-hacking.md) | Domain evidence, local web hacking, and exploitation-tool practice |
| [research](research/README.md) | Demonstration case study and research template |
| [docs/methodology.md](docs/methodology.md) | Collection behavior and evidence limitations |
| [docs/resources.md](docs/resources.md) | Curated primary resources |
| [docs/opsec-workflow.md](docs/opsec-workflow.md) | Evidence preservation, Android/agent review, publication hygiene |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution and verification instructions |

## Verification

```bash
python3 -m unittest discover -s tests -v
```

The GitHub Actions workflow runs offline tests and the demo on Python 3.10 and 3.12, validates the catalog, and checks Compose configuration whenever this section changes. Live source availability and third-party scanner execution are not tested in CI. See each lab's verification boundary before treating its instructions as a validated result.

## Scope and reuse

Use the labs for training and the collector for public-source research. Define an engagement's scope before adding active testing. Keep private evidence and credentials out of commits; generated reports are ignored by Git.

Project code is available under the [MIT license](LICENSE). Original Elevate360 Systems LLC copyright notices are preserved. Third-party software and source data retain their own terms. See the repository [security policy](SECURITY.md) for vulnerability reporting.

## Evidence integrity

After collecting a case, hash the completed folder and verify it later:

```bash
python3 src/manifest.py create reports/case-001 reports/case-001.manifest.json
python3 src/manifest.py verify reports/case-001 reports/case-001.manifest.json
```

Use an existing case folder and keep its manifest outside it. The tool detects added, missing, and changed files; it does not prove source authenticity or replace a signed chain of custody. See [limitations and workflow](docs/opsec-workflow.md).
