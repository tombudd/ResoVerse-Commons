# Security Policy

## Supported versions

Before the first release tag, only the current `main` branch is supported.
After tagging begins, the latest tagged release and `main` will be supported.

## Reporting a vulnerability

Do not open a public issue for an undisclosed vulnerability. Use GitHub's
private vulnerability reporting from the repository Security tab. The project
does not currently offer a second private reporting channel; if GitHub's
channel is unavailable, do not disclose exploit details in a public issue.

Do not include credentials, private data, exploit payloads against live
systems, or UNA private-runtime material in a report.

## Default execution policy

V1 evaluation is network denied and prohibits filesystem writes, environment
access, and subprocess creation. Evaluation must be time- and memory-bounded.
Manifest validation never executes a capability. Repository CI runs only after
code reaches trusted `main`; it is not a quarantine or governed
capability-execution environment.

Accepted candidates may be suspended or marked `REVOKED` when provenance,
integrity, maintainer custody, or security evidence becomes invalid.
