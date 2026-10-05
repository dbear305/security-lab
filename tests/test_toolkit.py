import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("toolkit", ROOT / "src/toolkit.py")
toolkit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toolkit)


class ToolkitTests(unittest.TestCase):
    def test_catalog_and_generated_reference_are_consistent(self):
        rows = toolkit.load_catalog()
        self.assertEqual(set(r["category"] for r in rows), set(toolkit.CATEGORIES))
        self.assertEqual((ROOT / "toolkit/README.md").read_text(encoding="utf-8"), toolkit.markdown(rows))

    def test_filters_combine(self):
        rows = toolkit.select(toolkit.load_catalog(), category="hacking", search="HTTP", starter=True)
        self.assertEqual([r["id"] for r in rows], ["ffuf", "zap"])
        self.assertTrue(all(r["hidden_gem"] for r in toolkit.select(toolkit.load_catalog(), gems=True)))
        self.assertEqual(toolkit.select(rows, search="nonexistent-tool"), [])

    def test_doctor_checks_presence_without_execution(self):
        rows = toolkit.load_catalog()[:3]
        result = toolkit.doctor(rows, which=lambda name: "/test/nmap" if name == "nmap" else None)
        self.assertEqual([r["status"] for r in result], ["found", "missing", "manual"])

    def test_malformed_catalog_is_rejected(self):
        base = {"schema_version": 1, "tools": toolkit.load_catalog()}
        variants = []
        for key, value in (("url", "https://github.com.evil.test/a/b"), ("commands", ["nmap -A"]), ("starter", "yes"), ("category", "unknown")):
            bad = copy.deepcopy(base)
            bad["tools"][0][key] = value
            variants.append(bad)
        bad = copy.deepcopy(base)
        bad["tools"].append(copy.deepcopy(bad["tools"][0]))
        variants.append(bad)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            for bad in variants:
                path.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaises(ValueError):
                    toolkit.load_catalog(path)

    def test_cli_filter_json_and_errors(self):
        command = [sys.executable, str(ROOT / "src/toolkit.py")]
        result = subprocess.run(command + ["list", "--category", "hacking", "--json"], capture_output=True, text=True, check=True)
        rows = json.loads(result.stdout)
        self.assertTrue(rows)
        self.assertTrue(all(r["category"] == "hacking" for r in rows))
        result = subprocess.run(command + ["show", "metasploit"], capture_output=True, text=True, check=True)
        self.assertIn("rapid7/metasploit-framework", result.stdout)
        result = subprocess.run(command + ["show", "unknown"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
