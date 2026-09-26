---
name: documentation-writing
description: Creates, updates, audits Project Knowledge docs; "обнови документацию"; not ADR grilling
---

# Documentation Management

## When to Use

Use when: "заполни документацию проекта", "опиши проект", "создай Project Knowledge",
"проведи интервью по проекту", "проверь документацию", "обнови документацию",
"аудит документации", "plan a new project", "fill project documentation",
"check docs", "audit documentation", "update docs" — the project's own durable documentation
must be created, updated, or audited.
For a design-grilling interview that only records ADRs or a glossary for one plan — use
`grill-with-docs` instead.

For reading docs or explaining concepts, read project-knowledge skill directly.

Create and maintain `.agents/skills/project-knowledge/` from the evidence source the user named.

Outside Feature Finalization Mode, follow
[create-project-knowledge.md](references/create-project-knowledge.md) when the user starts or
continues initial documentation and either its interview is still in progress or Project Knowledge
is missing, still a template, or only partially filled. Apply
[project-knowledge-structures.md](references/project-knowledge-structures.md) for content ownership
and structure. After writing, continue at Documentation Review.

When the user explicitly asks to reorganize existing Project Knowledge, apply
[project-knowledge-structures.md](references/project-knowledge-structures.md). Ordinary updates
preserve the filled structure already in use.

## Project Documentation Sources

A project keeps exactly two hand-written documentation sources: the root `AGENTS.md` entry point
and `.agents/skills/project-knowledge/`. Nothing is generated from them, so there is no mirror, no
conversion step, and no sync command. Keep both current in the same task that changes a documented
fact and commit them together.

## Documentation Principles

The reader should understand the project's purpose, structure, decisions, and operation without
reconstructing them from code. Record durable project-specific facts: purpose and business logic;
architecture, components, and their relationships; lasting agreements, decisions, and why those
decisions were made; security rules and configuration names; deployment, operations, monitoring,
recovery, where key code lives, and operational details an agent cannot infer from configuration
alone.

Do not list functions, classes, local control flow, or implementation details that can be read from
code. Treat an important non-obvious rule that applies only to a particular code path as code-owned:
keep it out of Project Knowledge, and change a nearby code comment only when the user also requested
source changes.

Keep generic framework, Git, Linux, SSH, Docker, `journalctl`, and `systemctl` explanations out of
Project Knowledge. For operations, preserve facts such as host, user, non-default port, SSH alias,
service or container name, log location, monitoring URL, environment-variable names, and emergency
recovery behavior. Store an exact command only when the procedure is non-standard and cannot be
recovered from project configuration.

Use source links instead of code snippets or pseudocode. Each fact has one owner file; update the
existing section and cross-reference it elsewhere instead of appending a duplicate. `patterns.md`
contains project-specific conventions, not general implementation advice.

Plans, user specs, tech specs, handoffs, and other `work/` artifacts are evidence, not owners of
current project state. Keep changing inventories in their authoritative registry, configuration,
or runtime source; Project Knowledge records the durable rule, not current counts or members. If a
Project Knowledge claim depends on a completed work artifact, correct that boundary instead of
expanding the artifact.

File size alone is not a finding. Report a size-related issue only when evidence demonstrates
duplication, stale content, implementation-level detail, or a structure that prevents useful
selective loading.

## Phase 1: Select the Evidence Source

Use the narrowest mode that matches the user's request:

1. **One current change:** inspect the changed lines, the files they affect, and related callers or
   contracts needed to understand the durable result.
2. **Named commit or range:** inspect exactly that commit or range plus the related files needed to
   interpret it.
3. **Recent history:** when the user asks for the last N commits, inspect those N commits and their
   resulting current code.
4. **Full update or audit:** inspect current code, all Project Knowledge, and `AGENTS.md`.
5. **Specific documentation edit, consistency check, or status:** inspect the named section and the
   documentation it can contradict.
6. **Feature finalization:** use this mode only when the user explicitly asks to finish a feature
   (including `/done`) and provides or identifies `work/{feature}/`.

Do not search for `user-spec.md` or require it outside feature-finalization mode. A normal
"update documentation" request does not archive work or create a finalization commit.

## Phase 2: Establish Durable Facts

1. Read the selected evidence and current target documentation before editing.
2. Trace names, versions, service boundaries, data model, environment variables, deployment
   triggers, and operational facts to current sources. For full audits, also check placeholders,
   duplication, stale links, generic tutorial content, inconsistent terminology, and facts that no
   longer match the code.
3. If Project Knowledge has no writable owner in the selected non-creation mode, report that no
   documentation target exists. Feature finalization keeps its explicit missing-documentation
   behavior below rather than starting an initial project interview from feature evidence.

## Phase 3: Update or Report

1. For an edit/update request, integrate facts into existing sections and update any directly
   contradicting references.
2. For an audit, consistency check, or status request, report evidence-backed issues without
   changing files unless the user also asked for fixes. Status classifications are filled, partial,
   template, or missing; size alone does not determine status.
3. Keep the `AGENTS.md` entry point and the Project Knowledge references consistent with the facts
   just changed; update both in the same task.

## Documentation Review

1. Run the review waves for the touched documents under the shared reviewer contract
   `skill://methodology/references/reviewer-contract.md`, sections "Review waves" and
   "Findings are diagnoses, not a work queue" — wave counts, stop rules, and findings dispositions
   live there. Wave 1 is a fresh `fw-docs-reviewer` (autoloads `documentation-writing`) with the
   complete touched documents, the selected evidence boundary, related code and contracts, and the
   user's request; it returns its JSON result directly, and a later wave re-reviews the corrected
   documentation with a fresh reviewer.
2. Findings are diagnoses for agreed normal documentation: apply only an authorized local
   correction. Surface unrelated pre-existing defects without changing them.
3. After the final permitted wave, make only remaining local corrections inside the requested
   documentation change, run the applicable direct checks, and show the user any remaining findings
   or required decisions.

## Feature Finalization Mode

1. Read `user-spec.md`, `decisions.md` when present, the implementation, and the relevant Git
   history. Compare the implemented result with the agreed spec.
2. If the feature is evidently incomplete, explain the concrete gap and ask whether to continue
   finalization.
3. Update only affected Project Knowledge through Phases 2-3 and Documentation Review. If Project
   Knowledge is missing, report that the documentation update was skipped and continue archival
   and finalization.
4. Move deferred or rejected scope that survived `logs/userspec/interview.yml` but is not covered by
   the agreed spec into the project's backlog, marking each item with the feature it came from
   (`from: {feature}`). When the project has no backlog or no backlog convention, ask the user where
   to record it instead of inventing a second convention. An item that exists only in the interview
   log is routed before that log is removed.
5. Remove active Project Knowledge and backlog links that treat `work/{feature}/` as a current
   source; do not add current operational inventory to completed artifacts.
6. Archive after documentation review: move `user-spec.md` and `decisions.md` (only when it holds
   material entries) to `work/completed/{feature}/`, and remove the remaining feature artifacts —
   `code-research.md`, `split-context.md`, and any other intermediate file — from the worktree.
   The approved spec and decisions are the only artifacts a completed feature keeps; everything
   else is planning trail, not an archive.
7. Stage the deletions of tracked files in the same commit as the Project Knowledge changes, commit
   with a concise documentation message, and report the updated files and completed-feature path. A
   finalization commit that leaves tracked artifacts in the worktree or stages them as still
   present is incomplete. An artifact that is untracked — `work/{feature}/logs/` is ignored by the
   project `.gitignore` in projects created from the bundled template — has nothing to stage; remove
   it from the worktree and do not force-add it.

This is the only mode that reads feature artifacts by default, archives a feature, or creates the
finalization commit.

## Agent Entry Point

Keep `AGENTS.md` as the compact entry rulebook it is: language, behavior, task scope, worktrees, and
security. Detailed project information belongs in Project Knowledge
(`.agents/skills/project-knowledge/`), not in `AGENTS.md`.
Template: `~/.agents/skills/project-initialization/assets/new-project/AGENTS.md`.

## Self-Verification

- [ ] The requested documentation outcome matches the selected evidence and remains within scope.
- [ ] No unresolved material deviation or contradiction is hidden from the user.
