# Capability Bundle V1

A capability bundle is a portable review unit. It binds one capability
manifest to one implementation artifact, its input/output contracts,
compatibility declaration, and independent-review evidence.

The bundle is metadata only. Creating or validating it does not execute the
artifact or grant sandbox, runtime, evidence-admission, learning, or production
authority.

Required elements are defined by
`schemas/capability-bundle.schema.json`. Every referenced file is bound by a
lowercase SHA-256 digest. The Python bundle validator resolves each reference,
including symlinks, and requires the resulting regular file to remain inside
the bundle root. It also requires the manifest entrypoint to identify the
byte-bound artifact and verifies both schema documents against the Draft
2020-12 metaschema. V1 dependencies remain empty.

`actorId` and `reviewerId` are declared identities. The validator requires them
to be non-empty and unequal, and binds the exact review-receipt bytes. It does
not authenticate either identity or prove real-world reviewer independence;
that remains an external admission decision.

```sh
python -m resoverse_commons.cli validate-bundle \
  examples/local-metadata-reader/bundle.json
```

Lifecycle transitions continue to follow `GOVERNANCE_BOUNDARY.md`; bundle
validity establishes only a well-formed candidate for quarantine.
