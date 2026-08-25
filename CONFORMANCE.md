# Cross-language conformance corpus

The `resoverse_commons/corpus` corpus is a portable set of JSON inputs and exact
expected V1 outcomes. It lets another implementation demonstrate behavioral
compatibility without importing or executing the Python reference validator.

Run the reference implementation from the repository root:

```sh
python -m resoverse_commons.cli conformance
```

Expected result: `PASS`, six declared and completed cases, no failures, and
`executionAttempted: false`.

## Implementer contract

1. Read `resoverse_commons/corpus/index.json`.
2. Validate each referenced manifest without executing its entrypoint.
3. Compare the exact `status` and sorted, unique `reasonCodes`.
4. Treat malformed indexes, unsafe paths, missing cases, and mismatches as
   conformance failure.
5. Publish the implementation version, corpus commit, command, and complete
   output when claiming compatibility.

Passing this corpus demonstrates only the declared V1 cases. It does not grant
admission, production activation, learning use, reviewer identity, or authority.
New cases may be proposed through an evaluation-fixture issue.

An experimental JavaScript implementation is available under
`implementations/javascript`. It passes this corpus independently but does not
yet claim full compatibility; see its README for the remaining parser gap.
