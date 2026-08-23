# Contributing

Contributions are welcome when they are portable, reproducible, rights-clear,
and compatible with the governance boundary.

## Before opening a pull request

1. Add or update a capability manifest.
2. Declare every permission. V1 capabilities must declare `dependencies: []`;
   third-party runtime dependencies are prohibited in V1.
3. Include deterministic positive and negative tests.
4. Run `python -m unittest discover -s tests -v`.
5. Run the manifest validator and include its receipt in the pull-request
   description.
6. Disclose AI-assisted code, third-party code, datasets, and model artifacts.
7. Sign off every commit using `git commit -s`.

The sign-off certifies the Developer Certificate of Origin 1.1:
<https://developercertificate.org/>.

## Review

The contributor may verify mechanics but cannot issue the independent review
of their own contribution. Acceptance requires a distinct reviewer. A passing
test is evidence within its declared scope, not evidence of unrestricted
capability or permission.

## Rights

All contributions are submitted under Apache-2.0. Do not submit material
unless you possess the necessary rights.
