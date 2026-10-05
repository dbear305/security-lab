import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("evidence", ROOT / "src/evidence.py")
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT / "examples/fixture.json").read_text())

    def test_domains(self):
        self.assertEqual(evidence.domain_name(" EXAMPLE.COM. "), "example.com")
        self.assertEqual(evidence.domain_name("bücher.example"), "xn--bcher-kva.example")
        for bad in ("https://example.com", "127.0.0.1", "example.com/a", "*.example.com", "-x.com"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                evidence.domain_name(bad)

    def test_ct_deduplicates_and_retains_wildcards(self):
        rows = evidence.parse_ct(self.fixture["responses"]["ct"], "example.com")
        self.assertEqual([r["value"] for r in rows], ["*.example.com", "example.com", "www.example.com"])
        self.assertEqual(len(rows[-1]["certificate_urls"]), 2)

    def test_dns_dedup_and_nxdomain(self):
        payload = self.fixture["responses"]["dns:A"]
        payload["Answer"] *= 2
        self.assertEqual(len(evidence.parse_dns(payload, "A")), 1)
        self.assertEqual(evidence.parse_dns({"Status": 3}, "A"), [])
        for bad in ({}, {"Status": 2}, {"Status": 0, "TC": True}, {"Status": 0, "Answer": [None]}):
            with self.assertRaises(ValueError):
                evidence.parse_dns(bad, "A")

    def test_offline_collection_never_uses_network(self):
        with patch.object(evidence, "urlopen", side_effect=AssertionError("network")):
            report = evidence.collect("example.com", fixture=self.fixture)
        self.assertTrue(report["complete"])
        self.assertEqual(report["mode"], "synthetic_fixture")
        self.assertEqual(len(report["sources"]), 7)
        self.assertTrue(all(len(s["response_sha256"]) == 64 for s in report["sources"]))

    def test_failed_source_is_not_an_empty_success(self):
        del self.fixture["responses"]["ct"]
        report = evidence.collect("example.com", fixture=self.fixture)
        self.assertFalse(report["complete"])
        self.assertEqual(report["sources"][-1]["status"], "error")
        self.assertTrue(report["observations"])

    def test_http_rate_limit_and_timeout_are_recorded(self):
        for exc in (HTTPError("https://crt.sh", 429, "Too Many Requests", {}, None), TimeoutError("timed out")):
            def fail(url, timeout):
                raise exc
            with patch.object(evidence.time, "sleep"):
                report = evidence.collect("example.com", fetch=fail)
            self.assertFalse(report["complete"])
            self.assertEqual(len(report["sources"]), 7)
            self.assertTrue(all(s["status"] == "error" for s in report["sources"]))

    def test_comparison_does_not_report_outage_as_removal(self):
        old = evidence.collect("example.com", fixture=self.fixture)
        del self.fixture["responses"]["ct"]
        self.fixture["responses"]["dns:A"]["Answer"][0]["data"] = "192.0.2.20"
        new = evidence.collect("example.com", fixture=self.fixture)
        diff = evidence.compare_reports(old, new)
        self.assertEqual(diff["excluded_sources"], ["ct"])
        self.assertEqual(diff["added"], [("dns:A", "example.com", "192.0.2.20")])
        self.assertEqual(diff["removed"], [("dns:A", "example.com", "192.0.2.10")])
        other = copy.deepcopy(old)
        other["domain"] = "another.example"
        with self.assertRaises(ValueError):
            evidence.compare_reports(old, other)
        other = copy.deepcopy(old)
        other["mode"] = "live"
        with self.assertRaises(ValueError):
            evidence.compare_reports(old, other)

    def test_report_escapes_untrusted_records(self):
        report = evidence.collect("example.com", fixture=self.fixture)
        report["observations"].append({"source_id": "dns:TXT", "value": "<script>x</script>|oops\nrow"})
        output = evidence.markdown(report)
        self.assertNotIn("<script>", output)
        self.assertIn("&#124;", output)

    def test_oversized_source_rejected(self):
        with patch.object(evidence, "urlopen") as opened:
            opened.return_value.__enter__.return_value.read.return_value = b"x" * (evidence.MAX_BYTES + 1)
            with self.assertRaisesRegex(ValueError, "10 MiB"):
                evidence.request_json("https://crt.sh", 1)

    def test_cli_writes_reports_and_compares(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, str(ROOT / "src/evidence.py"), "example.com", "--fixture", str(ROOT / "examples/fixture.json"), "--output", directory]
            first = subprocess.run(command, capture_output=True, text=True, check=True)
            report = Path(first.stdout.strip()) / "report.json"
            self.assertTrue(report.with_suffix(".md").exists())
            second = subprocess.run(command + ["--previous", str(report)], capture_output=True, text=True, check=True)
            current = json.loads((Path(second.stdout.strip()) / "report.json").read_text())
            self.assertEqual(current["changes"]["added"], [])
            self.assertEqual(current["changes"]["removed"], [])

    def test_cli_partial_and_invalid_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "fixture.json"
            del self.fixture["responses"]["ct"]
            fixture.write_text(json.dumps(self.fixture))
            command = [sys.executable, str(ROOT / "src/evidence.py"), "example.com", "--fixture", str(fixture), "--output", directory]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertTrue((Path(result.stdout.strip()) / "report.json").exists())
            result = subprocess.run(command + ["--timeout", "nan"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
