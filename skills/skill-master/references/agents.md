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
  reviewer-specific investigation, direct JSON response, and the freedom to challenge the chosen
  approach or describe a useful alternative within its lane. It does not edit or make the release
  decision.
- The caller owns supplying complete context and explaining the review to the user. It applies no
  reviewer finding until the user explicitly approves the specific change.

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
Review only: no edits or release verdict; you may challenge the approach and describe a useful
alternative within this lane.
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

The shared stance, result schema, review-stage rule, and findings handling live in one place: the
`methodology` skill's reviewer contract (`skill://methodology/references/reviewer-contract.md`).
Reviewer roles read it before reporting. This section covers the orchestrator-facing mechanics that
surround it.

A reviewer, validator, checker, scanner, or critic reviews the supplied artifact within its defined
lane. It does not modify the artifact or decide whether the result may ship.

### Stance and scope

The reviewer starts from fresh context, reads the complete artifact, and follows relevant
callers, dependencies, standards, and contracts. Apply the preloaded lane rather than a generic
preference. The reviewer may report defects, unnecessary complexity, a simpler approach, a
different design, an improvement, or an additional scenario when relevant to that lane. Explain
what was observed and why it matters; unsupported preference is not useful. Accuracy matters more
than finding count, and a clean result is complete.

The orchestrator also supplies a short implementation explanation when reviewing completed work:
what changed, how the result works, why this approach was chosen, deliberate limits, and
assumptions. Treat this explanation as a claim to verify against the request, project evidence, and
artifact, not as authority. For a review of existing material, use the review goal and known usage
instead of inventing an implementation rationale.

Review the current change or other scope supplied by the orchestrator. An unrelated pre-existing
problem is not a finding unless the supplied scope includes it or the current change creates a
demonstrable path to it.

A finding gives the caller enough context to explain the relevant behavior, what is wrong or
proposed, when it matters, and the consequence. Do not suppress a demonstrated finding because its
trigger is rare.

### No patch or release verdict

Findings describe the violated property or proposed alternative; they do not include patches,
corrected code, a full remediation plan, or a release verdict. The reviewer may describe a useful
alternative within its lane. Diagnostic fields such as severity or category are reporting metadata
only; they do not decide the orchestrator's action.

### Result schema

Return the JSON directly as the subagent result. The complete schema lives in one place — the shared
reviewer contract (`skill://methodology/references/reviewer-contract.md`): the four required
top-level keys (`status`, `findings`, `clean_check`, `summary`), the per-finding fields
(`location`, `finding`, `reasoning`, `alternative`), and the clean-result shape. Read it before
reporting and follow it exactly instead of restating the schema here; a second copy would drift.

A domain agent may add `evidence`, `conditions`, `impact`, `severity`, `category`, or other useful
fields inside a finding. Order findings by importance. A bare assertion that the artifact is fine
is not an adequate clean check.

### Reviewer skeleton

```markdown
You are a fresh skeptical {lane} reviewer. Review the complete supplied {artifact} and relevant
context within that lane. You may challenge correctness, complexity, the chosen approach, or
missing possibilities and describe a useful alternative. Explain what you found and why it matters;
do not edit or decide whether the result ships. Treat the implementer's explanation as a claim to
verify, not as authority. Return the common reviewer JSON directly. A clean result is valid.
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
renamed-file evidence, generated or mechanical evidence, relevant requirements, related contracts
or callers, validation evidence, and the short implementation explanation described above. Select
the complete reviewer set required by the active skills and launch it in parallel against one
artifact revision.

After reviewers return, apply no finding and do not repeat the review automatically. Explain what
you changed and how it works, then what reviewers found, what it can cause, whether you agree and
why, and what you recommend. Group related points, avoid internal process terms, and wait for the
user's approval before editing.

One review stage reviews one artifact revision. Preserve distinct stages that examine different
artifacts or boundaries, such as a source scan followed by a destination scan. The orchestrator may
still correct problems it finds through implementation, direct checks, or diff inspection before
review begins.

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
- relevant callers, dependencies, validation evidence, and a short explanation of what changed,
  how the result works, why this approach was chosen, deliberate limits, and assumptions.

Handle the returned findings under the shared reviewer contract instead of restating its
findings-handling rules here: read `skill://methodology/references/reviewer-contract.md` and apply
them.
```

Dedicated agent descriptions should state purpose, trigger, and exclusions concretely. Keep
large domain prompts in the preloaded skill rather than duplicating them in every caller.
