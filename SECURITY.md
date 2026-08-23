# Security Policy

## Supported versions

Only the latest tagged release is supported during the V1 pilot.

## Reporting a vulnerability

Do not open a public issue for an undisclosed vulnerability. Use GitHub's
private vulnerability reporting for this repository. If that channel is not
available, hold the report until a private maintainer channel is published.

Do not include credentials, private data, exploit payloads against live
systems, or UNA private-runtime material in a report.

## Default execution policy

V1 evaluation is network denied and prohibits filesystem writes, environment
access, and subprocess creation. Evaluation must be time- and memory-bounded.
Manifest validation never executes a capability.

Accepted candidates may be suspended or marked `REVOKED` when provenance,
integrity, maintainer custody, or security evidence becomes invalid.

