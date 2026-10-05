# Local web hacking lab

**Outcome:** inventory a service, fuzz routes, inspect a baseline scan, and run one transparent Nuclei template. Use the disposable local target below or a separately authorized assessment scope.

## Requirements and setup

Docker Engine/Desktop with Compose v2. Install Nmap, ffuf, and Nuclei from their [upstream projects](../toolkit/README.md). They are optional: run the stages for tools you have. On Windows, use PowerShell for Docker/Python and WSL or Kali for CLI tools. A tool in WSL is not necessarily visible to Windows Python's PATH check.

Run from the repository root:

```bash
python3 src/toolkit.py doctor --category hacking
python3 -c "from pathlib import Path; Path('reports/web-lab').mkdir(parents=True, exist_ok=True)"
docker compose -f labs/web/compose.yml up -d --wait juice-shop
```

On Windows, substitute `py -3` for `python3`. Open <http://127.0.0.1:3001>. The published port is loopback-only; the Compose network is internal. Keep testing on this local address. Port 3001 avoids the website's default port 3000.

The Compose images use upstream moving tags for easy setup, not frozen versions. For repeatable investigations, record the pulled image digests and pin `image:` to those digests. Image downloads need registry access even though the running lab network is internal.

```bash
docker image inspect bkimminich/juice-shop:latest --format '{{json .RepoDigests}}'
docker image inspect ghcr.io/zaproxy/zaproxy:stable --format '{{json .RepoDigests}}'
```

The ZAP image is pulled when its stage is first run; record its digest afterward. Save tool versions, image digests, date, and commands with your private lab notes.

## 1. Service inventory

```bash
nmap -sT -sV --version-light -p 3001 127.0.0.1 -oA reports/web-lab/nmap
```

TCP connect scanning does not require raw-socket privileges. Check that the port is open. A service guess is not proof of a particular software version or vulnerability.

## 2. Route discovery

```bash
ffuf -w labs/web/paths.txt -u http://127.0.0.1:3001/FUZZ -rate 5 -t 1 -ac -of json -o reports/web-lab/ffuf.json
```

The supplied list is deliberately short. Compare a real route with the deliberately nonexistent route. Juice Shop is a single-page application; identical fallback pages may look like valid routes. Automatic calibration helps but can also hide useful responses. Manually compare body length, redirects, and content before reporting anything.

## 3. ZAP baseline

```bash
docker compose -f labs/web/compose.yml --profile tools run --rm zap
```

Outputs: `reports/web-lab/zap.html` and `zap.json`. The scanner reaches the app by Docker service name, not the host's loopback address. Baseline performs crawling and passive rule analysis; it is not the full active scan. `-I` prevents warning-only findings from failing the command; FAIL findings and scanner errors still need review.

If Linux bind-mount permissions block report writing, set the container user to your account before running:

```bash
export LAB_UID=$(id -u)
export LAB_GID=$(id -g)
```

No permission change to the repository is required. On Docker Desktop, start with the defaults.

## 4. A Nuclei template you can read in full

```bash
nuclei -validate -t labs/web/templates/juice-shop-detect.yaml
nuclei -u http://127.0.0.1:3001 -t labs/web/templates/juice-shop-detect.yaml -rl 2 -c 1 -ni -duc -jsonl -o reports/web-lab/nuclei.jsonl
```

This repository's [template](web/templates/juice-shop-detect.yaml) makes one GET, follows no redirects, and matches a page title. A match establishes only a page-title observation. `-ni` disables Interactsh and `-duc` disables update checks; the template itself has no external callback. The locally authored template is unsigned; review it before execution. An absent match could mean the page title changed, not that the service is secure.

## 5. Save the result, then stop the lab

```bash
python3 src/manifest.py create reports/web-lab reports/web-lab.manifest.json
python3 src/manifest.py verify reports/web-lab reports/web-lab.manifest.json
docker compose -f labs/web/compose.yml down
```

Create the manifest only after tools finish writing. Use a new baseline filename for a subsequent run. The manifest sits outside the evidence folder to avoid hashing itself.

Turn one manually verified observation into a [research write-up](../research/TEMPLATE.md), including a fix and a retest. Raw output stays under ignored `reports/`.

## Troubleshooting and verification boundary

- Port in use: stop the conflicting local service or change the host port and all host-side commands together.
- App not ready: inspect `docker compose -f labs/web/compose.yml logs juice-shop`.
- ZAP cannot write: check the report directory exists and the UID/GID settings above.
- Empty scanner output: review errors, target readiness, and matching assumptions; do not label an empty file a clean assessment.

Compose receives configuration validation in CI. The Nuclei template was reviewed but not validated by a Nuclei binary here. Docker and the external scanners were unavailable in the build environment, so this lab has **not been runtime-validated there**. The Python utilities have automated offline tests.

Primary references: [Juice Shop](https://github.com/juice-shop/juice-shop), [Nmap](https://nmap.org/book/man.html), [ffuf](https://github.com/ffuf/ffuf), [ZAP baseline](https://www.zaproxy.org/docs/docker/baseline-scan/), [Nuclei](https://github.com/projectdiscovery/nuclei).
