"""Command-line entry point for manifest validation."""

from __future__ import annotations

import argparse
import json
from importlib.resources import as_file, files
from pathlib import Path

from .bundle import validate_bundle_path
from .conformance import run_conformance_corpus
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
    conformance = subparsers.add_parser(
        "conformance", help="run portable manifest fixtures without executing artifacts"
    )
    conformance.add_argument(
        "index",
        type=Path,
        nargs="?",
        default=None,
    )
    args = parser.parse_args()

    if args.command == "validate":
        receipt = validate_path(args.manifest)
    elif args.command == "validate-bundle":
        receipt = validate_bundle_path(args.bundle)
    elif args.index is not None:
        receipt = run_conformance_corpus(args.index)
    else:
        packaged_index = files("resoverse_commons").joinpath("corpus/index.json")
        with as_file(packaged_index) as index_path:
            receipt = run_conformance_corpus(index_path)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
