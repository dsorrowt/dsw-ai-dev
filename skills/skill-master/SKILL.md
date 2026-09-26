---
name: skill-master
description: Guides skill creation and updates; "создай скилл"; not vendored updates
---

# Skill Creator

## When to Use

Use when: "создай скилл", "измени скилл", "гайд по скиллам", "обнови скилл", "улучши скилл",
"create skill", "update skill", "skill guide", "new skill", "how to write a skill"

Do NOT use for updating, re-fetching, or restoring a vendored skill from its upstream source —
use `update-skills` instead.

## About Skills

Skills give the agent domain knowledge it does not have or a specific way of working needed by
the user.

Assume the agent can use ordinary tools, understand the current conversation, notice command
failures, and handle routine recoverable errors. Add an instruction only when the task, an
established contract, or a security, authorization, data-loss, or irreversible-action boundary
requires it. Do not add required actions, checks, state, or branches for behavior the agent can
already handle, and do not re-check immediately visible results.

Correct a local defect only when it restores agreed normal behavior. Treat a rare or unagreed
scenario, or a correction that adds behavior, state, entities, contracts, dependencies,
architecture, or material complexity, as a user decision; after the decision, encode the chosen
behavior or omit special handling.

## Skill Types

There are two types of skills based on how they guide the agent's work.

### Procedural Skills

Use when the skill defines a way of working or a sequence of actions. Describe it in the form and
detail the task requires. Phases, checkpoints, and explicit state are tools for real dependencies,
not required features of a procedural skill.

**Creating a procedural skill?** Read [procedural-skills.md](references/procedural-skills.md) — phase structure, checkpoints, verification patterns.

### Informational Skills

Use when providing methodology, knowledge, or guidelines without a required execution order.
Organize content by topic. Add decision guidance only where the task contains a real choice.

**Creating an informational skill?** Read [informational-skills.md](references/informational-skills.md) — section organization, knowledge structure.

## 1. Discovery

For a new skill or major change, reuse the request and project facts to establish purpose, routing,
scope, and required output. If a material design decision remains unresolved, run the adaptive
interview from [interview-guide.md](references/interview-guide.md) — question admission, stopping
rule, and handling decisions the user cannot answer. Otherwise proceed without an interview.

## 2. Skill Structure

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

### Frontmatter

**`name`** (required):
- kebab-case (lowercase, hyphens)
- ≤64 characters
- Exactly matches the skill directory name
- Unique identifier

**`description`** (required):
- Third person ("Analyzes code...", NOT "I analyze...")
- One line, and a plain scalar: `description: <text>` with no block scalar (`|`, `>-`) and no second
  line.
- The session prompt renders it verbatim only when it is a single line of ≤12 words and ≤160
  characters. Longer text is truncated to the first line plus "…" and then lossily compressed, so
  anything past that budget is unreliable.
- Sentence case, no trailing period.
- Include both WHAT the skill does AND WHEN to use it within that budget.

#### Description Best Practices

The runtime puts the description in the session prompt and uses it to decide when to auto-invoke
the skill. Be specific, and fit the key terms into that one line: the trigger terms users actually
say must be part of it.

**Template:**
```yaml
description: <what the skill does>; <strongest trigger terms>; not <near-miss>
```

Fuller routing guidance belongs in the body, not the description: put the `Use when:` list, the
near-misses, and the cross-references into a `## When to Use` section right after the H1, where
they cost no prompt budget. Only the WHAT phrase and the strongest triggers stay in the
description.

Use concrete positive routing: name the real intents and only the wording variations needed to
distinguish the skill's domain.

**Bad:**
```yaml
description: |
  This skill helps with documents.

  Use when: user wants to work with docs, fills documentation, checks documentation, updates
  documentation, audits documentation, plans a new project.
```
**Good:**
```yaml
description: Manages Project Knowledge docs; "заполни документацию"; not ADR-only grilling
```
#### Negative Triggers

Add a "not for ..." clause to the same line only when the skill genuinely overlaps a neighboring
skill or has a plausible near-miss, and only while the line budget still fits. Negative routing
should resolve a real ambiguity, not pad the line.

```yaml
description: Writes tests at the smallest reliable boundary; "напиши тесты"; not TDD
```

**Need `disable-model-invocation` or another optional field?** Read
[frontmatter-options.md](references/frontmatter-options.md) — the fields the runtimes actually read
and when to use each. No skill frontmatter reads a `model` field: omp recognizes it only in agent
files, and no framework wrapper ever sets it — the model comes from runtime configuration, and a
skill or role names only the `fast`/`good` class.

### Body

Every SKILL.md body consists of:
- **Core workflow** — main instructions that are always needed
- **Links to references** — for optional/detailed information
- Keep under 500 lines (otherwise → split to references)

**When defining output format**, read [output-patterns.md](references/output-patterns.md) — template pattern, examples pattern.

### Bundled Resources

A skill contains only SKILL.md and these three optional directories — nothing else (no README, CHANGELOG, etc.).

#### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for **deterministic mechanical work** — the kind of thing a model should not be redoing by hand each run.

Use scripts for repeated deterministic work such as calculation, transformation, or scaffolding.
Do not use them to validate model judgment or police the skill's own output. A bundled script
should handle its mechanical errors and expose a clear invocation contract. Keep a bundled script
runtime-agnostic: reference bundled files relative to the script's own location instead of
hardcoding runtime-specific paths, and leave runtime-specific instructions to the SKILL.md prose.

#### References (`references/`)

Content needed in some execution paths, not all. If the skill branches (multiple operations, domains, modes) — each branch's details go to a reference. Content needed on every execution stays in SKILL.md.

- **No duplication**: Content lives in either SKILL.md or references, not both

**How to link references in SKILL.md:**

Embed references where they are used. In the examples below, a path containing `<example>` is a
fictional placeholder for the skill you are designing — this skill ships no such file.

**Pattern A: Action-embedded (strong)** — the workflow step's action IS applying the reference content. The agent cannot complete the step without loading the file.

```markdown
3. Write tests following patterns from [testing-guide.md](references/<example>-testing-guide.md)
   (test structure, naming, what to skip)

4. Apply audit criteria from [principles.md](references/<example>-principles.md) to each file
   (code examples, obvious content, generic explanations)
```

**Pattern B: Condition + contents (basic)** — for optional references needed only in specific scenarios. Each link explains WHEN to read and WHAT's inside.

```markdown
**For tracked changes**, see [REDLINING.md] — revision marks, accept/reject.
**First time with docx-js?** Read [DOCX-JS.md] — setup, examples, pitfalls.
```

Use Pattern A for required rules and Pattern B for conditional details. Do not put references in a
passive resource catalog separated from the workflow.

```markdown
❌ Bad — passive catalog (ignored):
## Resources
### references/<example>-structure.md
Complete description of all files...
### references/<example>-principles.md
Quality principles...

✅ Good — embed each reference into the workflow step where it's needed:
4. Apply audit criteria from [principles.md](references/<example>-principles.md) to each file
```

#### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output the agent produces.

Use assets for templates, images, fonts, boilerplate, and other files copied or modified in the
output rather than read as instructions.

## 3. Writing Guidelines

### Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of the agent as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Progressive Disclosure

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** — always in context as the rendered one-line description (≤12 words)
2. **SKILL.md body** — When skill triggers (<5k words)
3. **Bundled resources** — As needed by the agent (unlimited, scripts execute without reading)

Keep SKILL.md body under 500 lines. Split content into separate files when approaching this limit. When splitting, reference them from SKILL.md and describe clearly when to read them.

Keep core workflow and selection guidance in SKILL.md. Move conditional or variant-specific
details into references, linked where the agent needs them.

```markdown
**For tracked changes**, read [redlining.md](references/<example>-redlining.md) — revision marks and
accept/reject behavior.
```

**Important guidelines:**
- Keep references one level deep from SKILL.md
- For large reference files (roughly over 300 lines), include a short table of contents when it
  materially improves navigation

### Generalize and Explain Why

Write a draft, then remove instructions that do not change the outcome. Generalize from realistic
usage instead of adding branches for isolated examples or hypothetical future configurations.

Prefer positive instructions when they fully convey the rule. Keep explicit negatives for
security, irreversible damage, disambiguation, and scope boundaries.

Explain why a non-obvious instruction matters so the agent can apply it correctly beyond the
example:

**Bad:** "Always return JSON format."
**Good:** "Return findings as JSON — orchestrator parses this automatically, invalid JSON crashes pipeline."

Words such as CRITICAL, MANDATORY, NEVER, IMPORTANT, and MUST do not replace a clear instruction
and its reason. Flag emphasis only when it creates noise, substitutes for motivation, or makes
priorities conflict.

### Delegating Heavy Work

Use subagents when fresh isolated context materially helps review, research, debugging, validation,
parallel work, or high-volume analysis. Use an inline prompt for a bounded one-off task and a
dedicated Skill + Agent only for substantial reusable methodology. Keep detailed agent contracts
out of SKILL.md. Apply [agents.md](references/agents.md) when delegating work or creating a
reviewer.

## 4. Validation

### Run Applicable Reviewers

Launch fresh skeptical reviewers according to what changed. Each applies the evidence gate and
common JSON contract from the `methodology` skill's reviewer contract
(`skill://methodology/references/reviewer-contract.md`); orchestrator mechanics are in
[agents.md → Reviewer contract](references/agents.md):

- `fw-skill-checker` — form, routing, package structure, and references;
- `fw-skill-logic-reviewer` — executable logic on required paths and established contracts;
- `fw-skill-simplicity-reviewer` — unnecessary rules, mechanisms, checks, and complexity.

Use `fw-skill-checker` for form or routing changes, `fw-skill-logic-reviewer` for workflow or
branching changes, and `fw-skill-simplicity-reviewer` when changing rules, phases, checkpoints,
scripts, options, or references. Run all three in parallel for a new skill or a major rewrite. Do
not run an unaffected lane merely to satisfy ceremony.

Provide the user scope, touched artifacts, relevant references and contracts, and validation
evidence. Findings are diagnoses for agreed normal behavior under the shared reviewer contract
`skill://methodology/references/reviewer-contract.md` ("Findings are diagnoses, not a work queue") —
apply only an authorized local correction and reject or ask the user before a material or rare and
unagreed one. Orchestrator mechanics are in
[agents.md → Orchestrator responsibilities](references/agents.md).

All three are defined under `~/.omp/agent/agents/` and autoload `skill-master`.
