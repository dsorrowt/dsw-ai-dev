---
name: layout-writing
description: Implements or adjusts layouts to match Figma/макет/вёрстка/адаптив; not blank-slate design
---

# Layout Writing

## When to Use

Use when: "сверстай по Figma", "поправь вёрстку", "подвинь блок", "перенеси из макета", "сделай адаптив", "добавь в том же стиле", "implement layout", "match Figma", "fix responsive layout" — a layout must be implemented or adjusted against a source or an existing project style.
For blank-slate visual design with no source to match — use `frontend-design` instead.
Use alongside code-writing for mixed layout and business-logic tasks; use code-writing alone for logic-only work.

Deliver a layout that matches its exact source where one exists, fills only genuinely unspecified
decisions from project evidence, and works at relevant widths in the existing codebase.

## Scope and Source

1. Read repository guidance, the affected component and styles, tokens, fonts, images, nearby
   components, and the relevant run or build command.
2. Classify the scope:
   - `selected area` — verify the changed element, component, or section with its nearest context;
   - `whole page` — build an ordered inventory of every major visual block from source metadata,
     node IDs, a DOM outline, or complete source-image segments, then verify every item.
3. With an exact source, apply [reproduce.md](references/reproduce.md) — source acquisition,
   native-size evidence, and comparison. Without an exact source, apply
   [design-decisions.md](references/design-decisions.md) — project-first decisions for unspecified
   values. For a partial source, apply each reference only to the area it governs.
4. Ask only for blockers that project or source evidence cannot resolve: the relevant frame when
   a Figma link names only a file, substitution of a required missing font or asset, or expansion
   beyond the requested scope.

Before editing a non-trivial layout whose intended appearance is not defined by an approved
user-spec, an exact visual source, or a user-approved plan, briefly describe in simple user-facing
language how the result will look and behave at relevant screen sizes and why it fits the existing
project style, then wait for approval.

Treat a new requirement, state, edge case, or improvement discovered during implementation or
review as a proposal, not authorization. If it changes the agreed presentation, behavior, scope,
approach, or material complexity, explain it and get the user's decision first. Correct
autonomously only a local mismatch in agreed normal presentation. Treat a rare or source-undefined
viewport, content state, or interaction state as a user decision even when its correction looks
local.

`layout-writing` owns markup structure, styles, responsive behavior, typography, asset placement,
and visual verification. `code-writing` owns data flow, state, APIs, validation, and business
behavior; use both for mixed work.

## Implement and Capture Evidence

1. Reuse suitable project components, tokens, primitives, fonts, images, and the asset pipeline.
   Implement the smallest change that satisfies the request; exact-source values override general
   design taste, while unspecified decisions follow project evidence.
2. Build a deduplicated viewport list for `capture.mjs` and pass it explicitly with `--viewports`:
   - `360`, `430`, `768`, and `1440` widths for baseline responsive coverage;
   - every established exact-source or user-screenshot viewport;
   - widths immediately before and after affected CSS breakpoints.
   Use the owning source height when known; otherwise choose one stable representative height and
   reuse it across captures and reruns.
3. Before capturing, create one temporary evidence root outside the repository. Give every
   capture or overlay invocation a new child `--out` path because the scripts reject existing
   targets and prior evidence must remain unchanged.
4. At every chosen width, render the selected area or every whole-page inventory block with its
   nearest relevant context and affected states. Apply the native-size comparison procedure from
   `reproduce.md` wherever an exact source exists; otherwise inspect composition, wrapping,
   clipping, crop, states, and horizontal overflow.
5. Correct confirmed mismatches and repeat only affected blocks and widths with new output paths.
   Run the smallest project check that proves the changed route still compiles or renders.

## Live Variant Mode

Optional, and only when the person is present in a browser: pick an element, generate variants,
accept one and it lands in source. It does not replace the capture procedure above; it precedes a
normal capture-and-review when the direction is still open. Needs the global `impeccable` skill.

```bash
IMPECCABLE_LIVE_COPY_AGENT=chat <skill-base>/scripts/impeccable live \
  --allow-missing-context --dev-url --auto-config
```

- `chat` keeps Apply inside this session. The default `auto` falls back to the `codex` or `claude`
  CLI with approvals and sandboxing off once nothing has polled for a minute, which also walks
  around this repository's hooks.
- `--allow-missing-context` boots without `PRODUCT.md`/`DESIGN.md`; `contextMissing` in the output
  is informational. Design context stays in Project Knowledge instead of new root files.
- Open the URL the boot reports: `pageUrls[0]` for a static folder, `devUrl` for a running dev
  server. Start `devCommand` yourself only when nothing answers on it.
- Service the poll as a supervised long-lived process with notification, never as a one-shot
  command: `live-poll` with its default long timeout, notify on
  `"type":"(generate|steer|accept|discard|manual_edit_apply|variant_mount_failed|exit)"`, and on
  each event follow `skill://impeccable/reference/live.md`, then
  `live-poll --reply <event-id> <status>` and poll again immediately.
- Stop with `impeccable live-server stop`. `.impeccable/` is private state, gitignored by the boot
  and safe to delete; the only other footprint is a marked block appended to `.gitignore`.

## Review and Hand Off

After every implementation, run one review stage with one fresh `fw-layout-reviewer` (autoloads
`layout-reviewing`) and no model override. Pass the request, scope, changed files, applicable
repository instructions and project-pattern evidence, source mode and responsibility boundary,
all checked widths, site images for every checked block and state, source and difference images
where applicable, the complete inventory and evidence set for a whole page or segmented tall block,
and a short explanation of what changed, how the layout behaves, why this approach was chosen,
deliberate limits, and assumptions. Include reviewers required by other active skills in the same
stage rather than starting a separate review sequence.

After reviewers return, do not change the layout from their findings or repeat the review
automatically. Explain what you changed and how the layout behaves, then what reviewers found, what
it can cause, whether you agree and why, and what you recommend. Wait for the user's approval;
recapture and directly inspect affected widths and states after approved changes.

Hand off with the change summary, checks run, widths and blocks actually verified, reviewer
findings and your assessment, and known evidence limitations.
