# Compatibility Policy

ResoVerse Commons follows semantic versioning for its Python package and
explicit versions for interchange contracts.

- Package `0.x`: the project is a pilot; breaking changes may occur in minor
  releases and are documented in `CHANGELOG.md`.
- Capability manifest `schemaVersion: "1.0"`: structural interchange format.
- Validator receipt `receiptVersion: "1.0"`: receipt field contract.
- Capability bundle `bundleVersion: "1.0"`: portable bundle contract.

Bundle compatibility ranges use the exact V1 grammar
`>=MAJOR.MINOR,<MAJOR.MINOR`, with ASCII non-negative integers and an upper
bound greater than the lower bound. Each numeric component is limited to nine
digits. Wildcards, whitespace, patch components, and open-ended ranges are not
accepted.

The Draft 2020-12 JSON Schema is the structural gate. The Python validator is
the authoritative V1 policy gate. Structural schema success is necessary but
never sufficient for policy `PASS`.
