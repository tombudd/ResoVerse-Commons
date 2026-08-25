import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CommunitySurfaceTests(unittest.TestCase):
    def test_required_community_files_exist(self):
        required = (
            "CODE_OF_CONDUCT.md",
            "CONTRIBUTING.md",
            "GOVERNANCE.md",
            "ROADMAP.md",
            "SECURITY.md",
            "SUPPORT.md",
            ".github/CODEOWNERS",
            ".github/pull_request_template.md",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/capability_proposal.yml",
            ".github/ISSUE_TEMPLATE/evaluation_fixture.yml",
            ".github/ISSUE_TEMPLATE/config.yml",
            ".github/workflows/pull-request-boundary.yml",
            ".github/dependabot.yml",
            ".github/FUNDING.yml",
            "CONFORMANCE.md",
            "GITHUB_LAUNCH_PLAYBOOK.md",
            "RELEASING.md",
            "SPONSORS.md",
            "tools/verify_release_manifest.py",
            "implementations/javascript/validator.mjs",
            "implementations/javascript/conformance.mjs",
            "tests/test_release_manifest.py",
        )
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_readme_has_copy_pasteable_onboarding(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for expected in (
            "git clone https://github.com/tombudd/ResoVerse-Commons.git",
            "python3 -m venv .venv",
            "py -3 -m venv .venv",
            "python -m pip install -e .",
            "Expected result: a `HOLD` receipt and exit code `2`",
            "python -m resoverse_commons.cli conformance",
            "[Sponsor ResoVerse Commons](SPONSORS.md)",
        ):
            self.assertIn(expected, readme)

    def test_local_markdown_links_resolve(self):
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        failures = []
        for document in sorted(ROOT.glob("*.md")):
            for target in link_pattern.findall(document.read_text(encoding="utf-8")):
                clean = target.split("#", 1)[0]
                if not clean or "://" in clean or clean.startswith("mailto:"):
                    continue
                if not (document.parent / clean).resolve().is_file():
                    failures.append(f"{document.name}: {target}")
        self.assertEqual(failures, [])

    def test_pull_request_feedback_cannot_execute_contributor_code(self):
        workflow = (ROOT / ".github/workflows/pull-request-boundary.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("pull_request:", workflow)
        self.assertNotIn("pull_request_target", workflow)
        self.assertNotIn("actions/checkout", workflow)
        self.assertNotRegex(workflow, r"(?m)^\s+run:")
        self.assertIn("contents: read", workflow)
        self.assertIn("pull-requests: read", workflow)
        self.assertIn("file.previous_filename", workflow)
        self.assertIn('rawUrl.hostname !== "github.com"', workflow)
        self.assertIn('"raw.githubusercontent.com"', workflow)
        self.assertIn('finalUrl.protocol !== "https:"', workflow)
        self.assertIn("for await (const chunk of response.body)", workflow)
        self.assertNotIn("response.arrayBuffer()", workflow)

    def test_current_public_tree_omits_forbidden_private_forms(self):
        forbidden = re.compile(r"(?i)(?:^|[^A-Za-z0-9])UNA-?1(?:[^A-Za-z0-9]|$)")
        failures = []
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if forbidden.search(text):
                failures.append(str(path.relative_to(ROOT)))
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
