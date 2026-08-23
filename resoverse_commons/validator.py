"""Deterministic capability-manifest validation with fail-closed policy checks."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import math
import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import urlsplit
from typing import Any

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
LEARNING_INPUTS = {"source_code", "evaluations", "counterexamples"}
TOP_LEVEL_FIELDS = {
    "schemaVersion", "id", "version", "name", "description", "entrypoint",
    "provenance", "dependencies", "permissions", "limits", "learningUse",
}
PROVENANCE_FIELDS = {"sourceUrl", "license", "authors", "rightsToSubmit"}
PERMISSION_FIELDS = {"network", "filesystemRead", "filesystemWrite", "environment", "subprocess"}
LIMIT_FIELDS = {"wallTimeSeconds", "memoryMiB"}
LEARNING_FIELDS = {"allowedInputs", "consent", "automaticPromotion"}


class DuplicateJsonKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateJsonKeyError(key)
        value[key] = item
    return value


def load_json_bytes(raw: bytes) -> object:
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _safe_relative_path(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if not all(character.isprintable() for character in value):
        return False
    if "\\" in value:
        return False
    path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    return (
        value != "."
        and path.as_posix() == value
        and not path.is_absolute()
        and not windows_path.drive
        and ".." not in path.parts
    )


def _json_compatible(value: object) -> bool:
    if value is None or isinstance(value, (bool, str, int)):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(_json_compatible(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _json_compatible(item) for key, item in value.items())
    return False


def _valid_source_url(value: object) -> bool:
    if not isinstance(value, str) or not value or any(not 33 <= ord(character) <= 126 for character in value):
        return False
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        parsed.port
    except (TypeError, ValueError, UnicodeError):
        return False
    valid_hostname = False
    if hostname:
        try:
            ipaddress.ip_address(hostname)
            valid_hostname = True
        except ValueError:
            labels = hostname[:-1].split(".") if hostname.endswith(".") else hostname.split(".")
            valid_hostname = (
                len(hostname) <= 253
                and all(
                    label
                    and len(label) <= 63
                    and re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
                    for label in labels
                )
            )
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.netloc)
        and valid_hostname
        and parsed.username is None
        and parsed.password is None
    )


def _unknown_fields(value: dict[str, Any], allowed: set[str], location: str) -> list[str]:
    return [f"UNKNOWN_FIELD:{location}.{field}" for field in sorted(set(value) - allowed)]


def validate_manifest(manifest: object) -> dict[str, Any]:
    """Return a stable PASS/HOLD receipt; never execute the declared capability."""

    reasons: list[str] = []
    canonical_digest: str | None = None
    try:
        compatible = _json_compatible(manifest)
        canonical_digest = hashlib.sha256(_canonical_bytes(manifest)).hexdigest() if compatible else None
    except (RecursionError, TypeError, ValueError):
        compatible = False
        canonical_digest = None
    if not compatible:
        reasons.append("INPUT_NOT_JSON_COMPATIBLE")
        manifest = {}
    if not isinstance(manifest, dict):
        manifest = {}
        reasons.append("MANIFEST_MUST_BE_OBJECT")

    reasons.extend(_unknown_fields(manifest, TOP_LEVEL_FIELDS, "manifest"))
    for field in sorted(TOP_LEVEL_FIELDS - set(manifest)):
        reasons.append(f"MISSING_REQUIRED_FIELD:{field}")

    if manifest.get("schemaVersion") != "1.0":
        reasons.append("UNSUPPORTED_SCHEMA_VERSION")
    if not isinstance(manifest.get("id"), str) or not ID_PATTERN.fullmatch(manifest.get("id", "")):
        reasons.append("INVALID_CAPABILITY_ID")
    if not isinstance(manifest.get("version"), str) or not SEMVER_PATTERN.fullmatch(manifest.get("version", "")):
        reasons.append("INVALID_SEMANTIC_VERSION")
    if not isinstance(manifest.get("name"), str) or not manifest.get("name", "").strip():
        reasons.append("INVALID_NAME")
    if not isinstance(manifest.get("description"), str) or len(manifest.get("description", "").strip()) < 20:
        reasons.append("INVALID_DESCRIPTION")
    if not _safe_relative_path(manifest.get("entrypoint")):
        reasons.append("UNSAFE_ENTRYPOINT_PATH")

    dependencies = manifest.get("dependencies")
    if dependencies != []:
        reasons.append("V1_DEPENDENCIES_PROHIBITED")

    provenance = manifest.get("provenance")
    if not isinstance(provenance, dict):
        reasons.append("INVALID_PROVENANCE")
    else:
        reasons.extend(_unknown_fields(provenance, PROVENANCE_FIELDS, "provenance"))
        for field in sorted(PROVENANCE_FIELDS - set(provenance)):
            reasons.append(f"MISSING_REQUIRED_FIELD:provenance.{field}")
        source_url = provenance.get("sourceUrl")
        if not _valid_source_url(source_url):
            reasons.append("INVALID_SOURCE_URL")
        if not isinstance(provenance.get("license"), str) or not provenance.get("license", "").strip():
            reasons.append("INVALID_LICENSE")
        authors = provenance.get("authors")
        if not isinstance(authors, list) or not authors or not all(isinstance(x, str) and x.strip() for x in authors):
            reasons.append("MISSING_AUTHORS")
        if provenance.get("rightsToSubmit") is not True:
            reasons.append("RIGHTS_TO_SUBMIT_NOT_CERTIFIED")

    permissions = manifest.get("permissions")
    if not isinstance(permissions, dict):
        reasons.append("INVALID_PERMISSIONS")
    else:
        reasons.extend(_unknown_fields(permissions, PERMISSION_FIELDS, "permissions"))
        for field in sorted(PERMISSION_FIELDS - set(permissions)):
            reasons.append(f"MISSING_REQUIRED_FIELD:permissions.{field}")
        network = permissions.get("network", [])
        filesystem_read = permissions.get("filesystemRead")
        filesystem_write = permissions.get("filesystemWrite", [])
        environment = permissions.get("environment", [])
        if network != []:
            reasons.append("V1_NETWORK_PERMISSION_DENIED")
        if not isinstance(filesystem_read, list) or not all(_safe_relative_path(x) for x in filesystem_read):
            reasons.append("INVALID_FILESYSTEM_READ_SCOPE")
        if filesystem_write != []:
            reasons.append("V1_FILESYSTEM_WRITE_PERMISSION_DENIED")
        if environment != []:
            reasons.append("V1_ENVIRONMENT_ACCESS_DENIED")
        if permissions.get("subprocess") is not False:
            reasons.append("V1_SUBPROCESS_PERMISSION_DENIED")

    limits = manifest.get("limits")
    if not isinstance(limits, dict):
        reasons.append("INVALID_LIMITS")
    else:
        reasons.extend(_unknown_fields(limits, LIMIT_FIELDS, "limits"))
        for field in sorted(LIMIT_FIELDS - set(limits)):
            reasons.append(f"MISSING_REQUIRED_FIELD:limits.{field}")
        wall_time = limits.get("wallTimeSeconds")
        memory = limits.get("memoryMiB")
        if not isinstance(wall_time, int) or isinstance(wall_time, bool) or not 1 <= wall_time <= 30:
            reasons.append("INVALID_WALL_TIME_LIMIT")
        if not isinstance(memory, int) or isinstance(memory, bool) or not 16 <= memory <= 512:
            reasons.append("INVALID_MEMORY_LIMIT")

    learning_use = manifest.get("learningUse")
    if not isinstance(learning_use, dict):
        reasons.append("INVALID_LEARNING_USE")
    else:
        reasons.extend(_unknown_fields(learning_use, LEARNING_FIELDS, "learningUse"))
        for field in sorted(LEARNING_FIELDS - set(learning_use)):
            reasons.append(f"MISSING_REQUIRED_FIELD:learningUse.{field}")
        allowed = learning_use.get("allowedInputs")
        if (
            not isinstance(allowed, list)
            or not all(isinstance(x, str) for x in allowed)
            or len(allowed) != len(set(allowed))
            or not set(allowed).issubset(LEARNING_INPUTS)
        ):
            reasons.append("INVALID_LEARNING_INPUTS")
        if learning_use.get("automaticPromotion") is not False:
            reasons.append("AUTOMATIC_PROMOTION_PROHIBITED")
        if learning_use.get("consent") != "explicit_contribution":
            reasons.append("EXPLICIT_CONTRIBUTION_CONSENT_REQUIRED")

    return {
        "receiptVersion": "1.0",
        "status": "HOLD" if reasons else "PASS",
        "canonicalManifestSha256": canonical_digest,
        "submittedBytesSha256": None,
        "reasonCodes": sorted(set(reasons)),
        "executionAttempted": False,
        "memoryPromotionAuthorized": False,
        "productionActivationAuthorized": False,
    }


def validate_path(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        raw_digest = hashlib.sha256(raw).hexdigest()
        value = load_json_bytes(raw)
    except DuplicateJsonKeyError as exc:
        return {
            "receiptVersion": "1.0",
            "status": "HOLD",
            "canonicalManifestSha256": None,
            "submittedBytesSha256": hashlib.sha256(raw).hexdigest(),
            "reasonCodes": [f"DUPLICATE_JSON_KEY:{exc}"],
            "executionAttempted": False,
            "memoryPromotionAuthorized": False,
            "productionActivationAuthorized": False,
        }
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {
            "receiptVersion": "1.0",
            "status": "HOLD",
            "canonicalManifestSha256": None,
            "submittedBytesSha256": hashlib.sha256(raw).hexdigest() if "raw" in locals() else None,
            "reasonCodes": [f"MANIFEST_READ_FAILED:{type(exc).__name__}"],
            "executionAttempted": False,
            "memoryPromotionAuthorized": False,
            "productionActivationAuthorized": False,
        }
    receipt = validate_manifest(value)
    receipt["submittedBytesSha256"] = raw_digest
    return receipt
