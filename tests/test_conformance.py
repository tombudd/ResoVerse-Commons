import json
import os
import tempfile
import unittest
from pathlib import Path

from resoverse_commons.conformance import run_conformance_corpus


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "resoverse_commons" / "corpus" / "index.json"


class ConformanceCorpusTests(unittest.TestCase):
    def test_published_corpus_passes_without_execution_or_admission(self):
        receipt = run_conformance_corpus(INDEX)
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["declaredCases"], 6)
        self.assertEqual(receipt["completedCases"], 6)
        self.assertEqual(receipt["failures"], [])
        self.assertFalse(receipt["executionAttempted"])
        self.assertFalse(receipt["admissionAuthorized"])

    def test_result_mismatch_holds(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        index["cases"] = [dict(index["cases"][0], expectedStatus="HOLD")]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pass-minimal.json").write_bytes(
                (INDEX.parent / "pass-minimal.json").read_bytes()
            )
            path = root / "index.json"
            path.write_text(json.dumps(index), encoding="utf-8")
            receipt = run_conformance_corpus(path)
        self.assertEqual(receipt["status"], "HOLD")
        self.assertEqual(receipt["failures"][0]["reason"], "STATUS_MISMATCH:HOLD:PASS")

    def test_unsafe_paths_hold(self):
        for relative in ("../outside.json", "C:/outside.json", "."):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                index = {
                    "corpusVersion": "1.0",
                    "cases": [{"id": "unsafe", "manifest": relative,
                               "expectedStatus": "PASS", "expectedReasonCodes": []}],
                }
                path = root / "index.json"
                path.write_text(json.dumps(index), encoding="utf-8")
                receipt = run_conformance_corpus(path)
            self.assertEqual(receipt["status"], "HOLD")

    def test_empty_case_list_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.json"
            path.write_text('{"corpusVersion":"1.0","cases":[]}', encoding="utf-8")
            receipt = run_conformance_corpus(path)
        self.assertEqual(receipt["status"], "HOLD")
        self.assertEqual(receipt["failures"], [{"id": "corpus", "reason": "MISSING_CORPUS_CASES"}])

    @unittest.skipIf(not hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_escape_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "corpus"
            root.mkdir()
            outside = Path(directory) / "outside.json"
            outside.write_text("{}", encoding="utf-8")
            try:
                (root / "escape.json").symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            index = {
                "corpusVersion": "1.0",
                "cases": [{"id": "escape", "manifest": "escape.json",
                           "expectedStatus": "HOLD", "expectedReasonCodes": []}],
            }
            path = root / "index.json"
            path.write_text(json.dumps(index), encoding="utf-8")
            receipt = run_conformance_corpus(path)
        self.assertEqual(receipt["failures"][0]["reason"], "CASE_PATH_OUTSIDE_CORPUS")


if __name__ == "__main__":
    unittest.main()
