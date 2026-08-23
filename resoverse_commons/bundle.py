"""Fail-closed validation for portable capability bundles."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .validator import (
    DuplicateJsonKeyError,
    ID_PATTERN,
    _safe_relative_path,
    load_json_bytes,
    validate_path,
)

SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
TOP_LEVEL_FIELDS = {
    "bundleVersion", "capabilityManifest", "artifact", "inputSchema",
    "outputSchema", "compatibility", "reviewEvidence",
}
FILE_REFERENCE_FIELDS = {"path", "sha256"}
REVIEW_REFERENCE_FIELDS = {"path", "sha256", "actorId", "reviewerId"}
COMPATIBILITY_FIELDS = {"protocol", "range"}
COMPATIBILITY_RANGE_PATTERN = re.compile(
    r"^>=(0|[1-9][0-9]{0,8})\.(0|[1-9][0-9]{0,8}),<(0|[1-9][0-9]{0,8})\.(0|[1-9][0-9]{0,8})$"
)
JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


def _receipt(raw_digest: str | None, reasons: list[str]) -> dict[str, Any]:
    return {
        "bundleReceiptVersion": "1.0",
        "status": "HOLD" if reasons else "PASS",
        "bundleBytesSha256": raw_digest,
        "reasonCodes": sorted(set(reasons)),
        "executionAttempted": False,
        "admissionAuthorized": False,
    }


def _closed_object(
    value: object, expected: set[str], location: str, reasons: list[str]
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        reasons.append(f"INVALID_OBJECT:{location}")
        return None
    for field in sorted(expected - set(value)):
        reasons.append(f"MISSING_REQUIRED_FIELD:{location}.{field}")
    for field in sorted(set(value) - expected):
        reasons.append(f"UNKNOWN_FIELD:{location}.{field}")
    return value


def _resolve_reference(
    root: Path,
    value: object,
    expected: set[str],
    location: str,
    reasons: list[str],
) -> tuple[Path | None, dict[str, Any] | None]:
    reference = _closed_object(value, expected, location, reasons)
    if reference is None:
        return None, None
    relative = reference.get("path")
    digest = reference.get("sha256")
    if not _safe_relative_path(relative):
        reasons.append(f"UNSAFE_BUNDLE_PATH:{location}")
        return None, reference
    if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
        reasons.append(f"INVALID_SHA256:{location}")

    try:
        candidate = (root / relative).resolve(strict=True)
        if not candidate.is_relative_to(root) or not candidate.is_file():
            reasons.append(f"BUNDLE_PATH_OUTSIDE_ROOT:{location}")
            return None, reference
        raw = candidate.read_bytes()
    except (OSError, RuntimeError):
        reasons.append(f"BUNDLE_FILE_READ_FAILED:{location}")
        return None, reference

    if isinstance(digest, str) and hashlib.sha256(raw).hexdigest() != digest:
        reasons.append(f"SHA256_MISMATCH:{location}")
    return candidate, reference


def _parse_json_file(path: Path, location: str, reasons: list[str]) -> object | None:
    try:
        return load_json_bytes(path.read_bytes())
    except DuplicateJsonKeyError as exc:
        reasons.append(f"DUPLICATE_JSON_KEY:{location}:{exc}")
    except (OSError, UnicodeError, json.JSONDecodeError):
        reasons.append(f"INVALID_JSON:{location}")
    return None


def validate_bundle_path(path: Path) -> dict[str, Any]:
    """Validate a bundle and its exact local files without executing any artifact."""

    reasons: list[str] = []
    raw_digest: str | None = None
    try:
        raw = path.read_bytes()
        raw_digest = hashlib.sha256(raw).hexdigest()
        bundle = load_json_bytes(raw)
        root = path.parent.resolve(strict=True)
    except DuplicateJsonKeyError as exc:
        return _receipt(raw_digest, [f"DUPLICATE_JSON_KEY:bundle:{exc}"])
    except (OSError, UnicodeError, json.JSONDecodeError, RuntimeError) as exc:
        return _receipt(raw_digest, [f"BUNDLE_READ_FAILED:{type(exc).__name__}"])

    document = _closed_object(bundle, TOP_LEVEL_FIELDS, "bundle", reasons)
    if document is None:
        return _receipt(raw_digest, reasons)
    if document.get("bundleVersion") != "1.0":
        reasons.append("UNSUPPORTED_BUNDLE_VERSION")

    resolved: dict[str, Path] = {}
    references: dict[str, dict[str, Any]] = {}
    for field in ("capabilityManifest", "artifact", "inputSchema", "outputSchema"):
        candidate, reference = _resolve_reference(
            root, document.get(field), FILE_REFERENCE_FIELDS, field, reasons
        )
        if candidate is not None:
            resolved[field] = candidate
        if reference is not None:
            references[field] = reference

    review_path, review_reference = _resolve_reference(
        root, document.get("reviewEvidence"), REVIEW_REFERENCE_FIELDS, "reviewEvidence", reasons
    )
    if review_path is not None:
        resolved["reviewEvidence"] = review_path
    if review_reference is not None:
        references["reviewEvidence"] = review_reference
        actor = review_reference.get("actorId")
        reviewer = review_reference.get("reviewerId")
        if not isinstance(actor, str) or not ID_PATTERN.fullmatch(actor):
            reasons.append("INVALID_ACTOR_ID")
        if not isinstance(reviewer, str) or not ID_PATTERN.fullmatch(reviewer):
            reasons.append("INVALID_REVIEWER_ID")
        if isinstance(actor, str) and isinstance(reviewer, str) and actor == reviewer:
            reasons.append("REVIEWER_NOT_DISTINCT")

    compatibility = _closed_object(
        document.get("compatibility"), COMPATIBILITY_FIELDS, "compatibility", reasons
    )
    if compatibility is not None:
        if compatibility.get("protocol") != "resoverse-commons":
            reasons.append("UNSUPPORTED_COMPATIBILITY_PROTOCOL")
        compatibility_range = compatibility.get("range")
        range_match = (
            COMPATIBILITY_RANGE_PATTERN.fullmatch(compatibility_range)
            if isinstance(compatibility_range, str)
            else None
        )
        if range_match is None:
            reasons.append("INVALID_COMPATIBILITY_RANGE")
        else:
            lower = (int(range_match.group(1)), int(range_match.group(2)))
            upper = (int(range_match.group(3)), int(range_match.group(4)))
            if lower >= upper:
                reasons.append("INVALID_COMPATIBILITY_RANGE")

    manifest_path = resolved.get("capabilityManifest")
    if manifest_path is not None:
        manifest_receipt = validate_path(manifest_path)
        if manifest_receipt["status"] != "PASS":
            reasons.append("CAPABILITY_MANIFEST_HELD")
        manifest = _parse_json_file(manifest_path, "capabilityManifest", reasons)
        artifact_reference = references.get("artifact")
        if (
            isinstance(manifest, dict)
            and artifact_reference is not None
            and manifest.get("entrypoint") != artifact_reference.get("path")
        ):
            reasons.append("ARTIFACT_ENTRYPOINT_MISMATCH")

    parsed_documents: dict[str, dict[str, Any]] = {}
    for field in ("inputSchema", "outputSchema", "reviewEvidence"):
        candidate = resolved.get(field)
        if candidate is not None:
            parsed = _parse_json_file(candidate, field, reasons)
            if not isinstance(parsed, dict):
                reasons.append(f"JSON_OBJECT_REQUIRED:{field}")
            else:
                parsed_documents[field] = parsed

    review_document = parsed_documents.get("reviewEvidence")
    if review_document is not None and review_reference is not None:
        if (
            review_document.get("actorId") != review_reference.get("actorId")
            or review_document.get("reviewerId") != review_reference.get("reviewerId")
        ):
            reasons.append("REVIEW_IDENTITY_MISMATCH")

    for field in ("inputSchema", "outputSchema"):
        schema = parsed_documents.get(field)
        if schema is not None:
            if schema.get("$schema") != JSON_SCHEMA_DIALECT:
                reasons.append(f"UNSUPPORTED_JSON_SCHEMA_DIALECT:{field}")
            else:
                try:
                    Draft202012Validator.check_schema(schema)
                except Exception:
                    reasons.append(f"INVALID_JSON_SCHEMA:{field}")

    return _receipt(raw_digest, reasons)
