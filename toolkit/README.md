# Security toolkit

Generated from `catalog.json` with `python3 src/toolkit.py list --markdown`.

Base catalog reviewed 2026-10-04; later additions record their review date in the entry. These are curated references, not bundled binaries or audited dependencies. Setup effort is an estimate; no maintenance or security guarantee is implied.

Starter = first tools to learn. Gem = a specialized find worth evaluating, not a star-count ranking.

## OSINT

| Tool | Practical use | Setup | Selection |
| --- | --- | --- | --- |
| [Subfinder](https://github.com/projectdiscovery/subfinder) | Expand domain leads before separately validating ownership and scope. | low | On demand |
| [checkdmarc](https://github.com/domainaware/checkdmarc) | Create actionable email-domain configuration findings. | low | Starter |
| [Auto Archiver](https://github.com/bellingcat/auto-archiver) | Keep archived evidence behind a research finding. | medium | Starter |
| [CertGraph](https://github.com/lanrat/certgraph) | Explore domain relationships beyond a flat certificate-name list. | low | Gem |
| [Octosuite](https://github.com/bellingcat/octosuite) | Analyze repository, organization, and public activity relationships. | low | On demand |
| [Kronikier](https://github.com/soxoj/kronikier) | Trace changes in a company's archived public contact pages. | medium | Gem |
| [Metawarc](https://github.com/ruarxive/metawarc) | Index preserved archives for repeatable local analysis. | medium | Gem |
| [Cert Spotter](https://github.com/SSLMate/certspotter) | Watch for certificate issuance involving your domains. | medium | On demand |
| [ASN](https://github.com/nitefood/asn) | Explain network ownership and routing context behind an address. | low | Gem |
| [ShadowFinder](https://github.com/bellingcat/ShadowFinder) | Compare possible locations using measured shadows and time. | medium | Gem |

## HACKING

| Tool | Practical use | Setup | Selection |
| --- | --- | --- | --- |
| [Nmap](https://github.com/nmap/nmap) | Inventory ports and service versions in a scoped assessment. | low | Starter |
| [ffuf](https://github.com/ffuf/ffuf) | Find routes and compare responses in the local web lab. | low | Starter |
| [ZAP](https://github.com/zaproxy/zaproxy) | Review HTTP behavior and produce a baseline web report. | medium | Starter |
| [Nuclei](https://github.com/projectdiscovery/nuclei) | Run reviewed, explicit templates against a lab or scoped asset. | medium | Starter |
| [Metasploit Framework](https://github.com/rapid7/metasploit-framework) | Study modules and reproduce a vulnerability in a disposable VM lab. | high | On demand |
| [sqlmap](https://github.com/sqlmapproject/sqlmap) | Validate SQL injection in an intentionally vulnerable application. | medium | On demand |
| [mitmproxy](https://github.com/mitmproxy/mitmproxy) | Inspect requests from your own client or test application. | medium | On demand |
| [Hackingtool (Z4nzu)](https://github.com/Z4nzu/hackingtool) | Find, install, and launch tools for recon, OSINT, web testing, and forensics in a Linux lab. | medium | On demand |

## OPSEC

| Tool | Practical use | Setup | Selection |
| --- | --- | --- | --- |
| [PCAPdroid](https://github.com/emanuele-f/PCAPdroid) | See which destinations your Android apps contact and export PCAPs. | low | Starter |
| [Wireshark](https://github.com/wireshark/wireshark) | Investigate PCAPs from Android, a lab, or your own network. | medium | Starter |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Review code and research outputs before publication. | low | Starter |
| [ExifCleaner](https://github.com/szTheory/exifcleaner) | Clean sharing copies of supported image and media files. | low | On demand |
| [Slips](https://github.com/stratosphereips/StratosphereLinuxIPS) | Evaluate unusual behavior in saved lab captures. | high | Gem |

## AI-SECURITY

| Tool | Practical use | Setup | Selection |
| --- | --- | --- | --- |
| [Cisco MCP Scanner](https://github.com/cisco-ai-defense/mcp-scanner) | Review agent tools, prompts, resources, and server code. | medium | Starter |

## LAB

| Tool | Practical use | Setup | Selection |
| --- | --- | --- | --- |
| [OWASP Juice Shop](https://github.com/juice-shop/juice-shop) | Practice web testing on a disposable local target. | low | Starter |

## Data exposure and limitations

### Nmap

Service and network discovery.

**Network/data:** Sends probes directly to the selected hosts.

**Limit:** Version guesses need confirmation; NSE scripts vary in behavior.

### ffuf

HTTP content and parameter fuzzing.

**Network/data:** Sends HTTP requests directly to the target.

**Limit:** SPA fallback pages can produce false positives; calibrate filters.

### ZAP

Intercepting proxy and web security scanner.

**Network/data:** Spidering sends requests; active scan modes send attack payloads.

**Limit:** Baseline rules are passive, but crawling is network-active and findings require review.

### Nuclei

Template-driven vulnerability checks.

**Network/data:** Templates can contact targets and out-of-band services; cloud upload is a separate feature.

**Limit:** Template matches are leads. Review template code, requests, and external interactions.

### Metasploit Framework

Exploit development and validation framework.

**Network/data:** Selected modules connect to targets; payloads may create sessions and change state.

**Limit:** Module-specific effects differ. Use VM snapshots and document exact module options.

### sqlmap

Automated SQL injection testing.

**Network/data:** Sends injection payloads to target endpoints.

**Limit:** Tests can be intrusive; start with a single parameter and minimal settings. Clone-based installs may have no PATH command.

### mitmproxy

Programmable HTTP and HTTPS interception.

**Network/data:** Traffic passes through your proxy; TLS decryption requires client trust configuration.

**Limit:** Use a dedicated test browser profile; remove the test CA when finished.

### Subfinder

Passive subdomain source aggregation.

**Network/data:** Queries external providers; API keys and provider coverage vary.

**Limit:** Discovered names are not proof of live services or common ownership.

### checkdmarc

SPF and DMARC record validation.

**Network/data:** Performs DNS lookups, including policy-related records.

**Limit:** DNS configuration alone does not establish mail delivery or spoofing outcomes.

### Auto Archiver

Preserves linked online content.

**Network/data:** Fetches URLs; configured storage and archivers can send data to third parties.

**Limit:** Platform changes, login requirements, and deleted content limit coverage.

### CertGraph

Certificate alternative-name relationship crawler.

**Network/data:** Default collection connects to hosts; the crtsh driver uses CT records.

**Limit:** Shared certificates require corroboration before inferring ownership.

### Octosuite

GitHub public-data investigation toolkit.

**Network/data:** Queries GitHub; authenticated requests identify the API account.

**Limit:** Rate limits and visibility constraints affect completeness.

### Kronikier

Historical website contact research.

**Network/data:** Queries the Wayback Machine and uses local caches.

**Limit:** Historical contacts may be obsolete; compare normalized phone numbers with raw text.

### Metawarc

Metadata extraction from WARC collections.

**Network/data:** Processes local archives; integrations can change exposure.

**Limit:** Useful after evidence capture; extracted metadata does not verify a source's claims.

### Cert Spotter

Certificate-transparency log monitoring.

**Network/data:** Reads public CT logs; configured notification hooks may send data elsewhere.

**Limit:** Issuance is an observation, not proof of a live service or compromise.

### ASN

ASN, routing, and IP context.

**Network/data:** Queries external routing, geolocation, and optional reputation services; modes vary.

**Limit:** IP geolocation and reputation are approximate and can be stale.

### ShadowFinder

Shadow-based geographic hypothesis tool.

**Network/data:** Notebook and map dependencies can access external services.

**Limit:** Measurement and timestamp uncertainty can produce broad or wrong location estimates.

### PCAPdroid

Android app traffic inspection.

**Network/data:** Normal capture processes traffic on the device using Android's VPN interface.

**Limit:** Competes with another VPN in standard mode; encrypted payloads remain encrypted without additional setup.

### Wireshark

Packet capture analysis.

**Network/data:** Offline PCAP reading can stay local; resolution features can generate lookups.

**Limit:** Captures can contain session tokens and personal data; GitHub is a mirror of the upstream GitLab repository.

### Gitleaks

Local secret detection in files and Git history.

**Network/data:** Core scanning can run locally.

**Limit:** A clean result is not proof that no credentials exist; exposed real secrets require rotation.

### ExifCleaner

Desktop media metadata cleaning.

**Network/data:** Processes files locally.

**Limit:** PDF metadata removal is reversible; preserve originals and inspect output separately.

### Slips

Behavioral analysis of network flows.

**Network/data:** Processes network data; threat-intelligence integrations may query external services.

**Limit:** Heuristic and ML alerts need investigation; start with known captures.

### Cisco MCP Scanner

MCP component security analysis.

**Network/data:** Static/local and external analysis engines have different data-sharing behavior.

**Limit:** Check the chosen engine and configuration before including private tool or skill content.

### OWASP Juice Shop

Intentionally vulnerable web application.

**Network/data:** Runs a local web service; image pulls contact a container registry.

**Limit:** Keep the published port on loopback; the application is deliberately vulnerable.

### Hackingtool (Z4nzu)

All-in-one security tool catalog and launcher by Z4nzu and contributors (MIT license).

**Network/data:** Installation downloads upstream tools; network activity and data exposure depend on the selected tool and any configured AI provider.

**Limit:** Requires Python 3.10+. Upstream supports Linux/macOS and explicitly rejects native Windows; use a Linux VM on a Windows host. Individual tools have their own requirements and licenses. Documentation reviewed 2026-10-05; runtime not tested here.

Third-party software and data retain their upstream licenses. Follow each linked project's installation documentation. This repository does not auto-install, vendor, or execute these tools.
