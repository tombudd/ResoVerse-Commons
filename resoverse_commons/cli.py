"""Command-line entry point for manifest validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bundle import validate_bundle_path
from .learning import _invalid_receipt, validate_learning_candidate
from .validator import DuplicateJsonKeyError, load_json_bytes, validate_path


def main() -> int:
    parser = argparse.ArgumentParser(prog="resoverse-commons")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate without executing")
    validate.add_argument("manifest", type=Path)
    validate_bundle = subparsers.add_parser(
        "validate-bundle", help="validate a bundle and its byte-bound files without executing"
    )
    validate_bundle.add_argument("bundle", type=Path)
    validate_learning = subparsers.add_parser("validate-learning-candidate", help="quarantine an opt-in learning candidate without promotion")
    validate_learning.add_argument("candidate", type=Path)
    args = parser.parse_args()

    if args.command == "validate":
        receipt = validate_path(args.manifest)
    elif args.command == "validate-bundle":
        receipt = validate_bundle_path(args.bundle)
    else:
        try:
            candidate = load_json_bytes(args.candidate.read_bytes())
        except DuplicateJsonKeyError as exc:
            receipt = _invalid_receipt(f"DUPLICATE_JSON_KEY:{exc}")
        except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
            receipt = _invalid_receipt(f"CANDIDATE_READ_ERROR:{type(exc).__name__}")
        else:
            receipt = validate_learning_candidate(candidate)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] in {"PASS", "waiting_for_review"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
