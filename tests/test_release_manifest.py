import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from verify_release_manifest import verify_release_inventory  # noqa: E402


def entry(path: Path, relative: str) -> str:
    digest = hashlib.sha256((path / relative).read_bytes()).hexdigest()
    return f"{digest}  ./{relative}\n"


class ReleaseManifestTests(unittest.TestCase):
    def test_complete_inventory_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.txt").write_text("one", encoding="utf-8")
            inventory = root / "RELEASE_MANIFEST.sha256"
            inventory.write_text(entry(root, "one.txt"), encoding="utf-8")
            failures, declared = verify_release_inventory(root, inventory)
        self.assertEqual(failures, [])
        self.assertEqual(declared, 1)

    def test_omitted_release_file_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.txt").write_text("one", encoding="utf-8")
            (root / "omitted.txt").write_text("omitted", encoding="utf-8")
            inventory = root / "RELEASE_MANIFEST.sha256"
            inventory.write_text(entry(root, "one.txt"), encoding="utf-8")
            failures, _ = verify_release_inventory(root, inventory)
        self.assertIn("inventory omits release file ./omitted.txt", failures)

    def test_declared_absent_file_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = root / "RELEASE_MANIFEST.sha256"
            inventory.write_text(f"{'0' * 64}  ./absent.txt\n", encoding="utf-8")
            failures, _ = verify_release_inventory(root, inventory)
        self.assertIn("inventory declares excluded or absent file ./absent.txt", failures)

    def test_missing_or_unreadable_inventory_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            failures, declared = verify_release_inventory(root, root / "missing.sha256")
            self.assertEqual(failures, ["release inventory is missing or unreadable"])
            self.assertEqual(declared, 0)

            failures, declared = verify_release_inventory(root, root)
            self.assertEqual(failures, ["release inventory is missing or unreadable"])
            self.assertEqual(declared, 0)

    def test_unsafe_portable_paths_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = root / "RELEASE_MANIFEST.sha256"
            for relative in (".", "nested\\file.txt", "C:drive.txt"):
                with self.subTest(relative=relative):
                    inventory.write_text(f"{'0' * 64}  ./{relative}\n", encoding="utf-8")
                    failures, _ = verify_release_inventory(root, inventory)
                    self.assertIn("line 1: unsafe path", failures)

    def test_nested_manifest_basename_is_not_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "nested"
            nested.mkdir()
            (nested / "RELEASE_MANIFEST.sha256").write_text("payload", encoding="utf-8")
            inventory = root / "RELEASE_MANIFEST.sha256"
            inventory.write_text("", encoding="utf-8")
            failures, _ = verify_release_inventory(root, inventory)
        self.assertIn(
            "inventory omits release file ./nested/RELEASE_MANIFEST.sha256",
            failures,
        )


if __name__ == "__main__":
    unittest.main()
