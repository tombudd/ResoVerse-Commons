# Release trust path

Releases are maintainer-controlled consequences. This checklist documents the
evidence required; it does not authorize a release or create one automatically.

## Candidate checks

1. Start from a clean, reviewed `main` commit.
2. Confirm the package version and changelog agree.
3. Run the complete test suite and conformance corpus on every supported Python
   version and operating-system lane in trusted-main CI.
4. Build the wheel, install it in an empty environment, and run its CLI.
5. Refresh `RELEASE_MANIFEST.sha256`, then verify it with
   `python tools/verify_release_manifest.py`.
6. Record a distinct review of source, manifest, CI run, and release artifacts.
7. Generate an SBOM and provenance statement for the final artifacts.
8. Create a signed tag only after the maintainer has approved the exact commit
   and artifacts.

## Recommended GitHub enforcement

Protect `main`; require pull requests, one approving review, CODEOWNERS review
for workflow changes, passing trusted checks, resolved conversations, signed
commits, linear history, and no force pushes or deletion. Enable private
vulnerability reporting, dependency alerts, Dependabot security updates,
secret scanning, and push protection where the hosting plan supports them.

Repository configuration and publication are external authority-bearing acts.
Their observed state must be checked separately; this document is not evidence
that a setting is active.

## Release-inventory scope

Every repository file is included except the manifest itself and generated or
non-release directories: `.git`, caches, virtual environments, build outputs,
`*.egg-info`, `receipts`, and `reviews`. Verification fails for a mismatched
hash, missing declared path, undeclared release file, duplicate, or unsafe path.
