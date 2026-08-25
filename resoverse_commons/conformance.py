"""Portable, non-executing conformance-corpus runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .validator import DuplicateJsonKeyError, _safe_relative_path, load_json_bytes, validate_path


def _failure(case_id: str, reason: str) -> dict[str, str]:
    return {"id": case_id, "reason": reason}


def run_conformance_corpus(index_path: Path) -> dict[str, Any]:
    """Run manifest fixtures and compare exact status/reasons without execution."""

    failures: list[dict[str, str]] = []
    completed = 0
    try:
        index = load_json_bytes(index_path.read_bytes())
        root = index_path.parent.resolve(strict=True)
    except DuplicateJsonKeyError as exc:
        index = None
        root = index_path.parent.resolve()
        failures.append(_failure("corpus", f"DUPLICATE_JSON_KEY:{exc}"))
    except (OSError, UnicodeError, ValueError) as exc:
        index = None
        root = index_path.parent.resolve()
        failures.append(_failure("corpus", f"CORPUS_READ_FAILED:{type(exc).__name__}"))

    cases: object = None
    corpus_version: object = None
    if isinstance(index, dict):
        corpus_version = index.get("corpusVersion")
        cases = index.get("cases")
        if set(index) != {"corpusVersion", "cases"}:
            failures.append(_failure("corpus", "INVALID_CORPUS_FIELDS"))
        if corpus_version != "1.0":
            failures.append(_failure("corpus", "UNSUPPORTED_CORPUS_VERSION"))
        if not isinstance(cases, list):
            failures.append(_failure("corpus", "INVALID_CORPUS_CASES"))
            cases = []
    elif index is not None:
        failures.append(_failure("corpus", "CORPUS_MUST_BE_OBJECT"))
        cases = []

    seen_ids: set[str] = set()
    for position, case in enumerate(cases or []):
        fallback_id = f"case-{position}"
        if not isinstance(case, dict) or set(case) != {
            "id", "manifest", "expectedStatus", "expectedReasonCodes"
        }:
            failures.append(_failure(fallback_id, "INVALID_CASE_FIELDS"))
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            failures.append(_failure(fallback_id, "INVALID_CASE_ID"))
            continue
        if case_id in seen_ids:
            failures.append(_failure(case_id, "DUPLICATE_CASE_ID"))
            continue
        seen_ids.add(case_id)

        relative = case.get("manifest")
        expected_status = case.get("expectedStatus")
        expected_reasons = case.get("expectedReasonCodes")
        if not _safe_relative_path(relative):
            failures.append(_failure(case_id, "UNSAFE_CASE_PATH"))
            continue
        if expected_status not in {"PASS", "HOLD"}:
            failures.append(_failure(case_id, "INVALID_EXPECTED_STATUS"))
            continue
        if (
            not isinstance(expected_reasons, list)
            or not all(isinstance(reason, str) and reason for reason in expected_reasons)
            or expected_reasons != sorted(set(expected_reasons))
        ):
            failures.append(_failure(case_id, "INVALID_EXPECTED_REASON_CODES"))
            continue

        try:
            manifest_path = (root / relative).resolve(strict=True)
            if not manifest_path.is_relative_to(root) or not manifest_path.is_file():
                raise OSError
        except (OSError, RuntimeError):
            failures.append(_failure(case_id, "CASE_PATH_OUTSIDE_CORPUS"))
            continue

        receipt = validate_path(manifest_path)
        completed += 1
        if receipt["status"] != expected_status:
            failures.append(
                _failure(case_id, f"STATUS_MISMATCH:{expected_status}:{receipt['status']}")
            )
        if receipt["reasonCodes"] != expected_reasons:
            failures.append(_failure(case_id, "REASON_CODES_MISMATCH"))

    return {
        "corpusVersion": corpus_version if corpus_version == "1.0" else None,
        "status": "HOLD" if failures else "PASS",
        "declaredCases": len(cases or []),
        "completedCases": completed,
        "failures": failures,
        "executionAttempted": False,
        "admissionAuthorized": False,
    }
