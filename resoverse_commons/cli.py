"""Command-line entry point for manifest validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bundle import validate_bundle_path
from .validator import validate_path


def main() -> int:
    parser = argparse.ArgumentParser(prog="resoverse-commons")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate without executing")
    validate.add_argument("manifest", type=Path)
    validate_bundle = subparsers.add_parser(
        "validate-bundle", help="validate a bundle and its byte-bound files without executing"
    )
    validate_bundle.add_argument("bundle", type=Path)
    args = parser.parse_args()

    receipt = (
        validate_path(args.manifest)
        if args.command == "validate"
        else validate_bundle_path(args.bundle)
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
