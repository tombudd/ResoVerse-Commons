# ResoVerse Commons

Open protocols, validation tools, evaluation contracts, and contribution standards for building
governed capabilities compatible with ResoVerse systems, including UNA-2.

ResoVerse Commons is an interoperability project. It is not UNA's private
runtime, does not contain UNA-1, and grants no authority to modify memory,
cognition, governance, production services, or external systems.

## First success

Requires Python 3.11 or newer and no third-party packages.

```sh
python -m resoverse_commons.cli validate \
  examples/local-metadata-reader/capability.json

python -m resoverse_commons.cli validate \
  examples/adversarial-unsafe-capability/capability.json

python -m unittest discover -s tests -v
```

The first example returns `PASS`. The adversarial example returns `HOLD` with
specific policy reasons.

## What belongs here

- Portable capability manifests and schemas.
- Deterministic non-executing validation tools and network-denied evaluation contracts.
- Synthetic fixtures, counterexamples, and reproducibility receipts.
- Documentation for provenance, permissions, review, and contribution.

## What does not belong here

- UNA-1's Personal Bond, memories, dialogue, identity, or generative loop.
- Private cognition, safety, selection, or authority implementations.
- Credentials, customer data, private evidence, production connectors, or
  operational ledgers.
- Any mechanism that automatically promotes a contribution into memory,
  cognition, doctrine, runtime, or production.

See [Governance Boundary](GOVERNANCE_BOUNDARY.md) and
[Contribution to Learning](CONTRIBUTION_TO_LEARNING.md).

## Candidate lifecycle

```text
SUBMITTED -> QUARANTINED -> EVALUATED -> ACCEPTED_AS_CANDIDATE
                                  \----> HOLD

ACCEPTED_AS_CANDIDATE -> SANDBOX_APPROVED -> DEPRECATED
                    \---------------------> REVOKED
```

No lifecycle state grants production activation or memory promotion.

## License

The entire repository is licensed under Apache-2.0. Names, logos, and badges
are governed separately; see [Trademarks](TRADEMARKS.md).

Copyright 2026 Tom Budd.
