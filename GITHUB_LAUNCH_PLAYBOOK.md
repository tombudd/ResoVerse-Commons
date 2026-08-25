# GitHub launch playbook

This playbook is a practical path from a technically ready repository to early
external evidence. It authorizes no publication or outreach by itself.

## Positioning

Use one consistent sentence:

> ResoVerse Commons is a fail-closed, non-executing admission-evidence layer
> for portable AI capabilities: exact artifacts, declared permissions,
> provenance, learning-use consent, review evidence, and deterministic receipts.

Do not market it as another agent runtime. Position it as a complementary trust
boundary for MCP servers, agent tools, guardrails, and orchestration frameworks.

## Launch prerequisites

- Merge only after the complete local candidate receives distinct review and
  every trusted-main matrix lane passes on GitHub.
- Protect `main` and require the trusted checks and review.
- Activate the `tombudd` GitHub Sponsors profile and confirm the Sponsor button.
- Upload a 1280 × 640 social-preview image with the positioning sentence and a
  simple manifest → validate → receipt visual.
- Pin ResoVerse Commons on the maintainer profile and feature it near the top of
  the profile README.
- Publish a signed preview release with concise notes, limitations, install
  instructions, conformance output, and one clear contribution request.

## First 30 days

### Week 1 — make the proof easy to share

1. Publish the preview release and a linked GitHub Discussion.
2. Post a 60-second demonstration: safe manifest returns `PASS`; unsafe manifest
   returns `HOLD`; neither executes code.
3. Point every announcement to one action: run the corpus, challenge an edge
   case, or take a `good first issue`.
4. Ask five relevant maintainers for technical criticism, not promotion.

### Week 2 — create useful participation

1. Open a weekly **Break the validator** Discussion with one bounded fixture.
2. Maintain three to five genuinely small `good first issue` tasks.
3. Respond to contributor questions within two working days.
4. Publicly document accepted defects and `HOLD` outcomes; that is proof of the
   project's value, not negative marketing.

### Week 3 — earn adjacent ecosystem attention

1. Build one concrete MCP server candidate profile or mapping document.
2. Share it in an appropriate MCP community thread only after it works.
3. Add one example showing how a Commons-validated artifact could become an
   OpenAI, LangChain, or NeMo tool through a separate activation decision.
4. Invite a TypeScript maintainer to extend the corpus and close the JavaScript
   parity gaps.

### Week 4 — publish evidence, not vanity metrics

Report:

- clean installs and conformance runs;
- external issues, pull requests, reviewers, and downstream experiments;
- defects found and fixed;
- time to first maintainer response;
- sponsorship received and what public work it funded, when disclosure is
  appropriate.

Stars are useful reach signals, but external implementations and constructive
review are stronger evidence.

## GitHub discoverability checklist

- Keep the description outcome-led and under one sentence.
- Use focused topics such as `ai-agents`, `ai-safety`, `agent-security`,
  `interoperability`, `json-schema`, `provenance`, and `python`.
- Add `model-context-protocol` only when a working MCP profile exists.
- Keep Discussions seeded with a welcome thread, design questions, release
  announcements, and the weekly adversarial challenge.
- Turn recurring contributor questions into documentation and starter issues.
- Use release notes and Discussions to notify watchers without requiring them to
  subscribe to every repository event.
- Pin the repository and keep the profile README's first screen current.

## Copy-ready launch text

### GitHub Discussion title

`ResoVerse Commons preview: challenge the fail-closed capability boundary`

### Short announcement

> I opened ResoVerse Commons for developers who want AI capabilities to be
> inspectable before they become executable. It packages exact artifacts,
> provenance, permissions, limits, learning-use consent, and review evidence,
> then returns deterministic PASS/HOLD receipts without running contributor
> code. Run the six-case corpus, bring an uncomfortable edge case, or take a
> good-first issue: https://github.com/tombudd/ResoVerse-Commons

### Maintainer outreach

> I am looking for technical criticism, not an endorsement. ResoVerse Commons
> is testing a narrow idea: can contributed AI capabilities carry enough
> portable evidence to be inspected before execution? If this overlaps your
> work, I would value one failure mode, interoperability concern, or missing
> conformance case.

## Avoid

- mass-tagging maintainers or cross-posting identical messages;
- claiming safety, compatibility, adoption, or independent validation beyond
  the published evidence;
- adding broad topics solely for search traffic;
- sponsor benefits that compromise review independence;
- announcing before the public CI and installation path reproduce cleanly.
