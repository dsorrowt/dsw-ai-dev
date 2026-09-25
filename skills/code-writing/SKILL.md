---
name: code-writing
description: |
  Guides code implementation through proportional context reading, focused changes, verification, and fresh reviews.
  Use whenever code needs to be written — from a short ad-hoc edit to a full user-spec.

  Use when: "напиши код", "закодь", "реализуй", "write code", "implement" — the target behavior is
  already agreed (an explicit request or a user-spec) and now has to be implemented.
  For an unexplained failure whose cause is still unknown, diagnose it with `diagnosing-bugs`
  first; return here once the fix is agreed.

  Do NOT use for pure layout from a design export (Figma, HTML/CSS export, screenshot) or an
  existing visual style ("сверстай", "подвинь блок", responsive) — use layout-writing instead.
  For a React/Next.js performance review with no implementation to write — use
  `vercel-react-best-practices` instead.
  Direct mixed layout + business-logic work uses both layout-writing and code-writing.

  For creating a user-spec → user-spec-planning skill.
---

# Code Writing

## Understand the Change

1. Extract the requested behavior and what done means from the request or user-spec. Resolve
   ambiguity from repository evidence; ask only when a substantive choice changes the result or
   scope.
2. Read repository instructions, affected code, its usages, and only the project documentation
   needed to change it safely. A localized edit needs local context; cross-cutting work needs its
   contracts, architecture, and relevant patterns.
3. For non-trivial work, read every source file that will change, find affected contracts and
   reusable code, and establish the smallest useful baseline check. Inspect generated, lock,
   snapshot, or other mechanical artifacts through their generator, relevant diff, and
   deterministic validation rather than an unhelpful full read.
4. Discuss the approach before editing only when evidence exposes a substantive fork, risk, or
   scope decision. Otherwise choose the smallest safe implementation that follows project or
   framework conventions.
5. Treat a new idea, risk, edge case, or opportunity discovered during implementation or review
   as a proposal, not authorization. A rare or unagreed scenario is a user decision even when its
   correction looks local. Correct autonomously only an authorized local defect in agreed normal
   behavior; ask before adding behavior, state, entities, contracts, dependencies, architecture,
   or material complexity.

## Implement and Verify

1. Implement only the requested behavior. Reuse existing capabilities before adding abstractions
   or dependencies. Do not add speculative validation, fallbacks, configuration, optimization,
   or future flexibility without a current requirement or realistic project condition.
2. Validate untrusted input at its boundary, keep secrets out of source, preserve useful error
   information, and handle failures where the program can recover or add context.
3. Let straightforward code explain itself. Comment only when code cannot communicate the reason
   for a business rule, safety invariant, external constraint, compatibility workaround,
   deliberate tradeoff, or required ordering.
4. When the change can alter observable behavior, apply `test-master` to select and run the
   protecting tests. If it has no test subject, state that instead of creating artificial
   assertions.
5. Run the smallest supported lint, format, type, build, render, and user-requested checks that
   cover the change. Use a project-wide command only when it is the available entrypoint or the
   change is cross-cutting. Separate unrelated baseline failures from regressions.

## Run Fresh Reviews

After every completed implementation, run the review waves for this change under the shared
reviewer contract `skill://methodology/references/reviewer-contract.md` ("Review waves";
"Findings are diagnoses, not a work queue"): wave counts, the complete-set-in-one-wave mechanics,
stop rules, and findings dispositions live there.

The waves launch the complete reviewer set selected for the implementation in parallel against the
same revision: always a fresh `fw-code-reviewer` (autoloads `code-reviewing`; never set a model in
the call, the runtime resolves it from configuration) whose review scope matches the change — a
localized edit gets focused connected context, a broad change gets all affected contracts and
architecture — plus `fw-security-reviewer` (autoloads `security-auditor`) when a security boundary
changed or the user requested a security review, and the `fw-test-reviewer` that `test-master` owns
when meaningful test code changed, included in every wave for this implementation. Give each
reviewer the user request or user-spec, applicable repository instructions, validation evidence,
every touched source file with relevant callers and dependencies, deleted or renamed file evidence,
and generator/diff/validation evidence for mechanical artifacts.

Findings are diagnoses for agreed normal behavior: apply only an authorized local correction, and
reject unsupported findings with evidence and report unrelated findings without expanding the task.
Corrections between waves are authorized local defects that need no user decision, each followed by
rerunning the affected direct checks. After the last wave, hand off the remaining findings and
required decisions about scope, behavior, approach, or material complexity, briefly explaining
rejected rare findings.
