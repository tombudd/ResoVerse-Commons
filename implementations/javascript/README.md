# Experimental JavaScript validator

This zero-dependency implementation independently expresses the V1 manifest
policy in JavaScript and passes the shared corpus:

```sh
node implementations/javascript/conformance.mjs
```

It is experimental, not yet a full compatibility claim. In particular, the
command uses the platform JSON parser and therefore does not independently
detect duplicate object keys in raw JSON. The Python implementation remains
the authoritative V1 policy gate until this limitation and broader adversarial
parity are resolved.

The runner validates JSON data only. It never imports or executes a declared
artifact and grants no admission or activation authority.
