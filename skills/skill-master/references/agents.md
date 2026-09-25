# Skill + Agent Pattern

Subagents isolate context-heavy work from the orchestrator. A skill holds reusable methodology;
an agent adds a bounded role, necessary tools, and a result contract.

## Contents

- [Runtime-neutral orchestration](#runtime-neutral-orchestration)
- [When to delegate](#when-to-delegate)
- [Inline and dedicated agents](#inline-and-dedicated-agents)
- [Agent file format](#agent-file-format)
- [Reviewer contract](#reviewer-contract)
- [Other agent contracts](#other-agent-contracts)
- [Orchestrator responsibilities](#orchestrator-responsibilities)
- [Invoking agents from skills](#invoking-agents-from-skills)

## Runtime-neutral orchestration

Use the subagent mechanism available in the current runtime. Describe the role and required
result without assuming a particular Team, Task, transcript, or transport API.

Nested delegation is allowed when the runtime supports it and the subtask genuinely benefits
from another isolated context. The delegating agent remains responsible for its own bounded
result. If nested delegation is unavailable or unnecessary, it returns the need to the
orchestrator instead.

Agents never select their own model, and a caller never passes one: omp resolves it from runtime
configuration (`task.agentModelOverrides`, then the parent session), and pi has a single session
model and no subagents. A role that needs a class of model states it as `fast` or `good` — never as
a model name.

## When to delegate

| Task type | Why isolation helps | Example |
|---|---|---|
| Review | Fresh context reduces anchoring on the implementation | Code or security review |
| Research | Extensive file reading stays outside the main context | Codebase exploration |
| Debugging | A focused trace keeps logs and hypotheses bounded | Root-cause analysis |
| Validation | A clean context can simulate or verify independently | Schema or skill review |
| Parallel work | Independent questions can run concurrently | Researching separate modules |
| High-volume work | Large logs and test output stay isolated | Test-suite analysis |

Delegate a concrete, bounded task. Keep decisions that combine findings, user scope, and the
overall solution with the orchestrator.

## Inline and dedicated agents

Use an inline subagent for a short, one-off task whose prompt can state the scope and result
directly. Use the runtime's suitable exploration, analysis, or execution role; role names differ
between runtimes.

Create a dedicated Skill + Agent pair for a reusable task with substantial methodology:

1. The skill contains the domain methodology and remains usable without an agent.
2. The agent preloads that skill, receives a bounded input, and defines the result contract.

This keeps methodology in one source while giving repeated reviews fresh context.

### Responsibility split for reviewers

- The skill owns reusable domain criteria, checklists, decision rules, and defect examples.
- The reviewer agent owns the fresh skeptical stance, bounded input, evidence to read,
  reviewer-specific hunt or investigation mechanics, evidence gate, diagnostic result fields,
  direct JSON response, and the exclusions against editing, designing remediation, or making a
  release decision.
- The caller owns launching a fresh reviewer, supplying complete context, evaluating returned
  findings, and deciding whether an authorized correction is warranted.

Do not repeat the preloaded skill's reusable domain rules in the agent. When a necessary reusable
rule exists only in an agent, move it into the preloaded skill before removing the agent copy;
this preserves behavior while restoring one canonical owner. Mechanics used only to investigate
the reviewer agent's bounded lane may remain in that agent.

## Agent file format

omp reads agent definitions from a project's `.omp/agents/<name>.md` and from the user directory
`~/.omp/agent/agents/<name>.md`; pi has no subagents and reads no agent files. The framework authors
its wrappers in the repository's `agents/` directory and installs them into the user directory.

The file body **is** the system prompt: omp passes everything after the frontmatter as the agent's
system prompt, and there is no `systemPrompt` frontmatter field to fill. Required fields are `name`
and `description`. The contract's optional fields are `tools`, `autoloadSkills`, `spawns`, `model`,
`output`, and `blocking`; a framework wrapper never sets `model` (see the field rules below).

A wrapper stays thin — a few body lines (the framework's wrappers use 4–6 wrapped lines, about five
sentences) that state the role and point at the preloaded skill and its contract. Domain criteria,
methodology, and the result schema live in the preloaded skill or in the shared reviewer contract,
not in the wrapper.

```yaml
---
name: fw-code-reviewer
description: >-
  Reviews code quality after implementation, including localized edits, features, refactors,
  cross-file changes, generated artifacts, and behavior changes.
autoloadSkills: [code-reviewing]
tools: [read, glob, grep]
---
You are a fresh skeptical code reviewer: try to disprove that the completed change satisfies its
requirements and repository contracts. Follow the preloaded code-reviewing methodology.
Before reporting, read the reviewer contract at
`skill://methodology/references/reviewer-contract.md` and follow its JSON output schema exactly.
Diagnose only: no edits, no remediation, no ship verdict.
```

Field rules:

- `name` — required. Framework wrappers carry the `fw-` prefix; bundled runtime names (`reviewer`,
  `scout`, `security-reviewer`, `task`, `sonic`) are shadowed first-wins and must not be reused.
- `description` — required. State the bounded purpose, the trigger for delegation, and the
  exclusions concretely.
- `tools` — restrict the tool set with lowercase runtime names (`read`, `glob`, `grep`, `bash`,
  `write`). Use only the tools the task needs: analysis and review agents normally need read/search
  tools, `bash` is added only for relevant read-only checks, and a reviewer is never granted `write`
  merely to persist its report.
- `autoloadSkills` — preloads the methodology skill whose rules the wrapper follows.
- `model` — part of the omp agent contract, but never set by a framework wrapper: the runtime
  resolves the model (`task.agentModelOverrides`, then the parent session) and a caller never passes
  one. A role that needs a class of model states the class (`fast` or `good`) in prose.
- `spawns`, `output`, `blocking` — recognized by omp; the thin wrappers do not declare them. Nested
  delegation returns the need to the orchestrator, and the result contract lives in the preloaded
  skill or in the shared reviewer contract.

The Claude Code fields are not part of the omp agent contract: `skills` (preloading is
`autoloadSkills`), `allowed-tools` (tool restriction is `tools`), `model: inherit`, and `color`.

## Reviewer contract

The shared stance, result schema, severity scale, and review-loop limit live in one place: the
`methodology` skill's reviewer contract (`skill://methodology/references/reviewer-contract.md`).
Reviewer roles read it
before reporting. This section covers the orchestrator-facing mechanics that surround it.

A reviewer, validator, checker, scanner, or critic diagnoses the supplied artifact. It does not
modify the artifact, design remediation, or decide whether the result may ship.

### Stance and scope

The reviewer starts from fresh context, reads the complete artifact, and follows relevant
callers, dependencies, standards, and contracts. It actively tries to disprove correctness but
does not assume a defect must exist. Accuracy matters more than the number of findings, and a
clean result is a complete valid outcome.

Review the current change or other scope supplied by the orchestrator. An unrelated pre-existing
problem is not a finding unless the supplied scope includes it or the current change creates a
demonstrable path to it.

Do not suppress a demonstrated finding because its trigger is rare. Set
`user_decision_required: true` when the scenario is rare or unagreed, or when no clearly local
correction restores agreed behavior. Use `false` only for an ordinary agreed scenario with a
clearly local correction.

### Evidence gate

Create a finding only when all five facts are established:

1. `location` identifies the concrete artifact location.
2. `evidence` states the observed fact, not a suspicion.
3. `violated_requirement` names the requirement, standard, or contract that the fact violates.
4. `conditions` describes a realistic path that triggers the problem in the current project.
5. `impact` states the concrete consequence under those conditions.

If any fact is missing, continue investigating or omit the finding. A personal preference, a
possible improvement, a best practice without demonstrated consequence, hypothetical future
expansion, a scenario without an established trigger path, or defensive machinery proposed
"just in case" does not pass the gate. A false finding is a reviewer error.

### No solution or release verdict

Findings describe the violated property, not how to fix it. Reviewer output contains no fix,
recommendation, patch, remediation plan, replacement architecture, new dependency, fallback,
corrected code example, or release verdict. Severity and other domain fields are diagnostic
metadata only; they do not decide the orchestrator's action.

### Result schema

Return the JSON directly as the subagent result. The complete schema lives in one place — the shared
reviewer contract (`skill://methodology/references/reviewer-contract.md`): the five required
top-level keys (`status`, `findings`, `clean_check`, `scope_reminder`, `summary`), the per-finding
fields, and the scope reminder literal. Read it before reporting and follow it exactly instead of
restating the schema here; a second copy would drift.

Every finding carries `severity` and `category` exactly as that contract defines them — the one
shared scale and vocabulary; a role never invents its own scale. Extra diagnostic fields such as
`cwe` or `confidence` may be added inside a finding when useful, provided they do not propose a
solution.

Every finding includes `user_decision_required`. `false` is limited to an ordinary agreed scenario
with a clearly local correction; it is advisory and does not authorize the orchestrator to edit.
`true` covers a rare or unagreed scenario, or one whose correction would likely add behavior,
state, entities, contracts, dependencies, architecture, or material complexity.

Order findings by consequence so the orchestrator can triage efficiently. A bare assertion that
the artifact is fine is not an adequate clean check.

### Reviewer skeleton

```markdown
You are a fresh skeptical {lane} reviewer. Try to disprove that the supplied {artifact}
satisfies {standard}, while treating accuracy rather than finding count as the goal. Read the
whole artifact and its relevant callers, dependencies, and contracts. Diagnose only: do not edit,
design remediation, or decide whether it ships.

Create a finding only after establishing its location, observed evidence, violated requirement,
realistic trigger conditions, and concrete impact. Do not suppress a demonstrated finding because
its trigger is rare. Set `user_decision_required: true` for a rare or unagreed scenario, or when no
clearly local correction restores agreed behavior; use `false` only for an ordinary agreed scenario
with a clearly local correction. Return the common reviewer JSON directly to the orchestrator. A
clean result explains what was checked and why no violation was proved.
```

## Other agent contracts

Executor and automation agents are not reviewers and use role-specific results. Keep their
contracts separate from the reviewer contract.

An executor reports changed artifacts and incomplete work:

```json
{
  "status": "success",
  "files_modified": ["path/to/file.ts"],
  "files_created": [],
  "summary": "Implemented the bounded task."
}
```

An automation agent reports actions and observable results:

```json
{
  "status": "success",
  "actions": ["ran tests"],
  "results": {},
  "errors": []
}
```

## Orchestrator responsibilities

The orchestrator launches a fresh reviewer instance with the touched artifacts, deleted or
renamed-file evidence, generated or mechanical evidence, relevant requirements, and complete
related contracts or callers. Freshness is an orchestration property; the reviewer does not need
round history.

Wave mechanics and findings handling live in the shared reviewer contract
`skill://methodology/references/reviewer-contract.md`, sections "Review waves" and
"Findings are diagnoses, not a work queue", instead of being restated here: the complete-set wave,
the wave counts, the stop rules, and the diagnose-then-authorize sequence. The orchestrator-specific
part of the loop: after the final permitted wave it corrects remaining local defects only within
the agreed behavior, runs the applicable direct checks, and returns the remaining findings and
required scope and design decisions to the user instead of launching another reviewer; a new
explicit user request starts another review cycle.

If a durable log is needed, the orchestrator stores the returned JSON. The reviewer does not need
a report path or write permission.

## Invoking agents from skills

Reference a dedicated agent by its role and provide complete input without prescribing a
runtime-specific transport:

```markdown
Run a fresh `fw-code-reviewer` with:
- touched, deleted, renamed, generated, and mechanical artifacts;
- the user request or user-spec;
- applicable repository instructions and project contracts;
- relevant callers, dependencies, and validation evidence.

Handle the returned findings under the shared reviewer contract instead of restating its
"Findings are diagnoses, not a work queue" rules here: read
`skill://methodology/references/reviewer-contract.md` and apply them.
```

Dedicated agent descriptions should state purpose, trigger, and exclusions concretely. Keep
large domain prompts in the preloaded skill rather than duplicating them in every caller.
