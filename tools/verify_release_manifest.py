"""Verify the exact release inventory without relying on platform utilities."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path, PurePosixPath, PureWindowsPath


LINE = re.compile(r"^([a-f0-9]{64})  (\./[^\n]+)$")
ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "RELEASE_MANIFEST.sha256"
EXCLUDED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "receipts",
    "reviews",
}


def discover_release_files(root: Path) -> set[str]:
    """Return every file that must appear in the release inventory."""

    discovered: set[str] = set()
    for candidate in root.rglob("*"):
        relative = candidate.relative_to(root)
        if (
            not candidate.is_file()
            or relative.as_posix() == "RELEASE_MANIFEST.sha256"
            or candidate.suffix == ".pyc"
            or any(part in EXCLUDED_DIRECTORIES or part.endswith(".egg-info") for part in relative.parts)
        ):
            continue
        discovered.add(relative.as_posix())
    return discovered


def verify_release_inventory(root: Path, inventory: Path) -> tuple[list[str], int]:
    root = root.resolve()
    failures: list[str] = []
    seen: set[str] = set()
    try:
        lines = inventory.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ["release inventory is missing or unreadable"], 0
    for number, line in enumerate(lines, 1):
        match = LINE.fullmatch(line)
        if match is None:
            failures.append(f"line {number}: malformed inventory entry")
            continue
        expected, declared = match.groups()
        relative = declared[2:]
        path = PurePosixPath(relative)
        if (
            not relative
            or not all(32 <= ord(character) <= 126 for character in relative)
            or "\\" in relative
            or path.as_posix() != relative
            or path.is_absolute()
            or PureWindowsPath(relative).drive
            or relative == "."
            or ".." in path.parts
        ):
            failures.append(f"line {number}: unsafe path")
            continue
        if relative in seen:
            failures.append(f"line {number}: duplicate path {relative}")
            continue
        seen.add(relative)
        candidate = (root / relative).resolve()
        try:
            if not candidate.is_relative_to(root) or not candidate.is_file():
                raise OSError
            observed = hashlib.sha256(candidate.read_bytes()).hexdigest()
        except OSError:
            failures.append(f"{declared}: missing or outside repository")
            continue
        if observed != expected:
            failures.append(f"{declared}: hash mismatch")

    if not seen:
        failures.append("release inventory is empty")
    discovered = discover_release_files(root)
    for omitted in sorted(discovered - seen):
        failures.append(f"inventory omits release file ./{omitted}")
    for unexpected in sorted(seen - discovered):
        failures.append(f"inventory declares excluded or absent file ./{unexpected}")
    return failures, len(seen)


def main() -> int:
    failures, declared = verify_release_inventory(ROOT, INVENTORY)
    for failure in failures:
        print(f"HOLD {failure}")
    if failures:
        return 2
    print(f"PASS {declared} complete release-manifest entries verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
