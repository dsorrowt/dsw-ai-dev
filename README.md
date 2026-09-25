<div align="center">

# AI-First Development Framework

**Plan → approve → implement → verify → review → finalize.**

![MIT](https://img.shields.io/badge/license-MIT-3ddc97.svg) ![omp · pi · orca](https://img.shields.io/badge/runtimes-omp%20%C2%B7%20pi%20%C2%B7%20orca-6d7cff.svg) ![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-29d3ee.svg) ![13 skills](https://img.shields.io/badge/agent%20skills-13-8b5cf6.svg) ![14 reviewers + 1 researcher](https://img.shields.io/badge/reviewers-14%20%2B%201%20researcher-f472b6.svg)

A compact workflow for software development with coding agents, designed around **omp**, **pi**, and **orca**.

A fork of [molyanov-ai-dev](https://github.com/pavel-molyanov/molyanov-ai-dev).

</div>

## Quick start

```bash
git clone https://github.com/dsorrowt/dsw-ai-dev.git
cd dsw-ai-dev
python3 scripts/fw-install.py install
```

The installer copies skills to `~/.agents/skills/` and agent wrappers to
`~/.omp/agent/agents/`. To preview an uninstall without changing anything:

```bash
python3 scripts/fw-install.py uninstall --dry-run
```

The installer creates no manifest or ledger: the source tree is the only state. A repeated
`install` reconciles differences between the sources and installed copies.

## How the workflow works

```text
  Plan ──▶ Implement ──▶ Verify ──▶ Review ──▶ Finalize
             ▲
             └─ approved user-spec (feature path)
```


| Stage         | Owner                                                                                     | Result                                                   | Gate                                                                                                 |
| ------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Plan**      | `user-spec-planning`                                                                      | specification, interview log, code research              | the user approves the spec after `fw-uspec-quality`, `fw-uspec-adequacy`, and `fw-skeptic` review it |
| **Implement** | `code-writing`, `layout-writing`, `infrastructure-setup`, `prompt-master`, `skill-master` | only the agreed changes                                  | observable behavior matches the specification                                                        |
| **Verify**    | `test-master` and the appropriate smoke/integration/unit boundary                         | evidence of the result                                   | the changed path has actually been exercised                                                         |
| **Review**    | `code-reviewing` and fresh `fw-*` reviewers                                               | evidence-gated findings                                  | no material finding remains unaddressed                                                              |
| **Finalize**  | `documentation-writing`                                                                   | current Project Knowledge and archived feature artifacts | documentation matches the code                                                                       |


Three sources of truth stay separate: the approved `user-spec.md` defines the expected feature
outcome, Project Knowledge stores durable project facts, and code owns implementation details. A
finding is a diagnosis, not an automatically generated task.

## Installation and safety

`fw-install.py` supports only `install` and `uninstall [--dry-run]`. Exit codes are `0` for
success, `2` for refusal or failure, and `3` when there is nothing to uninstall.

- `install` creates missing copies and overwrites copies that differ from their sources.
- Symlinks, directories at file paths, and incomplete source trees are rejected before writing.
- `uninstall` removes only files described by the current sources and preserves unrelated content.
- Backups are not created automatically. Create one separately before installation if needed.

Preview the uninstall plan:

```bash
python3 scripts/fw-install.py uninstall --dry-run
```

## Contents

### 13 Agent Skills


| Area           | Skills                                                                                    |
| -------------- | ----------------------------------------------------------------------------------------- |
| Process        | `methodology`, `project-initialization`                                                   |
| Planning       | `user-spec-planning`, `documentation-writing`                                             |
| Implementation | `code-writing`, `layout-writing`, `infrastructure-setup`, `prompt-master`, `skill-master` |
| Quality        | `test-master`, `code-reviewing`, `layout-reviewing`, `security-auditor`                   |


### 15 agent wrappers

`agents/fw-*.md` contains **14 reviewers and one researcher**. Each reviewer gets fresh isolated
context, a bounded role, and a minimal tool set. All 14 reviewers use the shared
[reviewer contract](skills/methodology/references/reviewer-contract.md).
`fw-code-researcher` gathers evidence for planning and writes `code-research.md`.

## Runtimes


| Capability      | omp                                       | pi                                          | orca                           |
| --------------- | ----------------------------------------- | ------------------------------------------- | ------------------------------ |
| Skills          | `~/.agents/skills/` after installation    | same location; project skills require trust | shared bundles                 |
| Agent layer     | `~/.omp/agent/agents/` after installation | no subagents                                | separate worker processes      |
| Project context | `AGENTS.md`                               | `AGENTS.md` and trust                       | —                              |
| Orchestration   | in-session `task`                         | an orca worker is needed for fresh context  | worktrees, terminals, handoffs |


Choose one orchestrator per step: the in-session `task` tool **or** an orca worker, never both.
pi does not launch subagents itself. Wrapper model selection comes from runtime configuration,
not from the wrapper.

## Boundaries

- The project template includes `.omp/mcp.json`; review it and pin an exact package version before
enabling it.

- `project-initialization` creates a project from the bundled template and can register it in Orca;
worktrees, terminals, and handoffs remain Orca responsibilities.

## Repository map

```text
skills/       13 Agent Skills: process, planning, implementation, quality
agents/       15 fw-* wrappers: 14 reviewers + 1 code researcher
scripts/      fw-install.py — stateless install/uninstall
AGENTS.md     language, behavior, scope, worktree, and security rules
```

## License

MIT © 2024 [Pavel Molyanov](https://molyanov.ru), author of the original
[molyanov-ai-dev](https://github.com/pavel-molyanov/molyanov-ai-dev). Full text: [LICENSE](LICENSE).