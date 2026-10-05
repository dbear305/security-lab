import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("manifest", ROOT / "src/manifest.py")
manifest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manifest)


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.case = self.base / "case"
        self.case.mkdir()
        (self.case / "nested").mkdir()
        (self.case / "a.txt").write_bytes(b"abc")
        (self.case / "nested/empty.bin").write_bytes(b"")

    def test_known_digest_and_nested_files(self):
        result = manifest.create(self.case)
        self.assertEqual(result["files"][0]["sha256"], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(result["files"][1]["path"], "nested/empty.bin")
        self.assertTrue(manifest.verify(self.case, result)["ok"])

    def test_added_missing_and_same_size_changes(self):
        baseline = manifest.create(self.case)
        (self.case / "a.txt").write_bytes(b"xyz")
        (self.case / "nested/empty.bin").unlink()
        (self.case / "new.txt").write_bytes(b"new")
        result = manifest.verify(self.case, baseline)
        self.assertEqual(result, {"ok": False, "added": ["new.txt"], "missing": ["nested/empty.bin"], "changed": ["a.txt"]})

    def test_symlinks_rejected(self):
        try:
            (self.case / "link").symlink_to(self.base)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "Symlinks"):
            manifest.create(self.case)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unavailable")
    def test_special_files_rejected_without_blocking(self):
        os.mkfifo(self.case / "pipe")
        with self.assertRaisesRegex(ValueError, "special files"):
            manifest.create(self.case)

    def test_unreadable_subdirectory_fails_closed(self):
        from unittest.mock import patch
        def inaccessible(root, onerror, followlinks):
            onerror(PermissionError("Unreadable directory"))
            return iter(())
        with patch.object(manifest.os, "walk", side_effect=inaccessible):
            with self.assertRaises(PermissionError):
                manifest.create(self.case)

    def test_malicious_or_malformed_manifest_paths_rejected(self):
        baseline = manifest.create(self.case)
        for name in ("../outside", "/etc/passwd", "C:/file", "nested\\file", "a//b", "./a", ""):
            bad = copy.deepcopy(baseline)
            bad["files"][0]["path"] = name
            with self.subTest(name=name), self.assertRaises(ValueError):
                manifest.verify(self.case, bad)
        bad = copy.deepcopy(baseline)
        bad["files"].append(bad["files"][0])
        with self.assertRaises(ValueError):
            manifest.verify(self.case, bad)
        for key, value in (("size", -1), ("size", True), ("sha256", "not-a-hash")):
            bad = copy.deepcopy(baseline)
            bad["files"][0][key] = value
            with self.assertRaises(ValueError):
                manifest.verify(self.case, bad)

    def test_cli_preserves_baseline_and_signals_differences(self):
        output = self.base / "manifest.json"
        command = [sys.executable, str(ROOT / "src/manifest.py")]
        subprocess.run(command + ["create", str(self.case), str(output)], check=True, capture_output=True)
        original = output.read_bytes()
        repeat = subprocess.run(command + ["create", str(self.case), str(output)], capture_output=True)
        self.assertEqual(repeat.returncode, 1)
        self.assertEqual(original, output.read_bytes())
        subprocess.run(command + ["verify", str(self.case), str(output)], check=True, capture_output=True)
        (self.case / "a.txt").write_bytes(b"changed")
        result = subprocess.run(command + ["verify", str(self.case), str(output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["changed"], ["a.txt"])
        result = subprocess.run(command + ["create", str(self.case), str(self.case / "manifest.json")], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.case / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
