import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from resoverse_commons.bundle import validate_bundle_path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "local-metadata-reader"


class BundleValidatorTests(unittest.TestCase):
    def test_reference_bundle_passes_without_execution_or_admission(self):
        receipt = validate_bundle_path(EXAMPLE / "bundle.json")
        self.assertEqual(receipt["status"], "PASS")
        self.assertFalse(receipt["executionAttempted"])
        self.assertFalse(receipt["admissionAuthorized"])

    def _fixture(self, directory: str) -> Path:
        target = Path(directory) / "bundle"
        shutil.copytree(EXAMPLE, target, ignore=shutil.ignore_patterns("__pycache__"))
        return target

    def _bundle(self, root: Path) -> dict:
        return json.loads((root / "bundle.json").read_text(encoding="utf-8"))

    def _write_bundle(self, root: Path, bundle: dict) -> Path:
        path = root / "bundle.json"
        path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
        return path

    def test_hash_mismatch_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture(directory)
            bundle = self._bundle(root)
            bundle["artifact"]["sha256"] = "0" * 64
            receipt = validate_bundle_path(self._write_bundle(root, bundle))
        self.assertIn("SHA256_MISMATCH:artifact", receipt["reasonCodes"])

    def test_traversal_and_windows_drive_paths_hold(self):
        for unsafe in ("../outside.py", "..\\outside.py", "C:/outside.py", "."):
            with self.subTest(unsafe=unsafe), tempfile.TemporaryDirectory() as directory:
                root = self._fixture(directory)
                bundle = self._bundle(root)
                bundle["artifact"]["path"] = unsafe
                receipt = validate_bundle_path(self._write_bundle(root, bundle))
                self.assertIn("UNSAFE_BUNDLE_PATH:artifact", receipt["reasonCodes"])

    @unittest.skipIf(not hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_escape_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture(directory)
            outside = Path(directory) / "outside.py"
            outside.write_text("outside = True\n", encoding="utf-8")
            link = root / "escape.py"
            link.symlink_to(outside)
            bundle = self._bundle(root)
            bundle["artifact"] = {
                "path": "escape.py",
                "sha256": hashlib.sha256(outside.read_bytes()).hexdigest(),
            }
            receipt = validate_bundle_path(self._write_bundle(root, bundle))
        self.assertIn("BUNDLE_PATH_OUTSIDE_ROOT:artifact", receipt["reasonCodes"])

    def test_duplicate_bundle_key_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bundle.json"
            path.write_text('{"bundleVersion":"1.0","bundleVersion":"2.0"}', encoding="utf-8")
            receipt = validate_bundle_path(path)
        self.assertTrue(any(code.startswith("DUPLICATE_JSON_KEY:bundle:") for code in receipt["reasonCodes"]))

    def test_declared_reviewer_must_differ_from_actor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture(directory)
            bundle = self._bundle(root)
            bundle["reviewEvidence"]["reviewerId"] = bundle["reviewEvidence"]["actorId"]
            receipt = validate_bundle_path(self._write_bundle(root, bundle))
        self.assertIn("REVIEWER_NOT_DISTINCT", receipt["reasonCodes"])

    def test_declared_identities_use_portable_grammar(self):
        for reviewer in (" example-implementer", "example-implementer ", "Example Reviewer"):
            with self.subTest(reviewer=reviewer), tempfile.TemporaryDirectory() as directory:
                root = self._fixture(directory)
                bundle = self._bundle(root)
                bundle["reviewEvidence"]["reviewerId"] = reviewer
                receipt = validate_bundle_path(self._write_bundle(root, bundle))
                self.assertIn("INVALID_REVIEWER_ID", receipt["reasonCodes"])

    def test_declared_identities_must_match_bound_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture(directory)
            bundle = self._bundle(root)
            bundle["reviewEvidence"]["reviewerId"] = "different-reviewer"
            receipt = validate_bundle_path(self._write_bundle(root, bundle))
        self.assertIn("REVIEW_IDENTITY_MISMATCH", receipt["reasonCodes"])

    def test_manifest_policy_hold_propagates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture(directory)
            manifest_path = root / "capability.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["permissions"]["network"] = ["https://example.com"]
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            bundle = self._bundle(root)
            bundle["capabilityManifest"]["sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            receipt = validate_bundle_path(self._write_bundle(root, bundle))
        self.assertIn("CAPABILITY_MANIFEST_HELD", receipt["reasonCodes"])

    def test_artifact_must_match_manifest_entrypoint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture(directory)
            alternate = root / "alternate.py"
            alternate.write_text("value = 1\n", encoding="utf-8")
            bundle = self._bundle(root)
            bundle["artifact"] = {
                "path": "alternate.py",
                "sha256": hashlib.sha256(alternate.read_bytes()).hexdigest(),
            }
            receipt = validate_bundle_path(self._write_bundle(root, bundle))
        self.assertIn("ARTIFACT_ENTRYPOINT_MISMATCH", receipt["reasonCodes"])

    def test_input_and_output_must_be_valid_draft_2020_12_schemas(self):
        invalid_schemas = (
            {"not": "a-json-schema"},
            {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "not-a-type"},
        )
        for field, filename in (("inputSchema", "input.schema.json"), ("outputSchema", "output.schema.json")):
            for invalid in invalid_schemas:
                with self.subTest(field=field, invalid=invalid), tempfile.TemporaryDirectory() as directory:
                    root = self._fixture(directory)
                    schema_path = root / filename
                    schema_path.write_text(json.dumps(invalid, indent=2) + "\n", encoding="utf-8")
                    bundle = self._bundle(root)
                    bundle[field]["sha256"] = hashlib.sha256(schema_path.read_bytes()).hexdigest()
                    receipt = validate_bundle_path(self._write_bundle(root, bundle))
                    self.assertTrue(
                        f"UNSUPPORTED_JSON_SCHEMA_DIALECT:{field}" in receipt["reasonCodes"]
                        or f"INVALID_JSON_SCHEMA:{field}" in receipt["reasonCodes"]
                    )

    def test_compatibility_range_uses_closed_v1_grammar(self):
        for value in (
            "nonsense", "*", ">=0.2", ">=0.2.0,<0.3.0", ">=1.0,<1.0",
            ">=2.0,<1.0", f">={'1' * 5000}.0,<2.0",
        ):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                root = self._fixture(directory)
                bundle = self._bundle(root)
                bundle["compatibility"]["range"] = value
                receipt = validate_bundle_path(self._write_bundle(root, bundle))
                self.assertIn("INVALID_COMPATIBILITY_RANGE", receipt["reasonCodes"])


if __name__ == "__main__":
    unittest.main()
