---
name: layout-writing
description: |
  Reproduces and adjusts web layouts from a design export (Figma, HTML/CSS export, screenshot) or an existing project style with high visual fidelity and proportional verification.
  Use when: "сверстай по Figma", "поправь вёрстку", "подвинь блок", "перенеси из макета", "сделай адаптив", "добавь в том же стиле", "implement layout", "match Figma", "fix responsive layout" — a layout must be implemented or adjusted against a source or an existing project style.
  For blank-slate visual design with no source to match — use `frontend-design` instead.
  Use alongside code-writing for mixed layout and business-logic tasks; use code-writing alone for logic-only work.
---

# Layout Writing

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

## Review and Hand Off

After every implementation, run the review waves for the result under the shared reviewer contract
`skill://methodology/references/reviewer-contract.md`, sections "Review waves" and
"Findings are diagnoses, not a work queue" — wave counts, stop rules, and findings dispositions
live there. Wave 1 is one fresh `fw-layout-reviewer` (autoloads `layout-reviewing`); after an
authorized correction changes the reviewed result, recapture the affected evidence and run the
next wave with a fresh reviewer. Pass
the request, scope, changed files, applicable repository instructions and project-pattern
evidence, source mode and responsibility boundary, all checked widths, site images for every
checked block and state, source and difference images where applicable, and the complete inventory
and evidence set for a whole page or segmented tall block.

Findings are diagnoses for agreed normal presentation; the material areas here are behavior,
state, markup states, component contracts, architecture, and material complexity. Apply only an
authorized local correction, and do not start a wave only for a finding that awaits the user's
decision. After the last wave, correct remaining local mismatches inside the agreed presentation,
recapture and inspect the affected widths and states, and report any remaining findings or
required user decisions.

Hand off with the change summary, checks run, widths and blocks actually verified, finding
dispositions, and known evidence limitations.
