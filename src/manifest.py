"""Create and verify SHA-256 inventories of local evidence folders."""

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


def inventory(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Evidence root must be a real directory, not a symlink")
    root = root.resolve()
    files = []
    def fail(error):
        raise error
    for directory, folders, names in os.walk(root, onerror=fail, followlinks=False):
        for name in folders + names:
            path = Path(directory) / name
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise ValueError(f"Symlinks and special files are unsupported: {path.relative_to(root)}")
        for name in names:
            path = Path(directory) / name
            before = path.stat()
            digest = hashlib.sha256()
            size = 0
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
                    size += len(chunk)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino) or size != after.st_size:
                raise ValueError(f"File changed during hashing: {path.relative_to(root)}")
            files.append({"path": path.relative_to(root).as_posix(), "size": size, "sha256": digest.hexdigest()})
    return sorted(files, key=lambda row: row["path"])


def create(root):
    result = {"schema_version": 1, "algorithm": "sha256", "created_at": datetime.now(timezone.utc).isoformat(), "files": inventory(root)}
    validate(result)
    return result


def validate(manifest):
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1 or manifest.get("algorithm") != "sha256" or not isinstance(manifest.get("files"), list):
        raise ValueError("Invalid manifest schema")
    seen = set()
    for row in manifest["files"]:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise ValueError("Invalid manifest entry")
        name = row["path"]
        path = PurePosixPath(name)
        if not name or path.is_absolute() or any(p in ("", ".", "..") for p in name.split("/")) or "\\" in name or ":" in name or name in seen:
            raise ValueError("Manifest paths must be unique relative POSIX file paths")
        seen.add(name)
        if type(row.get("size")) is not int or row["size"] < 0 or not isinstance(row.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
            raise ValueError("Invalid manifest size or SHA-256")


def verify(root, manifest):
    validate(manifest)
    expected = {r["path"]: (r["size"], r["sha256"]) for r in manifest["files"]}
    actual = {r["path"]: (r["size"], r["sha256"]) for r in inventory(root)}
    missing = sorted(expected.keys() - actual.keys())
    added = sorted(actual.keys() - expected.keys())
    changed = sorted(p for p in expected.keys() & actual.keys() if expected[p] != actual[p])
    return {"ok": not (missing or added or changed), "missing": missing, "added": added, "changed": changed}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("create", "verify"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("manifest", type=Path, help="Manifest must be outside the evidence directory")
    args = parser.parse_args(argv)
    try:
        if args.manifest.resolve().is_relative_to(args.directory.resolve()):
            raise ValueError("Keep the manifest outside the evidence directory")
        if args.action == "create":
            result = create(args.directory)
            # Exclusive creation preserves an existing baseline instead of silently replacing it.
            with args.manifest.open("x", encoding="utf-8") as handle:
                handle.write(json.dumps(result, indent=2) + "\n")
            print(f"Inventoried {len(result['files'])} files: {args.manifest}")
            return 0
        result = verify(args.directory, json.loads(args.manifest.read_text(encoding="utf-8")))
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 2
    except (OSError, ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
