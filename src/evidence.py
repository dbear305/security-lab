"""Domain evidence collector. Python 3.10+, standard library only."""

import argparse
import hashlib
import html
import ipaddress
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

VERSION = "0.1.0"
DNS_TYPES = {"A": 1, "AAAA": 28, "MX": 15, "NS": 2, "TXT": 16, "CAA": 257}
MAX_BYTES = 10 * 1024 * 1024


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def domain_name(value):
    name = value.strip().rstrip(".").encode("idna").decode("ascii").lower()
    try:
        ipaddress.ip_address(name)
    except ValueError:
        pass
    else:
        raise ValueError("Provide a domain, not an IP address")
    labels = name.split(".")
    if len(name) > 253 or len(labels) < 2 or any(
        not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part)
        for part in labels
    ):
        raise ValueError("Provide a domain such as example.com, without a URL or wildcard")
    return name


def request_json(url, timeout):
    request = Request(url, headers={"Accept": "application/json", "User-Agent": f"E360-Evidence/{VERSION}"})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Source response exceeded 10 MiB; collection is incomplete")
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def parse_dns(payload, record_type):
    if not isinstance(payload, dict) or type(payload.get("Status")) is not int:
        raise ValueError("Invalid DNS response: missing numeric Status")
    if payload.get("TC"):
        raise ValueError("Truncated DNS response")
    if payload["Status"] not in (0, 3):
        raise ValueError(f"DNS response code {payload['Status']}")
    answers = payload.get("Answer", [])
    if not isinstance(answers, list):
        raise ValueError("Invalid DNS answer list")
    records = set()
    for item in answers:
        if not isinstance(item, dict):
            raise ValueError("Invalid DNS answer")
        if item.get("type") == DNS_TYPES[record_type]:
            if not isinstance(item.get("data"), str) or not isinstance(item.get("name"), str):
                raise ValueError("DNS answer missing owner or data")
            owner = domain_name(item["name"])
            data = item["data"]
            if record_type in ("A", "AAAA"):
                address = ipaddress.ip_address(data)
                if address.version != (4 if record_type == "A" else 6):
                    raise ValueError("DNS address family mismatch")
                data = str(address)
            elif record_type == "NS":
                data = domain_name(data)
            elif record_type == "MX":
                priority, host = data.split(maxsplit=1)
                data = f"{int(priority)} {'.' if host == '.' else domain_name(host)}"
            records.add((owner, data))
    return [{"kind": "dns", "record_type": record_type, "owner": owner, "value": data}
            for owner, data in sorted(records)]


def parse_ct(payload, domain):
    if not isinstance(payload, list):
        raise ValueError("Invalid certificate transparency response: expected a list")
    names = {}
    for item in payload:
        if not isinstance(item, dict) or not isinstance(item.get("name_value"), str):
            raise ValueError("Certificate entry missing name_value")
        for raw in item["name_value"].splitlines():
            wildcard = raw.strip().startswith("*.")
            try:
                name = domain_name(raw.strip()[2:] if wildcard else raw)
            except (ValueError, UnicodeError):
                continue
            if name != domain and not name.endswith("." + domain):
                continue
            value = ("*." if wildcard else "") + name
            refs = names.setdefault(value, set())
            cert_id = str(item.get("id", ""))
            if cert_id.isdigit():
                refs.add("https://crt.sh/?id=" + cert_id)
    return [{"kind": "certificate_name", "value": name, "certificate_urls": sorted(refs)}
            for name, refs in sorted(names.items())]


def collect(domain, timeout=15, fixture=None, fetch=request_json):
    domain = domain_name(domain)
    if fixture is not None and fixture.get("domain") != domain:
        raise ValueError("Fixture domain does not match the requested domain")
    report = {"schema_version": 1, "tool_version": VERSION, "domain": domain,
              "collected_at": utc_now(), "mode": "synthetic_fixture" if fixture is not None else "live",
              "sources": [], "observations": []}
    queries = [("dns:" + kind, "https://dns.google/resolve?" + urlencode({"name": domain, "type": kind}), kind)
               for kind in DNS_TYPES]
    queries.append(("ct", "https://crt.sh/?" + urlencode({"q": "%." + domain, "output": "json"}), None))
    for source_id, url, kind in queries:
        source = {"id": source_id, "url": url, "collected_at": utc_now(), "status": "error"}
        try:
            if fixture is not None:
                payload = fixture["responses"][source_id]
                raw = json.dumps(payload, sort_keys=True).encode()
                digest = hashlib.sha256(raw).hexdigest()
            else:
                payload, digest = fetch(url, timeout)
            source["response_sha256"] = digest
            items = parse_dns(payload, kind) if kind else parse_ct(payload, domain)
            if kind:
                source["dns_status"] = payload["Status"]
            source["status"] = "ok"
            report["observations"].extend(dict(item, source_id=source_id) for item in items)
        except (HTTPError, URLError, OSError, ValueError, KeyError, TypeError) as exc:
            source["error"] = str(exc)
        report["sources"].append(source)
        if fixture is None and source_id != "ct":
            time.sleep(0.2)
    report["complete"] = all(item["status"] == "ok" for item in report["sources"])
    return report


def compare_reports(previous, current):
    if previous.get("schema_version") != 1 or current.get("schema_version") != 1:
        raise ValueError("Comparison requires schema version 1")
    if previous.get("domain") != current.get("domain") or previous.get("mode") != current.get("mode"):
        raise ValueError("Compare reports for the same domain and collection mode")
    old_sources = {s["id"] for s in previous["sources"] if s["status"] == "ok"}
    new_sources = {s["id"] for s in current["sources"] if s["status"] == "ok"}
    comparable = old_sources & new_sources

    def keys(report):
        return {(o["source_id"], o.get("owner", ""), o["value"]) for o in report["observations"]
                if o["source_id"] in comparable}

    before, after = keys(previous), keys(current)
    all_sources = {s["id"] for s in previous["sources"] + current["sources"]}
    return {"added": sorted(after - before), "removed": sorted(before - after),
            "excluded_sources": sorted(all_sources - comparable)}


def cell(value):
    return html.escape(str(value), quote=True).replace("|", "&#124;").replace("\n", "<br>")


def markdown(report):
    lines = [f"# Domain evidence: {report['domain']}", "",
             f"Collected: {report['collected_at']}", f"Mode: {report['mode']}",
             f"All configured source requests succeeded: {report['complete']}", "",
             "Collection success does not imply exhaustive coverage. Certificate names do not prove live hosts, ownership, or vulnerabilities.", "",
             "## Sources", "", "| Source | Status | URL | Detail |", "| --- | --- | --- | --- |"]
    for source in report["sources"]:
        detail = source.get("error", "DNS status " + str(source["dns_status"]) if "dns_status" in source else "Collected")
        lines.append("| " + " | ".join(cell(v) for v in (source["id"], source["status"], source["url"], detail)) + " |")
    lines += ["", "## Observations", "", "| Source | Owner | Value |", "| --- | --- | --- |"]
    for item in report["observations"]:
        lines.append("| " + " | ".join(cell(v) for v in (item["source_id"], item.get("owner", ""), item["value"])) + " |")
    if "changes" in report:
        changes = report["changes"]
        lines += ["", "## Changes since prior report", "", "These are changes in source observations, not confirmed changes in infrastructure.", ""]
        for label in ("added", "removed"):
            lines.append(f"### {label.title()} ({len(changes[label])})")
            lines.extend("- " + " / ".join(cell(v) for v in row) for row in changes[label])
            lines.append("")
        lines.append("Excluded unavailable sources: " + (", ".join(cell(s) for s in changes["excluded_sources"]) or "none"))
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("domain")
    parser.add_argument("--output", type=Path, default=Path("reports"))
    parser.add_argument("--fixture", type=Path, help="Replay synthetic source responses without network access")
    parser.add_argument("--previous", type=Path, help="Compare against a prior report.json")
    parser.add_argument("--timeout", type=float, default=15)
    args = parser.parse_args(argv)
    try:
        if not 0 < args.timeout <= 60:
            raise ValueError("Timeout must be greater than zero and at most 60 seconds")
        fixture = json.loads(args.fixture.read_text(encoding="utf-8")) if args.fixture else None
        previous = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else None
        report = collect(args.domain, timeout=args.timeout, fixture=fixture)
        if previous is not None:
            report["changes"] = compare_reports(previous, report)
        destination = args.output / (report["domain"] + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
        destination.mkdir(parents=True, exist_ok=False)
        (destination / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (destination / "report.md").write_text(markdown(report), encoding="utf-8")
        print(destination)
        return 0 if report["complete"] else 2
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
