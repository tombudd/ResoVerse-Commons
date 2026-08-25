"""Fail-closed, non-authorizing intake for opt-in learning candidates."""

from __future__ import annotations

import hashlib
import json
from typing import Any


TOP_LEVEL_FIELDS = {"candidateVersion", "id", "provenance", "artifacts", "learningUse", "revocation"}
PROVENANCE_FIELDS = {"sourceUrl", "license", "authors", "rightsToSubmit"}
LEARNING_FIELDS = {"consent", "intendedUse", "automaticPromotion"}
REVOCATION_FIELDS = {"supported", "contact"}


def _canonical_sha256(value: object) -> str | None:
    try:
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    except (TypeError, ValueError):
        return None


def validate_learning_candidate(candidate: object) -> dict[str, Any]:
    """Return a quarantine receipt; this never admits evidence, memory, or cognition."""

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
        if not isinstance(provenance.get("sourceUrl"), str) or not provenance["sourceUrl"].startswith(("https://", "http://")):
            reasons.append("INVALID_SOURCE_URL")
        if not isinstance(provenance.get("license"), str) or not provenance["license"].strip():
            reasons.append("INVALID_LICENSE")
        if not isinstance(provenance.get("authors"), list) or not provenance["authors"] or not all(isinstance(author, str) and author.strip() for author in provenance["authors"]):
            reasons.append("MISSING_AUTHORS")
        if provenance.get("rightsToSubmit") is not True:
            reasons.append("RIGHTS_TO_SUBMIT_NOT_CERTIFIED")

    artifacts = candidate.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts or not all(isinstance(item, dict) and set(item) == {"path", "sha256"} and isinstance(item["path"], str) and item["path"] and isinstance(item["sha256"], str) and len(item["sha256"]) == 64 for item in artifacts):
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
        "status": "QUARANTINED" if not reason_codes else "HOLD",
        "candidateId": candidate_id if isinstance(candidate_id, str) else None,
        "canonicalCandidateSha256": _canonical_sha256(candidate),
        "reasonCodes": reason_codes,
        "evidenceAdmissionAuthorized": False,
        "memoryPromotionAuthorized": False,
        "cognitionChangeAuthorized": False,
        "executionAttempted": False,
    }
