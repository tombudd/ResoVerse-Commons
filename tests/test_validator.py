import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from resoverse_commons.validator import (  # noqa: E402
    LEARNING_FIELDS,
    LIMIT_FIELDS,
    PERMISSION_FIELDS,
    PROVENANCE_FIELDS,
    TOP_LEVEL_FIELDS,
    validate_manifest,
    validate_path,
)


def load_example(name: str) -> dict:
    path = ROOT / "examples" / name / "capability.json"
    return json.loads(path.read_text(encoding="utf-8"))


class ValidatorTests(unittest.TestCase):
    def test_safe_reference_passes_without_execution(self):
        receipt = validate_manifest(load_example("local-metadata-reader"))
        self.assertEqual(receipt["status"], "PASS")
        self.assertFalse(receipt["executionAttempted"])
        self.assertFalse(receipt["memoryPromotionAuthorized"])

    def test_adversarial_capability_is_held(self):
        receipt = validate_manifest(load_example("adversarial-unsafe-capability"))
        self.assertEqual(receipt["status"], "HOLD")
        self.assertIn("V1_NETWORK_PERMISSION_DENIED", receipt["reasonCodes"])
        self.assertIn("AUTOMATIC_PROMOTION_PROHIBITED", receipt["reasonCodes"])
        self.assertIn("RIGHTS_TO_SUBMIT_NOT_CERTIFIED", receipt["reasonCodes"])

    def test_path_escape_is_held(self):
        manifest = load_example("local-metadata-reader")
        manifest["entrypoint"] = "../escape.py"
        self.assertIn("UNSAFE_ENTRYPOINT_PATH", validate_manifest(manifest)["reasonCodes"])

        manifest["entrypoint"] = "..\\escape.py"
        self.assertIn("UNSAFE_ENTRYPOINT_PATH", validate_manifest(manifest)["reasonCodes"])

    def test_rights_certification_is_required(self):
        manifest = copy.deepcopy(load_example("local-metadata-reader"))
        manifest["provenance"]["rightsToSubmit"] = False
        self.assertIn("RIGHTS_TO_SUBMIT_NOT_CERTIFIED", validate_manifest(manifest)["reasonCodes"])

    def test_receipt_is_deterministic(self):
        manifest = load_example("local-metadata-reader")
        self.assertEqual(validate_manifest(manifest), validate_manifest(manifest))

    def test_every_required_field_is_enforced(self):
        source = load_example("local-metadata-reader")
        for field in source:
            manifest = copy.deepcopy(source)
            del manifest[field]
            self.assertEqual(validate_manifest(manifest)["status"], "HOLD", field)

    def test_unknown_and_invalid_fields_are_held(self):
        manifest = load_example("local-metadata-reader")
        manifest["unknown"] = True
        self.assertIn("UNKNOWN_FIELD:manifest.unknown", validate_manifest(manifest)["reasonCodes"])

        manifest = load_example("local-metadata-reader")
        manifest["name"] = ""
        self.assertIn("INVALID_NAME", validate_manifest(manifest)["reasonCodes"])

        manifest = load_example("local-metadata-reader")
        del manifest["permissions"]["network"]
        self.assertIn("MISSING_REQUIRED_FIELD:permissions.network", validate_manifest(manifest)["reasonCodes"])

    def test_semver_is_ascii_only(self):
        manifest = load_example("local-metadata-reader")
        manifest["version"] = "1١.0.0"
        self.assertIn("INVALID_SEMANTIC_VERSION", validate_manifest(manifest)["reasonCodes"])

    def test_source_url_rejects_whitespace_and_controls(self):
        for value in (
            "https://exa mple.com",
            "https://example.com/has space",
            "https://example.com/line\nbreak",
            "https://example.com/\x7f",
            "https://example.com/\x80",
        ):
            manifest = load_example("local-metadata-reader")
            manifest["provenance"]["sourceUrl"] = value
            self.assertIn("INVALID_SOURCE_URL", validate_manifest(manifest)["reasonCodes"])

    def test_malformed_nested_learning_input_holds_without_exception(self):
        manifest = load_example("local-metadata-reader")
        manifest["learningUse"]["allowedInputs"] = [{}]
        self.assertIn("INVALID_LEARNING_INPUTS", validate_manifest(manifest)["reasonCodes"])

    def test_telemetry_is_excluded_from_v1(self):
        manifest = load_example("local-metadata-reader")
        manifest["learningUse"]["allowedInputs"] = ["telemetry"]
        self.assertIn("INVALID_LEARNING_INPUTS", validate_manifest(manifest)["reasonCodes"])

    def test_duplicate_learning_inputs_are_held(self):
        manifest = load_example("local-metadata-reader")
        manifest["learningUse"]["allowedInputs"] = ["source_code", "source_code"]
        self.assertIn("INVALID_LEARNING_INPUTS", validate_manifest(manifest)["reasonCodes"])

    def test_v1_requires_explicit_zero_dependencies(self):
        manifest = load_example("local-metadata-reader")
        manifest["dependencies"] = ["package"]
        self.assertIn("V1_DEPENDENCIES_PROHIBITED", validate_manifest(manifest)["reasonCodes"])

    def test_filesystem_reads_must_be_narrow_relative_paths(self):
        for value in (["/"], ["../private"], ["..\\private"], ["C:/Windows/*"], ["."], "fixtures/*.json"):
            manifest = load_example("local-metadata-reader")
            manifest["permissions"]["filesystemRead"] = value
            self.assertIn("INVALID_FILESYSTEM_READ_SCOPE", validate_manifest(manifest)["reasonCodes"])

    def test_windows_drive_entrypoint_is_held(self):
        manifest = load_example("local-metadata-reader")
        manifest["entrypoint"] = "C:/Windows/system.ini"
        self.assertIn("UNSAFE_ENTRYPOINT_PATH", validate_manifest(manifest)["reasonCodes"])

    def test_non_object_hashes_preserve_input_identity(self):
        first = validate_manifest([])
        second = validate_manifest([1])
        self.assertEqual(first["status"], "HOLD")
        self.assertNotEqual(first["manifestSha256"], second["manifestSha256"])

    def test_validate_path_hashes_exact_submitted_bytes(self):
        path = ROOT / "examples" / "local-metadata-reader" / "capability.json"
        import hashlib
        self.assertEqual(validate_path(path)["manifestSha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_reference_implementation(self):
        import importlib.util
        path = ROOT / "examples" / "local-metadata-reader" / "implementation.py"
        spec = importlib.util.spec_from_file_location("reference_implementation", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        self.assertEqual(module.extract_metadata({"id": "x", "ignored": 3}), {"status": "PASS", "metadata": {"id": "x"}})

    def test_schema_and_validator_field_contracts_match(self):
        schema = json.loads((ROOT / "schemas" / "capability-manifest.schema.json").read_text())
        self.assertEqual(set(schema["required"]), TOP_LEVEL_FIELDS)
        self.assertEqual(set(schema["properties"]), TOP_LEVEL_FIELDS)
        mappings = {
            "provenance": PROVENANCE_FIELDS,
            "permissions": PERMISSION_FIELDS,
            "limits": LIMIT_FIELDS,
            "learningUse": LEARNING_FIELDS,
        }
        for field, expected in mappings.items():
            child = schema["properties"][field]
            self.assertEqual(set(child["required"]), expected)
            self.assertEqual(set(child["properties"]), expected)

    def test_receipt_matches_published_contract_shape(self):
        schema = json.loads((ROOT / "schemas" / "evidence-receipt.schema.json").read_text())
        receipt = validate_manifest(load_example("local-metadata-reader"))
        self.assertEqual(set(receipt), set(schema["required"]))
        self.assertRegex(receipt["manifestSha256"], r"^[a-f0-9]{64}$")
        self.assertIn(receipt["status"], schema["properties"]["status"]["enum"])


if __name__ == "__main__":
    unittest.main()
