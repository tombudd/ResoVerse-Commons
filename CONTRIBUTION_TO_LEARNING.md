# Contribution Review Contract

Status: a public guide for handling submissions. It does not give a submission permission to run or be used.

## Permitted candidate inputs

Maintainers may check explicitly submitted source code, manifests, tests,
counterexamples, reproducible results, and contributor-owned or compatibly
licensed data. Automatically collected usage data is not included.

Each input must identify its author, origin, license, rights to submit,
whether it needs extra software to run, intended use, and known limits. Extra
software is not allowed for the first version.

## Candidate use

A submission may wait for review, be inspected without running it, be checked
in an isolated environment with no network access, be compared with other
submissions, and be reviewed. None of these steps add it to the project,
change the software, or use it in a live service.

## Separate decisions

Recording a submission, allowing an isolated check, allowing it to run, adding
it to the project, changing the software, and using it in a live service are
different decisions. Passing one step does not allow any other step.

## Prohibitions

- Nothing from pull requests, issues, discussions, forks, or outside
  repositories is used automatically.
- Contributors must clearly say how a submission may be used.
- Private, personal, customer, password, and service-only material is not allowed.
- A submission cannot approve or review itself.
- Missing or unclear information never counts as permission.

A submission with missing information returns `needs_changes`.
