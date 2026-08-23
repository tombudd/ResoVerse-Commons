"""Reference implementation: pure transformation, no network or writes."""

from __future__ import annotations

from typing import Any


def extract_metadata(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"status": "HOLD", "reason": "INPUT_MUST_BE_OBJECT"}
    return {
        "status": "PASS",
        "metadata": {
            key: value[key]
            for key in ("id", "title", "source")
            if key in value and isinstance(value[key], str)
        },
    }

