"""Fail-closed, non-authorizing intake for opt-in learning candidates."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .validator import _safe_relative_path, _valid_source_url


TOP_LEVEL_FIELDS = {"candidateVersion", "id", "provenance", "artifacts", "learningUse", "revocation"}
PROVENANCE_FIELDS = {"sourceUrl", "license", "authors", "rightsToSubmit"}
LEARNING_FIELDS = {"consent", "intendedUse", "automaticPromotion"}
REVOCATION_FIELDS = {"supported", "contact"}
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def _canonical_sha256(value: object) -> str | None:
    try:
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    except (RecursionError, TypeError, ValueError):
        return None


def _invalid_receipt(reason: str) -> dict[str, Any]:
    return {
        "receiptVersion": "1.0",
        "status": "needs_changes",
        "candidateId": None,
        "canonicalCandidateSha256": None,
        "reasonCodes": [reason],
        "addedToProject": False,
        "softwareChanged": False,
        "codeRun": False,
    }


def validate_learning_candidate(candidate: object) -> dict[str, Any]:
    """Return a review receipt without running or using the submission."""

    reasons: list[str] = []
    if not isinstance(candidate, dict):
        candidate = {}
        reasons.append("CANDIDATE_MUST_BE_OBJECT")
    if set(candidate) != TOP_LEVEL_FIELDS:
        reasons.append("INVALID_CANDIDATE_FIELDS")
    if candidate.get("candidateVersion") != "1.0":
        reasons.append("UNSUPPORTED_CANDIDATE_VERSION")
    candidate_id = candidate.get("id")
    if not isinstance(candidate_id, str) or not candidate_id or not candidate_id.isascii() or not candidate_id.replace("-", "").replace("_", "").isalnum():
        reasons.append("INVALID_CANDIDATE_ID")

    provenance = candidate.get("provenance")
    if not isinstance(provenance, dict) or set(provenance) != PROVENANCE_FIELDS:
        reasons.append("INVALID_PROVENANCE")
    else:
        if not _valid_source_url(provenance.get("sourceUrl")):
            reasons.append("INVALID_SOURCE_URL")
        if not isinstance(provenance.get("license"), str) or not provenance["license"].strip():
            reasons.append("INVALID_LICENSE")
        if not isinstance(provenance.get("authors"), list) or not provenance["authors"] or not all(isinstance(author, str) and author.strip() for author in provenance["authors"]):
            reasons.append("MISSING_AUTHORS")
        if provenance.get("rightsToSubmit") is not True:
            reasons.append("RIGHTS_TO_SUBMIT_NOT_CERTIFIED")

    artifacts = candidate.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts or not all(isinstance(item, dict) and set(item) == {"path", "sha256"} and _safe_relative_path(item["path"]) and isinstance(item["sha256"], str) and SHA256_PATTERN.fullmatch(item["sha256"]) for item in artifacts):
        reasons.append("INVALID_ARTIFACTS")

    learning = candidate.get("learningUse")
    if not isinstance(learning, dict) or set(learning) != LEARNING_FIELDS:
        reasons.append("INVALID_LEARNING_USE")
    else:
        if learning.get("consent") != "explicit_learning_candidate":
            reasons.append("EXPLICIT_LEARNING_CONSENT_REQUIRED")
        if learning.get("intendedUse") not in {"evaluation", "counterexample", "documentation_feedback"}:
            reasons.append("INVALID_INTENDED_LEARNING_USE")
        if learning.get("automaticPromotion") is not False:
            reasons.append("AUTOMATIC_PROMOTION_PROHIBITED")

    revocation = candidate.get("revocation")
    if not isinstance(revocation, dict) or set(revocation) != REVOCATION_FIELDS or revocation.get("supported") is not True or not isinstance(revocation.get("contact"), str) or not revocation["contact"].strip():
        reasons.append("REVOCATION_PATH_REQUIRED")

    reason_codes = sorted(set(reasons))
    return {
        "receiptVersion": "1.0",
        "status": "waiting_for_review" if not reason_codes else "needs_changes",
        "candidateId": candidate_id if isinstance(candidate_id, str) else None,
        "canonicalCandidateSha256": _canonical_sha256(candidate),
        "reasonCodes": reason_codes,
        "addedToProject": False,
        "softwareChanged": False,
        "codeRun": False,
    }
