---
name: methodology
description: |
  Explains the current AI-First development methodology: skill routing, Project Knowledge,
  user-spec planning and execution, evidence-gated reviews, reviewer roles, feature finalization,
  and model classes.

  Use when: "изучи методологию", "как работает пайплайн", "как делать фичи",
  "как устроены скиллы", "how does the methodology work", "explain the workflow"
---

# AI-First Development Methodology

## Purpose

The methodology keeps project and feature work understandable across sessions while making the
process proportional to the task. Durable project facts live in Project Knowledge, an approved
user-spec is the contract for a planned feature, execution skills own their domain workflows, and
fresh reviewer agents diagnose completed work without taking decisions away from the orchestrator
or the user.

## Operating Model

Requests route directly to skills by intent. Feature planning, direct execution, initialization,
documentation, and finalization do not depend on command wrapper files. Request the workflow in
plain language; historical shorthand such as `/new-user-spec` or `/done` does not imply that an
installed slash-command wrapper exists.

Choose the smallest path that fits the work:

| Need | Path |
|---|---|
| Small, well-defined change | Invoke the matching execution skill directly |
| Feature whose behavior or approach needs agreement | `user-spec-planning` → approval → execution → finalization |
| New repository | `project-initialization` → initial Project Knowledge → feature or ad-hoc work |
| Documentation-only work | `documentation-writing` with the evidence boundary named by the request |
| Review or audit only | Use the matching review skill or reviewer without modifying the artifact |

One request may activate several skills. For example, a UI feature with state changes uses both
`layout-writing` and `code-writing`; their verification and reviewers are coordinated in one
execution rather than treated as unrelated pipelines.

## Planned Feature Lifecycle

```text
user-spec-planning → explicit approval → a follow-up task: implement the approved spec
→ verified implementation commit → documentation-writing feature finalization
→ squashed integration into the shared branch
```

Planning and implementation commits are local. The shared branch receives one squashed commit per
feature, so `work/` planning artifacts never enter shared history.

### Plan the Feature

`user-spec-planning` owns the complete planning contract:

1. Start or resume `work/{feature}/logs/userspec/interview.yml`. Ask 3–4 questions per batch and
   run as many batches as the actual gaps require; there is no fixed number of interview cycles.
2. Load the Project Knowledge router when it exists and follow only the routes relevant to the
   feature. Missing Project Knowledge never blocks planning; it does block implementation work that
   needs it as operating context (for example `infrastructure-setup`), which stops and asks the user
   to create or fill it through `documentation-writing`.
3. Once the intended outcome is clear enough, run `fw-code-researcher`, write
   `work/{feature}/code-research.md`, and use code evidence in the remaining interview.
4. Run fresh `fw-uspec-interview-checker` instances until the agreed scope has no substantive
   requirements gap. A finding that would expand the feature returns to the user for a decision.
5. Fill the bundled user-spec template in place. Keep its scaffold in English, write its content
   in the user's language, preserve the executor instruction, and commit the draft.
6. Validate every round in parallel with:
   - `fw-uspec-quality` for document quality, coverage, and testable criteria;
   - `fw-uspec-adequacy` for feasibility, proportionality, and architecture fit;
   - `fw-skeptic` for factual claims about the current codebase.
7. Stop when all lanes are clean or after the third validation round. Obtain explicit user
   approval, set the spec and interview statuses, commit the approval, and return the absolute
   user-spec path for a follow-up task.

If the request contains independently valuable outcomes, planning proposes a split and waits for
the user's choice. Different files, code layers, or execution skills alone do not require separate
specs.

### Implement the Feature

The implementation task reads the approved `user-spec.md`, its executor instruction,
`decisions.md` when present, and the relevant Project Knowledge routes. It then activates the
skills required by the agreed work:

- `code-writing` owns application behavior, data flow, APIs, state, validation, and code changes;
- `layout-writing` owns markup, styling, typography, assets, responsive behavior, and visual
  evidence;
- `infrastructure-setup` owns Docker, hooks, CI/CD, delivery, release artifacts, monitoring,
  recovery, and other operational changes;
- `prompt-master` owns LLM prompt creation and revision;
- `skill-master` owns skill creation and revision.

Each executor reads context in proportion to the change, implements only agreed behavior, runs the
smallest checks that establish the result, and coordinates every reviewer required by the active
skills. When observable behavior changes, `test-master` selects the smallest reliable boundary
that reproduces each meaningful risk; it does not create tests for artifacts with no contract to
protect.

The verified implementation is committed separately in local history before feature finalization;
squashed integration collapses these local commits into the single commit the shared branch
receives. `decisions.md` receives only material decisions or deviations that need to survive the
current context: it is created by its first such entry and never exists as an empty file.

### Finalize the Feature

Feature finalization is an explicit mode of `documentation-writing`. The user identifies
`work/{feature}/` and asks to finish or finalize it; no wrapper command file is required.

The skill reads the spec, decisions, implementation, and relevant Git history; checks whether the
feature is evidently complete; updates only affected durable Project Knowledge; moves deferred or
rejected scope that is not covered by the agreed spec into the project's backlog, marking each item
with the feature it came from and asking the user when the project has no backlog convention;
removes active links that still treat the feature folder as current; keeps only `user-spec.md` and
`decisions.md` (when it holds material entries) in `work/completed/{feature}/`; removes the
remaining feature artifacts (`code-research.md`, `split-context.md`, and other intermediates) from
the worktree, staging the deletions of tracked files in the same commit; and commits the
documentation and archive change. The archive holds the approved contract and its decisions instead
of the planning trail. If Project Knowledge is missing, the documentation update is skipped but
archival and finalization may still continue.

This is the only documentation mode that reads feature artifacts by default, archives a feature,
or creates a finalization commit. A normal documentation update or audit does none of those.

## Ad-hoc Work

A small direct request does not require a user-spec. The matching execution skill derives done
from the request, reads only the needed project context, makes the focused change, and verifies it
at the smallest useful boundary. Broader or cross-cutting work loads the contracts and Project
Knowledge routes it actually affects.

A risk, idea, edge case, or improvement discovered during implementation or review is a proposal,
not new authorization. The executor may correct a local defect required for the agreed result; a
change to behavior, scope, approach, state, fallback, validation, or material complexity returns
to the user for a decision.

## New Projects and Project Knowledge

`project-initialization` creates a repository from its bundled template, preserves
pre-existing files in the next available `old*` directory,
creates the initialization commit, connects a private GitHub
repository, creates `main` and `dev`, and leaves `dev` active. Reviewing or merging preserved
`old*` files is separate work.

The next step is initial Project Knowledge through `documentation-writing`. Its adaptive interview
derives what it can from the repository, uses as many question batches as needed, obtains
checkpoint agreement for project definition, architecture, and operations/experience, proposes a
documentation topology when one is not already established, and writes durable facts in English.

Project Knowledge lives in `.agents/skills/project-knowledge/`, whose `SKILL.md` is always the
router. Use structure by context boundary rather than file size:

- compact projects may keep Project, Architecture, Patterns, Deployment, and applicable UX or
  domain facts in the router itself;
- standard projects use the router plus `project.md`, `architecture.md`, `patterns.md`, and
  `deployment.md`;
- `ux-guidelines.md` or domain references are added only when they form independently useful
  loading boundaries.

`AGENTS.md` stays a compact entry rulebook for agents — language, behavior, task scope, worktrees,
and security — instead of a project fact sheet. Project Knowledge lives in
`.agents/skills/project-knowledge/`, whose `SKILL.md` router is the route to the right reference.

## Sources of Truth

### Approved User Spec

`work/{feature}/user-spec.md` owns the agreed feature outcome, behavior, acceptance criteria,
constraints, risks, accepted decisions, testing intent, and verification plan.

### Project Knowledge

Project Knowledge owns current durable project facts: purpose, architecture, project-specific
patterns and business rules, deployment and operations, and applicable UX or domain guidance.
Code owns implementation detail; configuration or registries own changing inventories; `work/`
artifacts are evidence rather than owners of current project state.

### Feature Folder

```text
work/{feature}/
├── user-spec.md
├── code-research.md
├── decisions.md        # created by the first material decision or deviation
└── logs/
    ├── userspec/
    │   └── interview.yml
    └── working/
```

Completed features keep only `user-spec.md` and, when it holds material entries, `decisions.md`, and
move to `work/completed/{feature}/`; the interview log, `code-research.md`, and working logs are
removed at finalization. Planning templates, interview state, and
the initializer script are bundled inside `user-spec-planning`; new-project templates are bundled
inside `project-initialization`. There is no shared resource directory between skills.

## Skill Responsibilities

| Area | Owning skills |
|---|---|
| Feature requirements | `user-spec-planning` |
| Project documentation and finalization | `documentation-writing` |
| Application implementation | `code-writing` |
| UI implementation and visual evidence | `layout-writing` |
| Infrastructure and operations | `infrastructure-setup` |
| Project creation | `project-initialization` |
| Prompt authoring | `prompt-master` |
| Skill authoring | `skill-master` |
| Test selection and quality | `test-master` |
| Code, layout, and security review criteria | `code-reviewing`, `layout-reviewing`, `security-auditor` |

A skill package owns its optional `references/`, deterministic `scripts/`, and output
`assets/`. This keeps dependencies portable across installations and public publication instead of
relying on unrelated global directories.

## Review Model

Reusable methodology lives in skills. Dedicated `fw-*` reviewer agents add fresh isolated context,
a bounded skeptical role, the minimum tools needed to inspect evidence, and a structured diagnostic
result. Their model comes from runtime configuration, never from the caller; reviewer roles run in
the `good` class. They do not edit artifacts, design remediation, or decide whether work ships. The
shared stance, result schema, review-loop limit, and findings handling are defined once in
[references/reviewer-contract.md](references/reviewer-contract.md), which every reviewer reads
before reporting. Its "Review waves" and "Findings are diagnoses, not a work queue" sections carry
the shared wave mechanics and the findings rules — the complete-set wave, the wave counts, the
stop rules, the diagnose-then-authorize sequence — so no skill restates them.

A finding is valid only when it establishes a concrete location, observed evidence, violated
requirement, realistic triggering conditions, and impact — the contract's evidence gate. A clean
result is valid. The orchestrator applies only an authorized correction, one inside the user
request, approved plan, or user-spec, exactly as the contract's findings rule states.

Common reviewer ownership is:

- every completed code implementation: `fw-code-reviewer`;
- layout implementation: `fw-layout-reviewer` with prepared source and rendered evidence;
- meaningful test-code changes: `fw-test-reviewer` through `test-master`;
- changed security boundaries or an explicit security request: `fw-security-reviewer`;
- documentation edits: `fw-docs-reviewer`;
- material infrastructure work or an explicit infrastructure review: `fw-infra-reviewer`;
- prompt edits: `fw-prompt-reviewer`;
- skill changes: the applicable `fw-skill-checker`, `fw-skill-logic-reviewer`, and
  `fw-skill-simplicity-reviewer` lanes;

## Model classes

Skills and agents name a class of model, never a model or a vendor. Two classes exist: `fast` for
mechanical, high-volume, low-judgement steps such as search fan-out, listings, mechanical edits, and
data collection; `good` for review, planning, architecture, and spec quality, and for any work that
judges another agent's output. The class is bound to a concrete model in runtime configuration,
outside this repository: for omp, role aliases in `task.agentModelOverrides` with concrete selectors
in `modelRoles`; for pi, the single `defaultProvider`/`defaultModel` in `settings.json`, where both
classes collapse into the session model. The contract's `model` field exists, but no framework skill
or agent file ever carries it.

## Orchestration: one step, one orchestrator

Fresh context is the anti-anchoring mechanism. In omp a subagent is already isolated. In pi only an
orca worker gives fresh context — a separate process in an orca worktree: run the review wave before
delivering large work, omp↔pi handoffs, and file-isolated tasks through the `orca` CLI; within one pi
session independence is not guaranteed.

The in-session `task` tool and an orca worker are two different orchestrators, and one step uses
exactly one of them. Use `task` when the work stays entirely inside the current session and runtime:
quick local checks and decomposition into bounded subtasks. Its subagents are child sessions of the
same harness and die with the session. Use an orca worker when at least one worker condition holds —
the review wave before delivering large work, an omp↔pi handoff, file isolation — or when the result
must outlive the session or run in another runtime. When in doubt, choose by this rule instead of
spawning both in one step: neither runtime documents the semantics of mixing the two.

The words "orchestrate" or "orchestration" from a user select neither mechanism by themselves. The
choice follows the worker conditions above and the version-matched `orca` guides (`orca-cli`,
`orchestration`), never the wording of a request; project skills do not depend on any keyword being
spoken.

## Working Principles

- **Simplest sufficient process:** add a document, abstraction, rule, fallback, or coordination
  layer only for a current requirement or demonstrated failure.
- **Proportional context:** load the smallest context that preserves the affected contracts.
- **One outcome, one user-facing specification:** split only independently valuable outcomes and
  let the user decide.
- **Evidence before action:** reviewer identity or severity never substitutes for evidence, and a
  finding never expands authorization.
- **Stable commits:** commit meaningful states such as a draft spec, approved spec, verified
  implementation, or finalized documentation; do not force incidental state into a commit.
- **Local intermediates, squashed integration:** local commits may carry the planning trail;
  `dev` and `main` receive one squashed commit per feature. Never push a branch whose history
  contains `work/` planning artifacts — squash-merge does not remove objects already pushed. To
  publish work for review before merging, build a single-commit branch from the current `dev`
  carrying only the finalized tree.
