import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


class JsonSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas" / "capability-manifest.schema.json").read_text())
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)
        cls.safe = json.loads((ROOT / "examples" / "local-metadata-reader" / "capability.json").read_text())

    def test_safe_example_is_structurally_valid(self):
        self.assertEqual(list(self.validator.iter_errors(self.safe)), [])

    def test_each_required_field_is_structurally_required(self):
        for field in self.schema["required"]:
            candidate = copy.deepcopy(self.safe)
            del candidate[field]
            self.assertTrue(list(self.validator.iter_errors(candidate)), field)

    def test_schema_role_is_structural_not_policy_authority(self):
        candidate = copy.deepcopy(self.safe)
        candidate["permissions"]["filesystemRead"] = ["../private"]
        self.assertEqual(list(self.validator.iter_errors(candidate)), [])

    def test_receipt_schema_accepts_both_hash_identities(self):
        from resoverse_commons.validator import validate_manifest

        schema = json.loads((ROOT / "schemas" / "evidence-receipt.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        receipt = validate_manifest(self.safe)
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(receipt)), [])

    def test_capability_bundle_schema_is_valid_and_closed(self):
        schema = json.loads((ROOT / "schemas" / "capability-bundle.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        bundle = {
            "bundleVersion": "1.0",
            "capabilityManifest": {"path": "capability.json", "sha256": "c" * 64},
            "artifact": {"path": "implementation.py", "sha256": "a" * 64},
            "inputSchema": {"path": "schemas/input.json", "sha256": "d" * 64},
            "outputSchema": {"path": "schemas/output.json", "sha256": "e" * 64},
            "compatibility": {"protocol": "resoverse-commons", "range": ">=0.2,<0.3"},
            "reviewEvidence": {
                "path": "review.json",
                "sha256": "b" * 64,
                "actorId": "actor",
                "reviewerId": "reviewer",
            },
        }
        validator = Draft202012Validator(schema)
        self.assertEqual(list(validator.iter_errors(bundle)), [])
        bundle["unknown"] = True
        self.assertTrue(list(validator.iter_errors(bundle)))

    def test_bundle_receipt_schema_accepts_validator_output(self):
        from resoverse_commons.bundle import validate_bundle_path

        schema = json.loads((ROOT / "schemas" / "bundle-receipt.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        receipt = validate_bundle_path(
            ROOT / "examples" / "local-metadata-reader" / "bundle.json"
        )
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(receipt)), [])

    def test_reference_input_and_output_schemas_are_valid_draft_2020_12(self):
        for name in ("input.schema.json", "output.schema.json"):
            schema = json.loads(
                (ROOT / "examples" / "local-metadata-reader" / name).read_text()
            )
            self.assertEqual(
                schema.get("$schema"), "https://json-schema.org/draft/2020-12/schema"
            )
            Draft202012Validator.check_schema(schema)


if __name__ == "__main__":
    unittest.main()
