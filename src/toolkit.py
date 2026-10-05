"""Browse Daniel's security toolkit offline. Never installs or runs tools."""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

CATALOG = Path(__file__).resolve().parents[1] / "toolkit/catalog.json"
CATEGORIES = ("osint", "hacking", "opsec", "ai-security", "lab")


def load_catalog(path=CATALOG):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Unsupported catalog schema")
    rows = data.get("tools")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Catalog must contain tools")
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid catalog entry")
        for key in ("id", "name", "summary", "use_case", "setup", "network", "limitation", "url"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Missing catalog field: {key}")
        if not re.fullmatch(r"[a-z0-9-]+", row["id"]) or row["id"] in seen:
            raise ValueError("Invalid or duplicate tool ID")
        seen.add(row["id"])
        if row.get("category") not in CATEGORIES:
            raise ValueError("Unknown category")
        if row.get("setup") not in ("low", "medium", "high"):
            raise ValueError("Unknown setup estimate")
        if any(type(row.get(key)) is not bool for key in ("starter", "hidden_gem")):
            raise ValueError("Tool flags must be boolean")
        url = urlparse(row["url"])
        if url.scheme != "https" or url.netloc != "github.com" or not re.fullmatch(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", url.path):
            raise ValueError("Expected a canonical GitHub project URL")
        commands = row.get("commands")
        if not isinstance(commands, list) or any(not isinstance(c, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", c) for c in commands):
            raise ValueError("Commands must be executable names, without arguments")
    return rows


def select(rows, category=None, search=None, starter=False, gems=False):
    return [r for r in rows if (not category or r["category"] == category)
            and (not starter or r["starter"]) and (not gems or r["hidden_gem"])
            and (not search or search.casefold() in " ".join(
                str(r[k]) for k in ("id", "name", "summary", "use_case")).casefold())]


def doctor(rows, which=shutil.which):
    results = []
    for row in rows:
        found = {cmd: which(cmd) for cmd in row["commands"]}
        status = "found" if found and all(found.values()) else "missing" if found else "manual"
        results.append({"id": row["id"], "status": status, "executables": found})
    return results


def markdown(rows):
    def cell(value):
        return str(value).replace("|", "&#124;").replace("\n", " ")
    lines = ["# Security toolkit", "", "Generated from `catalog.json` with `python3 src/toolkit.py list --markdown`.", "",
             "Upstream project pages reviewed 2026-10-04. These are curated references, not bundled binaries or audited dependencies. Setup effort is an estimate; no maintenance or security guarantee is implied.", "",
             "Starter = first tools to learn. Gem = a specialized find worth evaluating, not a star-count ranking.", ""]
    for category in CATEGORIES:
        lines += [f"## {category.upper()}", "", "| Tool | Practical use | Setup | Selection |", "| --- | --- | --- | --- |"]
        for row in select(rows, category=category):
            label = ", ".join(name for key, name in (("starter", "Starter"), ("hidden_gem", "Gem")) if row[key]) or "On demand"
            lines.append(f"| [{cell(row['name'])}]({row['url']}) | {cell(row['use_case'])} | {row['setup']} | {label} |")
        lines.append("")
    lines += ["## Data exposure and limitations", ""]
    for row in rows:
        lines += [f"### {row['name']}", "", row["summary"], "", f"**Network/data:** {row['network']}", "", f"**Limit:** {row['limitation']}", ""]
    lines += ["Third-party software and data retain their upstream licenses. Follow each linked project's installation documentation. This repository does not auto-install, vendor, or execute these tools.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    listing = sub.add_parser("list", help="Search the curated catalog")
    detail = sub.add_parser("show", help="View one tool and its upstream installation link")
    detail.add_argument("id")
    check = sub.add_parser("doctor", help="Check PATH; never execute binaries")
    sub.add_parser("validate", help="Validate catalog structure")
    for command in (listing, check):
        command.add_argument("--category", choices=CATEGORIES)
        command.add_argument("--search")
        command.add_argument("--starter", action="store_true")
        command.add_argument("--gems", action="store_true")
        command.add_argument("--json", action="store_true")
    listing.add_argument("--markdown", action="store_true")
    args = parser.parse_args(argv)
    try:
        rows = load_catalog()
        if args.action == "validate":
            print(f"Valid catalog: {len(rows)} tools")
            return 0
        if args.action == "show":
            row = next((r for r in rows if r["id"] == args.id), None)
            if row is None:
                raise ValueError(f"Unknown tool: {args.id}")
            print(f"{row['name']} ({row['category']})\n{row['summary']}\n\nUse: {row['use_case']}\nSetup: {row['setup']}\nNetwork/data: {row['network']}\nLimit: {row['limitation']}\n\nInstall/docs: {row['url']}")
            return 0
        rows = select(rows, args.category, args.search, args.starter, args.gems)
        if args.action == "doctor":
            results = doctor(rows)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print("PATH presence only; versions, authenticity, and readiness are not checked.")
                for row in results:
                    print(f"{row['id']:20} {row['status']:8} {json.dumps(row['executables'])}")
            return 2 if any(r["status"] == "missing" for r in results) else 0
        if args.json:
            print(json.dumps(rows, indent=2))
        elif args.markdown:
            print(markdown(rows), end="")
        else:
            for row in rows:
                print(f"{row['id']:20} {row['category']:12} {row['summary']}")
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
