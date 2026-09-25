<!--
Scaffold for the project README. README is for humans — write the final content
in the language the user writes in. Headers below are a starting point; localize them too.
-->

# [Project name]

> **This README is for the project owner**, not for AI agents.
> Instructions for agents live in AGENTS.md and the .agents/skills/project-knowledge/ skill.

## About

[Short description: what the project does and why it exists]

## Project structure

```
AGENTS.md                        # Agent entry rules: language, behavior, scope, worktrees, security
.agents/
└── skills/
    └── project-knowledge/       # Project documentation for AI agents
        ├── SKILL.md             # Router: what the project is, which reference to read when
        └── references/
            ├── project.md       # Purpose, audience, scope, capabilities
            ├── architecture.md  # Stack, components, integrations, data model
            ├── patterns.md      # Conventions, Git workflow, testing, business rules
            ├── deployment.md    # Environments, routine delivery, operations, recovery
            └── ux-guidelines.md # Optional: interface language, tone, design system

.omp/mcp.json         # Optional MCP config (omp only); read the MCP warning below
.gitignore            # Ignores .env and secrets, but keeps .env.example
backlog.md            # Feature ideas and bugs (what to do later)
.env.example          # Placeholder for the required environment variable names
work/
├── [feature]/        # Active feature or bug: one user-spec.md each
└── completed/.gitkeep  # Finished features: user-spec.md, plus decisions.md when it has entries
```

Your source code goes wherever you want it — this scaffold only fixes the paths above.

## Trust this project once (pi)

Project knowledge lives in `.agents/skills/project-knowledge/` and is gated by pi's project trust.
Before the first `pi` run, either confirm trust interactively (run `pi`, then `/trust` — the
decision is saved in `~/.pi/agent/trust.json`), or pass `--approve` in headless runs. Without
trust, `-p`/json/rpc runs silently skip `.agents/skills/` (defaultProjectTrust "ask").
omp reads the same path with no trust step.

## Optional MCP config (omp only) — trust and pinning

`.omp/mcp.json` is opt-in and is **not** ready to enable as shipped. It runs `npx` on an npm package
name, and that name is unpinned: the run fetches whatever the registry serves under it at that
moment, with your user's permissions. Before you enable the server:

- review the package and pin an exact version in `args` (for example
  `@upstash/context7-mcp@<exact version>`);
- keep automatic install flags out of the config — installing the package must be confirmed, never
  silent;
- delete `.omp/mcp.json` if you do not use MCP.

The framework deliberately pins nothing here and will not invent a version: it does not track that
package. Leaving an unpinned MCP package enabled is your trust decision, and the unpinned default is
recorded as a known limitation of this template.

## Development methodology

The project uses a **spec-driven approach** with AI agents:

1. **User Spec** (user's language) → agree on the complete outcome
2. **Implementation** → in a fresh session, the AI agent executes that user-spec directly
3. **Finalization** → project documentation is updated and the feature is archived

Future feature ideas and known bugs are tracked in `backlog.md`. Active feature and bug work lives
in the `work/` folder.
