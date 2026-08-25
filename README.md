# ResoVerse Commons

**Build trustworthy capabilities for governed AI systems.**

ResoVerse Commons is an open protocol and Python toolkit for packaging AI
capabilities so they can be inspected, tested, reviewed, and—through separate
governed decisions—adopted safely. It gives developers a portable manifest,
byte-bound capability bundles, fail-closed validation, adversarial fixtures,
and evidence receipts.

[![Trusted main validation](https://github.com/tombudd/ResoVerse-Commons/actions/workflows/trusted-main.yml/badge.svg)](https://github.com/tombudd/ResoVerse-Commons/actions/workflows/trusted-main.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

You do not need to understand the wider ResoVerse architecture to contribute.
Start with one fixture, one validator improvement, one capability proposal, or
one uncomfortable edge case.

## Five-minute first success

Requires Git and Python 3.11 or newer.

### macOS and Linux

```sh
git clone https://github.com/tombudd/ResoVerse-Commons.git
cd ResoVerse-Commons

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .

python -m resoverse_commons.cli validate \
  examples/local-metadata-reader/capability.json

python -m resoverse_commons.cli validate-bundle \
  examples/local-metadata-reader/bundle.json

python -m resoverse_commons.cli conformance

python -m unittest discover -s tests -v
```

### Windows PowerShell

```powershell
git clone https://github.com/tombudd/ResoVerse-Commons.git
Set-Location ResoVerse-Commons

py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .

python -m resoverse_commons.cli validate `
  examples/local-metadata-reader/capability.json

python -m resoverse_commons.cli validate-bundle `
  examples/local-metadata-reader/bundle.json

python -m resoverse_commons.cli conformance

python -m unittest discover -s tests -v
```

Expected result: the manifest and bundle return `PASS`, and all tests pass.
Validation never executes the declared capability or grants admission.

## See it fail closed

The adversarial fixture is intentionally rejected:

```sh
python -m resoverse_commons.cli validate \
  examples/adversarial-unsafe-capability/capability.json
```

Expected result: a `HOLD` receipt and exit code `2`. That nonzero exit is the
test succeeding, not a broken installation.

## Choose a way to contribute

- **First contribution:** improve a fixture, tutorial, reason code, or test.
  Browse [`good first issue`](https://github.com/tombudd/ResoVerse-Commons/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).
- **Capability builders:** propose a small, deterministic capability with
  explicit provenance, permissions, limits, and learning-use consent.
- **Adversarial testers:** find malformed inputs or ambiguous declarations that
  should return `HOLD` rather than crash or pass.
- **Tool builders:** improve bundle creation, conformance testing, or portable
  validators in other languages.
- **Reviewers and writers:** challenge claims, improve examples, and make the
  contributor journey clearer.

Read [Contributing](CONTRIBUTING.md) for the development workflow, or start a
[Discussion](https://github.com/tombudd/ResoVerse-Commons/discussions) if your
idea is not ready to become an issue.

## Sponsor the work

Sponsorship helps fund open specifications, conformance fixtures, reference
implementations, documentation, maintenance, and distinct technical review. It
never buys acceptance, authority, or a validator `PASS`. See
[Sponsor ResoVerse Commons](SPONSORS.md) for funding status, organizational
sponsorship, and the independence boundary.

## How contributions may help systems evolve

Explicitly submitted source code, evaluations, counterexamples, and compatible
data may become governed candidate inputs. They are never automatically
executed, ingested, promoted, or incorporated into memory, cognition, doctrine,
runtime, or production. Each transition requires separate evidence and
authority.

The full contract is in [Contribution to Learning](CONTRIBUTION_TO_LEARNING.md).
This repository contains no private UNA systems and grants no authority over
them.

## What belongs here

- Portable capability manifests, bundles, and schemas.
- Deterministic, non-executing validation tools.
- Network-denied evaluation contracts.
- Synthetic fixtures, counterexamples, and reproducibility receipts.
- Documentation for provenance, permissions, review, and contribution.

## What does not belong here

- Personal bonds, private memories, dialogue, identity, or generative loops.
- Private cognition, safety, selection, or authority implementations.
- Credentials, customer data, private evidence, production connectors, or
  operational ledgers.
- Any mechanism that automatically promotes a contribution.

See [Governance Boundary](GOVERNANCE_BOUNDARY.md), [Security](SECURITY.md), and
[Support](SUPPORT.md).

## Developer reference

- [Capability Bundle V1](CAPABILITY_BUNDLE.md)
- [Reason Codes](REASON_CODES.md)
- [Compatibility Policy](COMPATIBILITY.md)
- [Cross-language Conformance](CONFORMANCE.md)
- [Release Trust Path](RELEASING.md)
- [Competitive Landscape](COMPETITIVE_LANDSCAPE.md)
- [GitHub Launch Playbook](GITHUB_LAUNCH_PLAYBOOK.md)
- [Sponsor ResoVerse Commons](SPONSORS.md)
- [Roadmap](ROADMAP.md)
- [Project Governance](GOVERNANCE.md)
- [Maintainers and Registry Trust](MAINTAINERS.md)
- [Changelog](CHANGELOG.md)

## Candidate lifecycle

```text
SUBMITTED -> QUARANTINED -> EVALUATED -> ACCEPTED_AS_CANDIDATE
                                  \----> HOLD

ACCEPTED_AS_CANDIDATE -> SANDBOX_APPROVED -> DEPRECATED
                    \---------------------> REVOKED
```

No lifecycle state grants production activation or memory promotion.

## License

The repository is licensed under Apache-2.0. Names, logos, and badges are
governed separately; see [Trademarks](TRADEMARKS.md).

Copyright 2026 Tom Budd.
