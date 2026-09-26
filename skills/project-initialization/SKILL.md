---
name: project-initialization
description: Initializes new projects ("инициализируй проект", template, Orca, GitHub repo)
---

# Project Initialization

## When to Use

Use when: "инициализируй проект", "создай новый проект", "init project", "initialize project"

Initialize the project in the current working directory. Existing project files are preserved in
an `old*` directory for later review; do not merge them into the new scaffold during this workflow.

## The Bundled Template

The bundled template is self-contained: the files it ships are the files the project uses, with no
generation step in between. It provides `AGENTS.md` (handwritten entry rules for agents, read by omp
and pi without a trust step), `.agents/skills/project-knowledge/**` (the project's own knowledge
skill, filled in later), `.omp/mcp.json` (optional MCP configuration, off by default), `.gitignore`,
`README.md` (carries the one-time `pi` trust step), `backlog.md`, `.env.example`, and
`work/completed/.gitkeep`.

## 1. Check the Current Directory

Work only in the current directory. If it is already a Git repository with uncommitted changes,
ask whether to commit them first, continue while preserving them in `old*`, or stop. Do not proceed
until the user chooses.

Resolve the directory of this loaded `project-initialization` skill and set `INIT_SKILL_DIR` to that
absolute path. Verify that its `assets/new-project/` directory exists before moving project files.

## 2. Preserve Existing Files and Apply the Template

If the current directory contains anything other than `.git`, move all such entries into the first
available directory named `old`, `old2`, `old3`, and so on. Do not move `.git`.

```bash
OLD_DIR=""
if find . -mindepth 1 -maxdepth 1 ! -name '.git' -print -quit | grep -q .; then
  OLD_DIR="old"
  N=2
  while [ -e "$OLD_DIR" ]; do OLD_DIR="old${N}"; ((N++)); done
  mkdir "$OLD_DIR"
  find . -mindepth 1 -maxdepth 1 ! -name '.git' ! -name "$OLD_DIR" -exec mv -- {} "$OLD_DIR/" \;
fi

cp -rp "$INIT_SKILL_DIR/assets/new-project/." .
```

If `OLD_DIR` is non-empty, inspect it for `.env*`, `*.key`, `*.pem`, `credentials.json`, and
`secrets/`. Ensure every sensitive path is covered by the new `.gitignore` before staging files.
Never print secret contents.

## 3. Initialize Git

Initialize Git with `main` as the primary branch when needed. For an existing repository, preserve
its history and make the current primary branch `main`. Then:

1. Stage the scaffold and preserved `old*` directory, subject to the secret check above.
2. Create the first initialization commit. If the repository already has history, create a normal
   initialization commit instead of rewriting existing commits.

## 4. Connect GitHub and Create Branches

GitHub is required for this workflow. Verify that `gh` is installed and authenticated.

- If `origin` already exists, show its URL and ask whether it is the intended repository. Stop on
  a mismatch rather than replacing the remote. Confirm through `gh` that the repository is private;
  if it is public, stop and ask whether to make it private or use another repository.
- If `origin` does not exist, ask for the GitHub repository name unless already supplied. The
  supplied name authorizes creating the private repository. Create it with
  `gh repo create {name} --private --source=. --remote=origin`.

Before any push, inspect whether a local or remote `dev` branch already exists. If neither exists,
create `dev` from `main`. If either exists, show its relationship to `main` and ask whether to reuse
it; never reset or recreate an existing `dev`, and stop if local and remote histories conflict.

Ask explicitly before pushing `main`. After approval, push `main`, push the created or approved
`dev`, leave `dev` checked out, and read the canonical repository URL through `gh`.

## 5. Register the Project in Orca

A checkout on disk is not yet an Orca project. Orca keeps its own registry of repos, durable
projects and per-host setups, and the worktrees, terminals, and handoffs of the project are created
from that registry. Register the checkout that steps 1–4 produced:

```bash
orca repo add --path "$PWD" --json
```

Orca derives the identity from the folder itself — a repository with a GitHub remote becomes
`github:{owner}/{repo}`, a folder without one becomes `repo:{id}` — and creates the project plus a
`ready` setup for this host. Confirm with `orca repo list` (one line for the folder) and
`orca project setups` (one `ready` setup pointing at this checkout), and report both ids.

Other hosts and machines:

- `orca project setup-existing-folder --project {id} --host local --path {absolute-path} --kind git`
  imports a checkout for a project identity that already exists. A path whose remote does not match
  the given id is refused (`Imported folder does not match the selected project identity`), so never
  invent an id — register the folder first and reuse the id `orca repo add` reported.
- `orca project setup-clone --project {id} --host {host} --url {clone-url} --destination {parent-dir}`
  lets Orca clone the repository on another machine instead of copying a folder.
- `--host local` is this machine (`orca host list`). A paired runtime uses
  `--host runtime:{environment-id}` from `orca environment list`, and SSH targets are set up in the
  Orca desktop UI.

Orca places the worktrees of a project under its own base path; to choose a different one, update the
setup record: `orca project setup-update --setup {setup-id} --worktree-base-path {path} --json`.

Registration is best effort: if the `orca` executable is absent or its runtime is unreachable
(`orca status`), report that and finish the workflow — the repository is complete without it.

Two boundaries stay with Orca, not this workflow: worktrees, terminals, handoffs, and file isolation
are created through Orca, and no second checkout or nested copy of the project is made here. When the
work needs a fresh context, ask Orca for a worktree.

## 6. Report the Result

Report:

- the GitHub URL;
- the created or reused `main` and `dev` branches;
- the Orca project id and the setup state for this host, or why registration was skipped;
- the preserved `old*` directory, or that the directory was initially empty;
- that `dev` is the active branch;
- that the project `README.md` carries the one-time trust step for `pi`;
- the next step: create the initial Project Knowledge with `documentation-writing`.

Do not review or merge files from `old*` during initialization.
