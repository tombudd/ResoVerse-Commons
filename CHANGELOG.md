# Changelog

## Unreleased

- Added GitHub Sponsors configuration, organizational sponsorship guidance,
  draft tiers, and an explicit sponsor-independence boundary.
- Added a GitHub-native launch playbook with positioning, discoverability,
  contributor-conversion, and copy-ready outreach guidance.
- Added a portable six-case V1 conformance corpus and fail-closed CLI runner.
- Added an experimental zero-dependency JavaScript validator that independently
  passes the shared corpus, with its remaining parity limitation documented.
- Added deterministic generated-input robustness coverage.
- Expanded trusted-main verification across Python 3.11–3.14, Linux, macOS,
  and Windows, with a clean wheel-install smoke test.
- Added cross-platform release-manifest verification, Dependabot configuration,
  and a release trust-path checklist.
- Corrected the runtime dependency pin to a release available through the
  project build environment so clean wheel installation succeeds.
- Reframed the README around a five-minute first success and concrete ways to
  contribute.
- Added contributor support, conduct, roadmap, issue forms, pull-request
  guidance, and code-ownership surfaces.
- Added read-only, non-executing pull-request boundary feedback.
- Added regression checks for community files, documentation links, onboarding
  commands, and public-boundary wording.

## 0.2.0 — 2026-08-23

- Made malformed URL and path handling fail closed.
- Separated canonical-manifest and submitted-byte receipt hashes.
- Defined structural-schema and authoritative-policy roles.
- Added Draft 2020-12 conformance tests and adversarial input coverage.
- Removed unused reference-capability permissions.
- Added a byte-bound, root-contained capability-bundle verifier and contract.
- Enforced Draft 2020-12 input/output schemas, portable reviewer identifiers,
  and the closed V1 compatibility-range grammar.
- Added duplicate-key rejection for manifests and bundles.
- Added reason-code, compatibility, and trusted-main CI contracts.
- Added GitHub private vulnerability reporting as the security channel.

## 0.1.0 — 2026-08-23

- Initial public validation-contract release.
