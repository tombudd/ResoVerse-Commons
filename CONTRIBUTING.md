# Contributing to ResoVerse Commons

Thank you for helping make governed AI capabilities easier to build, test, and
review. Small, focused contributions are welcome.

## Find the right starting point

- Browse issues labeled
  [`good first issue`](https://github.com/tombudd/ResoVerse-Commons/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
  for bounded work with a clear finish line.
- Use a capability-proposal issue when you have an idea but not an
  implementation.
- Use an evaluation-fixture issue for a counterexample, parser edge case, or
  expected `HOLD` behavior.
- Start a [Discussion](https://github.com/tombudd/ResoVerse-Commons/discussions)
  for open questions and early design exploration.

If you are unsure, ask. A question is a useful contribution.

## Development setup

Requires Git and Python 3.11 or newer.

```sh
git clone https://github.com/tombudd/ResoVerse-Commons.git
cd ResoVerse-Commons
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
python -m resoverse_commons.cli conformance
```

Windows PowerShell users can create the environment with `py -3 -m venv
.venv` and activate it with `.venv\Scripts\Activate.ps1`.

## Contribution requirements

1. Keep the change focused and explain the problem it solves.
2. Declare every permission. V1 capabilities require `dependencies: []` and
   prohibit third-party runtime dependencies.
3. Include deterministic positive and negative tests for behavior changes.
4. Run `python -m unittest discover -s tests -v` and the conformance corpus.
5. Validate changed manifests and bundles without executing their artifacts.
6. Disclose AI assistance, third-party code, datasets, and model artifacts.
7. Do not include credentials, private data, customer data, or protected
   implementation material.
8. Sign off each commit with `git commit -s`.

The sign-off certifies the [Developer Certificate of Origin
1.1](https://developercertificate.org/). All contributions are submitted under
Apache-2.0; submit only material you have the right to contribute.

## Pull-request feedback

The pull-request boundary workflow is deliberately non-executing. It reads
changed files through GitHub's API with a read-only token, checks JSON syntax
and public-boundary patterns, and never checks out or runs contributor code.
This is useful early feedback, not capability approval or independent review.

Maintainers refresh the release manifest after the candidate is final. Please
do not treat a stale release-manifest hash during development as an instruction
to bypass review.

## Review and decisions

The contributor may verify mechanics but cannot issue the independent review
of their own work. Acceptance requires a distinct reviewer. A passing test is
evidence within its declared scope, not unrestricted permission.

Maintainers aim to acknowledge new contributions within five working days. If
review will take longer, the target is to leave a status update rather than let
the contribution disappear silently.

Possible outcomes are:

- `PASS` for the stated review scope;
- `HOLD` with concrete reason codes or requested changes;
- closure with an explanation when the proposal is outside the public boundary
  or roadmap.

See [Governance Boundary](GOVERNANCE_BOUNDARY.md) and [Support](SUPPORT.md).
