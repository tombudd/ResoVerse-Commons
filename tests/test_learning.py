import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from resoverse_commons.cli import main
from resoverse_commons.learning import validate_learning_candidate


def candidate():
    return {"candidateVersion": "1.0", "id": "counterexample-1", "provenance": {"sourceUrl": "https://example.com/source", "license": "Apache-2.0", "authors": ["Contributor"], "rightsToSubmit": True}, "artifacts": [{"path": "fixture.json", "sha256": "a" * 64}], "learningUse": {"consent": "explicit_learning_candidate", "intendedUse": "counterexample", "automaticPromotion": False}, "revocation": {"supported": True, "contact": "security@example.com"}}


class LearningCandidateTests(unittest.TestCase):
    def test_valid_candidate_waits_for_review_without_changing_the_project(self):
        receipt = validate_learning_candidate(candidate())
        self.assertEqual(receipt["status"], "waiting_for_review")
        self.assertFalse(receipt["addedToProject"])
        self.assertFalse(receipt["softwareChanged"])
        self.assertFalse(receipt["codeRun"])

    def test_consent_and_revocation_are_required(self):
        value = candidate()
        value["learningUse"]["consent"] = "implicit"
        value["revocation"]["supported"] = False
        receipt = validate_learning_candidate(value)
        self.assertEqual(receipt["status"], "needs_changes")
        self.assertIn("EXPLICIT_LEARNING_CONSENT_REQUIRED", receipt["reasonCodes"])
        self.assertIn("REVOCATION_PATH_REQUIRED", receipt["reasonCodes"])

    def test_artifact_requires_a_safe_path_and_hex_digest(self):
        value = candidate()
        value["artifacts"][0]["path"] = "../fixture.json"
        value["artifacts"][0]["sha256"] = "g" * 64
        receipt = validate_learning_candidate(value)
        self.assertEqual(receipt["status"], "needs_changes")
        self.assertIn("INVALID_ARTIFACTS", receipt["reasonCodes"])

    def test_recursive_input_returns_a_receipt(self):
        value = candidate()
        value["recursive"] = value
        receipt = validate_learning_candidate(value)
        self.assertEqual(receipt["status"], "needs_changes")
        self.assertIsNone(receipt["canonicalCandidateSha256"])

    def test_cli_rejects_malformed_and_duplicate_key_input(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, contents, expected_reason in (
                ("malformed.json", "{", "CANDIDATE_READ_ERROR:JSONDecodeError"),
                ("duplicate.json", '{"id":"one","id":"two"}', "DUPLICATE_JSON_KEY:id"),
            ):
                path = Path(directory) / name
                path.write_text(contents, encoding="utf-8")
                output = io.StringIO()
                with patch.object(sys, "argv", ["resoverse-commons", "validate-learning-candidate", str(path)]), redirect_stdout(output):
                    self.assertEqual(main(), 2)
                receipt = json.loads(output.getvalue())
                self.assertEqual(receipt["status"], "needs_changes")
                self.assertIn(expected_reason, receipt["reasonCodes"])

    def test_cli_handles_deeply_nested_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested.json"
            depth = sys.getrecursionlimit() + 10
            path.write_text("[" * depth + "0" + "]" * depth, encoding="utf-8")
            output = io.StringIO()
            with patch.object(sys, "argv", ["resoverse-commons", "validate-learning-candidate", str(path)]), redirect_stdout(output):
                self.assertEqual(main(), 2)
            receipt = json.loads(output.getvalue())
            self.assertEqual(receipt["status"], "needs_changes")
            self.assertIn("CANDIDATE_MUST_BE_OBJECT", receipt["reasonCodes"])
            self.assertIsNotNone(receipt["canonicalCandidateSha256"])

    def test_cli_handles_decoder_recursion_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.json"
            path.write_text("{}", encoding="utf-8")
            output = io.StringIO()
            with patch("resoverse_commons.cli.load_json_bytes", side_effect=RecursionError), patch.object(sys, "argv", ["resoverse-commons", "validate-learning-candidate", str(path)]), redirect_stdout(output):
                self.assertEqual(main(), 2)
            receipt = json.loads(output.getvalue())
            self.assertEqual(receipt["reasonCodes"], ["CANDIDATE_READ_ERROR:RecursionError"])
