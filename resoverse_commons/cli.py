"""Command-line entry point for manifest validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .validator import validate_path


def main() -> int:
    parser = argparse.ArgumentParser(prog="resoverse-commons")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate without executing")
    validate.add_argument("manifest", type=Path)
    args = parser.parse_args()

    receipt = validate_path(args.manifest)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

