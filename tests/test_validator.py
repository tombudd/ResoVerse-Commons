import copy
import json
import random
import sys
import tempfile
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
            "https://[::1",
            "https://example.com:bad",
            "https://@",
            "https://user@:443",
            "https://user:password@example.com",
            "https://%zz/path",
            "https://-invalid.example/path",
            "https://invalid-.example/path",
            "https://under_score.example/path",
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
        for value in (
            ["/"], ["../private"], ["..\\private"], ["C:/Windows/*"], ["."],
            ["./fixtures/data.json"], ["fixtures//data.json"], "fixtures/*.json",
        ):
            manifest = load_example("local-metadata-reader")
            manifest["permissions"]["filesystemRead"] = value
            self.assertIn("INVALID_FILESYSTEM_READ_SCOPE", validate_manifest(manifest)["reasonCodes"])

    def test_windows_drive_entrypoint_is_held(self):
        manifest = load_example("local-metadata-reader")
        manifest["entrypoint"] = "C:/Windows/system.ini"
        self.assertIn("UNSAFE_ENTRYPOINT_PATH", validate_manifest(manifest)["reasonCodes"])

    def test_control_bearing_paths_are_held(self):
        for value in ("foo\x00.py", "foo\nbar.py", "scope\x7f.json"):
            manifest = load_example("local-metadata-reader")
            manifest["entrypoint"] = value
            self.assertIn("UNSAFE_ENTRYPOINT_PATH", validate_manifest(manifest)["reasonCodes"])
            manifest = load_example("local-metadata-reader")
            manifest["permissions"]["filesystemRead"] = [value]
            self.assertIn("INVALID_FILESYSTEM_READ_SCOPE", validate_manifest(manifest)["reasonCodes"])

    def test_non_object_hashes_preserve_input_identity(self):
        first = validate_manifest([])
        second = validate_manifest([1])
        self.assertEqual(first["status"], "HOLD")
        self.assertNotEqual(first["canonicalManifestSha256"], second["canonicalManifestSha256"])

    def test_validate_path_hashes_exact_submitted_bytes(self):
        path = ROOT / "examples" / "local-metadata-reader" / "capability.json"
        import hashlib
        receipt = validate_path(path)
        self.assertEqual(receipt["submittedBytesSha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(
            receipt["canonicalManifestSha256"],
            validate_manifest(load_example("local-metadata-reader"))["canonicalManifestSha256"],
        )

    def test_duplicate_json_keys_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"schemaVersion":"bad","schemaVersion":"1.0"}', encoding="utf-8")
            receipt = validate_path(path)
        self.assertEqual(receipt["status"], "HOLD")
        self.assertTrue(any(code.startswith("DUPLICATE_JSON_KEY:") for code in receipt["reasonCodes"]))

    def test_non_json_python_objects_hold_without_exception(self):
        for value in ({1: "x", "two": 2}, {"x": {1, 2}}, object(), float("nan")):
            receipt = validate_manifest(value)
            self.assertEqual(receipt["status"], "HOLD")
            self.assertIn("INPUT_NOT_JSON_COMPATIBLE", receipt["reasonCodes"])
            self.assertIsNone(receipt["canonicalManifestSha256"])

    def test_excessively_nested_input_holds_without_exception(self):
        value = []
        for _ in range(1500):
            value = [value]
        receipt = validate_manifest(value)
        self.assertEqual(receipt["status"], "HOLD")
        self.assertIn("INPUT_NOT_JSON_COMPATIBLE", receipt["reasonCodes"])

    def test_arbitrary_json_roots_always_return_receipts(self):
        for value in (None, True, False, 0, 1.5, "text", [], [1], {}, {"x": [None, True, 3]}):
            receipt = validate_manifest(value)
            self.assertIn(receipt["status"], {"PASS", "HOLD"})
            self.assertEqual(len(receipt["canonicalManifestSha256"]), 64)

    def test_deterministic_generated_json_inputs_never_raise(self):
        generator = random.Random(20260823)

        def value(depth=0):
            primitives = [None, True, False, generator.randint(-1000, 1000), "text"]
            if depth >= 4:
                return generator.choice(primitives)
            choice = generator.randrange(3)
            if choice == 0:
                return generator.choice(primitives)
            if choice == 1:
                return [value(depth + 1) for _ in range(generator.randrange(5))]
            return {f"key-{index}": value(depth + 1) for index in range(generator.randrange(5))}

        for _ in range(1000):
            candidate = value()
            first = validate_manifest(candidate)
            second = validate_manifest(candidate)
            self.assertEqual(first, second)
            self.assertIn(first["status"], {"PASS", "HOLD"})

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
        self.assertRegex(receipt["canonicalManifestSha256"], r"^[a-f0-9]{64}$")
        self.assertIsNone(receipt["submittedBytesSha256"])
        self.assertIn(receipt["status"], schema["properties"]["status"]["enum"])


if __name__ == "__main__":
    unittest.main()
