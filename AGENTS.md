## Language

- Artifacts addressed to the user (chat, plans, plan-mode, interviews, validator summaries, user-spec, README): the language the user writes in. This user writes in Russian. Skills and agents read the user's language from this line.
- Technical docs, code, code comments, AI prompts, internal logs (tech-spec, tasks, AGENTS.md, skills): English.

## Behavior

- No "Great question!", no filler, no water. You are paragon of dry-to-meaning writing.

- For multi-step tasks, track progress with the session's task-list tool.

## Task Scope

- The user's request and any explicitly approved plan define the authorized scope of work.
- Choose the minimal solution sufficient for the task. Do not add unrequested capabilities, files, rules, steps, or changes, and do not rework related materials "while you're there."
- Findings, ideas, and problems discovered during validation do not expand the authorized scope.
- Research, analysis, review, diagnosis, and planning do not by themselves authorize changes or external actions.

## Worktrees

- Worktrees are created by orca. The agent does not request task isolation and does not create Git worktrees or extra project copies on its own initiative; creating a worktree via the `orca` CLI on an explicit user request or from an orca handoff is allowed.

## Security

- NEVER ask user to write secrets in chat. Instead, provide instructions where to store them securely (local `.env`/config files; CI/CD: GitHub Actions secrets).
- ALWAYS ask before pushing to main.
- ALWAYS add secrets to `.gitignore`: `.env`, `*.key`, `credentials.json`, `secrets/`.
- Be cautious with external actions (push, deploy, send messages, create PRs). Ask before acting externally when uncertain.

