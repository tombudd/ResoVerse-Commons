# Validator Reason Codes

The validator returns sorted, unique reason codes. Any reason produces
`HOLD`; absence of reasons produces `PASS`. Neither result grants runtime or
promotion authority.

| Code or prefix | Meaning |
| --- | --- |
| `INPUT_NOT_JSON_COMPATIBLE` | The Python API received a value outside the JSON data model. |
| `MANIFEST_MUST_BE_OBJECT` | The JSON root is not an object. |
| `MISSING_REQUIRED_FIELD:*` | A required field is absent. |
| `UNKNOWN_FIELD:*` | A closed-contract object contains an unknown field. |
| `UNSUPPORTED_SCHEMA_VERSION` | The manifest does not declare schema `1.0`. |
| `INVALID_CAPABILITY_ID` | The identifier is outside the lowercase portable form. |
| `INVALID_SEMANTIC_VERSION` | The version is not ASCII `major.minor.patch`. |
| `INVALID_NAME`, `INVALID_DESCRIPTION` | Human-readable metadata is absent or malformed. |
| `UNSAFE_ENTRYPOINT_PATH` | The entrypoint is absolute, traversing, drive-qualified, backslash-bearing, blank, or nonprintable. |
| `V1_DEPENDENCIES_PROHIBITED` | V1 requires the exact declaration `dependencies: []`. |
| `INVALID_PROVENANCE`, `INVALID_SOURCE_URL`, `INVALID_LICENSE`, `MISSING_AUTHORS` | Provenance is incomplete or malformed. |
| `RIGHTS_TO_SUBMIT_NOT_CERTIFIED` | The contributor did not certify submission rights. |
| `INVALID_PERMISSIONS` | The permission object is malformed. |
| `V1_NETWORK_PERMISSION_DENIED` | V1 does not admit network permission. |
| `INVALID_FILESYSTEM_READ_SCOPE` | A read scope is malformed or unsafe. |
| `V1_FILESYSTEM_WRITE_PERMISSION_DENIED` | V1 does not admit filesystem writes. |
| `V1_ENVIRONMENT_ACCESS_DENIED` | V1 does not admit environment access. |
| `V1_SUBPROCESS_PERMISSION_DENIED` | V1 does not admit subprocess creation. |
| `INVALID_LIMITS`, `INVALID_WALL_TIME_LIMIT`, `INVALID_MEMORY_LIMIT` | Resource limits are absent or outside V1 bounds. |
| `INVALID_LEARNING_USE`, `INVALID_LEARNING_INPUTS` | Learning-use declarations are malformed, duplicated, or unsupported. |
| `AUTOMATIC_PROMOTION_PROHIBITED` | Automatic promotion must be false. |
| `EXPLICIT_CONTRIBUTION_CONSENT_REQUIRED` | Explicit contribution consent is absent. |
| `MANIFEST_READ_FAILED:*` | File reading, decoding, or JSON parsing failed. |
| `DUPLICATE_JSON_KEY:*` | A JSON object repeats a key and is rejected before interpretation. |
| `BUNDLE_READ_FAILED:*` | The bundle itself could not be read, decoded, or parsed. |
| `INVALID_OBJECT:*`, `UNSUPPORTED_BUNDLE_VERSION` | A bundle object is malformed or uses an unsupported version. |
| `UNSAFE_BUNDLE_PATH:*`, `BUNDLE_PATH_OUTSIDE_ROOT:*`, `BUNDLE_FILE_READ_FAILED:*` | A referenced file path is non-canonical, unsafe, escaping, absent, or unreadable. |
| `INVALID_SHA256:*`, `SHA256_MISMATCH:*` | A declared byte identity is malformed or does not match the file. |
| `INVALID_JSON:*`, `JSON_OBJECT_REQUIRED:*` | A referenced JSON contract is malformed or is not an object. |
| `INVALID_ACTOR_ID`, `INVALID_REVIEWER_ID`, `REVIEWER_NOT_DISTINCT` | Declared review identities are absent, outside the portable identifier grammar, or not distinct. This does not authenticate identity. |
| `REVIEW_IDENTITY_MISMATCH` | The bundle's declared identities do not match the byte-bound review receipt. |
| `UNSUPPORTED_COMPATIBILITY_PROTOCOL`, `INVALID_COMPATIBILITY_RANGE` | The compatibility declaration is unsupported or malformed. |
| `UNSUPPORTED_JSON_SCHEMA_DIALECT:*`, `INVALID_JSON_SCHEMA:*` | An input/output schema does not declare or conform to Draft 2020-12. |
| `CAPABILITY_MANIFEST_HELD` | The referenced manifest failed authoritative policy validation. |
| `ARTIFACT_ENTRYPOINT_MISMATCH` | The byte-bound artifact is not the manifest entrypoint. |
