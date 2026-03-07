---
description: Generate UX artifacts (JTBD, journey, flows) plus a high-fidelity static HTML prototype from the current feature spec.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only --mode design --input "{ARGS}"
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly -Mode design -InputFile "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Usage / Input File *(MANDATORY)*

This command requires an explicit **input file** as the first token in `$ARGUMENTS`:

- `/sdd.design <spec.md> [notes...]`
- `<spec.md>` can be an absolute path or a repo-root relative path under `specs/<feature>/`.

Examples:

- `/sdd.design specs/001-foo/spec.md`
- `/sdd.design /abs/path/to/specs/001-foo/spec.md 请偏重移动端体验`

If `$ARGUMENTS` is empty: **ERROR** and STOP.

Pre-implementation phases MUST NOT infer feature context from current git branch, `SPECIFY_FEATURE`, or latest `specs/*` directory. Context MUST be derived from the explicit input file.

## Constitution Evidence Source Policy (MANDATORY)

- Load constitution policy from:
  - Preferred: `.specify/memory/constitution.md`
  - Fallback: `memory/constitution.md`
- Treat `## Evidence Source Policy (ISS-MCP)` as policy SSOT for repository-fact assertions in this command.
- If both constitution files are missing, use the bootstrap policy in `templates/constitution-template.md` and explicitly label conclusions as degraded governance context.
- For repository fact retrieval, call-chain analysis, architecture-boundary verification, dependency mapping, and impact-scope tracing, follow that policy exactly.

## Goal

Produce a complete design handoff for the current feature, including:

1. UX research artifacts (JTBD, persona, journey map, flow)
2. UI specification (screens, IA, components, copy, states, accessibility)
3. A high-fidelity static HTML prototype (no backend; mocked data)

This command is optimized for **communication + implementation readiness**, not for pixel-perfect brand design.

SSOT rule: `spec.md` is the requirements SSOT. Design artifacts (`ux/`, `ui/`, `prototype/`) MUST NOT redefine normative requirements; they only translate in-scope requirements into implementation-ready UX/UI/prototype outputs.

## Setup

1. Run `{SCRIPT}` from repo root and parse JSON for:
   - `FEATURE_DIR` (absolute path)
   - `FEATURE_SPEC` (absolute path to `spec.md`)
   - `IMPL_PLAN` (absolute path to `plan.md`, may not exist)
   - `INPUT_FILE_ABS` (absolute path to explicit input file; MUST be `spec.md`)

2. Validate prerequisites:
   - If `FEATURE_DIR` does not exist: **ERROR** and instruct to run `/sdd.specify` first.
   - If `FEATURE_SPEC` does not exist: **ERROR** and instruct to run `/sdd.specify` first.

3. Load context:
   - Read `FEATURE_SPEC`
   - Read the design template pack and use it as the structure baseline for generated artifacts:
     - Preferred (split templates, flat):
       - `.specify/templates/design-template.md` (index + checklist)
       - `.specify/templates/design-ux-template.md` (UX artifacts)
       - `.specify/templates/design-ui-template.md` (UI spec)
       - `.specify/templates/design-prototype-template.md` (static prototype)
     - Fallback:
       - `templates/design-template.md`
       - `templates/design-ux-template.md`
       - `templates/design-ui-template.md`
       - `templates/design-prototype-template.md`
   - If `IMPL_PLAN` exists, read it and extract any UI constraints (platforms, libraries, routes, a11y requirements, design system notes).

## Outputs (write files)

Create these files under `FEATURE_DIR` (create directories if needed):

### A) UX artifacts (`ux/`)

1. `ux/jtbd.md`
   - Primary job statement: `When [situation], I want to [motivation], so I can [outcome].`
   - Primary persona (role, goals, context, constraints)
   - Current alternatives + pain points
   - Success metrics (measurable)

2. `ux/journey.md`
   - Journey stages for the primary scenario
   - For each stage: user actions, thoughts, feelings, pain points, opportunities

3. `ux/flow.md`
   - User flow steps (entry → key decision points → exit)
   - Error/empty/edge states
   - Accessibility requirements (keyboard + screen reader expectations)

### B) UI spec (`ui/`)

1. `ui/ui-spec.md`
   - Screen inventory (at least the primary happy-path screens)
   - Navigation model (routes or page map) + information architecture
   - Component inventory (forms, tables, cards, dialogs, toasts, etc.)
   - Content model (what data is shown/edited, validations, constraints)
   - State model per screen: loading/empty/error/permission/success
   - Copy guidelines + example microcopy (labels, errors, empty states)
   - Accessibility checklist tailored to the feature
   - **Flow continuity contract**: for each primary screen, define the primary forward action, destination screen, and carried continuity keys (`sessionId`, `entityId`, `mode`, `state`, etc. as applicable)
   - **Traceability**: map Spec requirements (FR-### and/or scenarios) → screens/components

### C) Static HTML prototype (`prototype/`)

Create a self-contained static prototype (no build tooling required):

1. `prototype/index.html`
   - A hub page linking to the key screens
   - Includes shared navigation and a consistent layout
   - Includes a runnable happy-path demo entry with explicit step order

2. `prototype/pages/*.html`
   - One HTML file per key screen (minimum 3 screens unless the feature is smaller)
   - Each page includes representative content, forms, and error/empty states (can be in-page sections)
   - Each non-terminal primary screen includes at least one **primary forward action** that performs deterministic navigation to the next mapped screen (real `href` or deterministic JS navigation)
   - Each non-happy state includes an explicit recovery action (retry/back/fix) with a deterministic destination or state transition
   - Primary actions MUST NOT be toast-only placeholders

3. `prototype/assets/styles.css`
   - Design tokens via CSS variables (color, spacing, typography)
   - Components styled to appear “high-fidelity” (not wireframes)
   - Responsive layout rules (mobile + desktop)
   - Visible focus states and reduced-motion support
   - Clear visual hierarchy zones (navigation, primary action area, feedback/status area)

4. `prototype/assets/app.js`
   - Centralized mock store object (e.g., `window.__SPECKIT_MOCK_STORE`) shared across pages
   - Mock data + minimal interactivity for:
     - Tabs/modals/toasts
     - Form validation feedback
     - Switching between “states” (loading/empty/error) via simple toggles
     - Continuity key propagation helpers (query params and/or localStorage) for primary flow transitions
   - No external dependencies

5. `prototype/README.md`
   - How to view (open files locally)
   - Optional local server command examples
   - Flow continuity matrix (`step`, `from page`, `action`, `to page`, `continuity keys`)

## Execution rules

1. **Do not invent requirements**: if the spec is missing key UX details (primary actor, core flow, success criteria), add up to **3** `[NEEDS CLARIFICATION: ...]` markers in `ui/ui-spec.md` and proceed with reasonable defaults, explicitly labeled as assumptions.
2. **Coverage gate**: every in-scope `FR-###` from `FEATURE_SPEC` MUST be mapped to at least one screen in `ui/ui-spec.md` (traceability table). If the spec does not use FR IDs, map scenarios/user stories instead.
3. **Accessibility is not optional**: all interactive elements must have keyboard focus styles and labels; error states must be described with text (not color only).
4. **Static prototype constraints**:
   - Use semantic HTML (`header`, `nav`, `main`, `form`, `button`, `label`, `table`, etc.)
   - Avoid heavy JavaScript; keep it understandable and modular
   - Use mock data that looks realistic for the domain (names, IDs, timestamps)
   - For primary actions, use deterministic navigation (actual link or deterministic JS navigation). Toast-only primary actions are prohibited.
   - Ensure cross-screen continuity with explicit continuity keys and visible binding on destination screens.
   - Non-happy states must be interactive and recoverable; text-only notes are insufficient.
5. **Keep outputs feature-scoped**: write only under `FEATURE_DIR/ux/`, `FEATURE_DIR/ui/`, `FEATURE_DIR/prototype/`.

## Handoff-ready gates *(MANDATORY)*

Before finalizing outputs, enforce these hard gates. If any gate fails, regenerate the affected artifacts.

1. **SSOT alignment gate**
   - `spec.md` remains the requirements SSOT.
   - `ui/ui-spec.md` and `prototype/*` MUST NOT introduce normative behavior that is not traceable to in-scope requirements.
2. **Traceability closure gate**
   - Every in-scope requirement (`FR-###` or scenario) MUST map to screen(s), component(s), and at least one prototype page.
   - Every primary screen (`SCR-xx`) MUST have a concrete `prototype/pages/*.html` mapping row in `ui/ui-spec.md`.
3. **State coverage gate**
   - For each primary screen, define applicable states (`loading`, `empty`, `error`, `permission`, `success`) in `ui/ui-spec.md`.
   - Prototype MUST visibly demonstrate the primary happy path plus at least one non-happy state per primary screen.
4. **Implementation-readiness gate**
   - `ui/ui-spec.md` MUST include route-to-screen mapping, content model (`Entity.field` where available), interaction contract, and accessibility checklist.
   - `prototype/README.md` MUST include demo flow order, assumptions, and implementation notes for frontend handoff.
5. **Context continuity gate**
   - Every non-terminal primary screen MUST expose at least one primary forward action to its mapped next screen.
   - Primary flow must be executable end-to-end without manual URL edits.
   - Continuity keys must be carried across steps and rendered/bound on destination pages.
6. **Interaction fidelity gate**
   - Non-happy states MUST be demonstrably interactive (toggle/view path) and include explicit recovery actions.
   - Each primary screen MUST include at least one non-toast interaction that changes page state or navigation.
7. **No-placeholder gate**
   - Final generated artifacts MUST NOT contain unresolved placeholders such as `TODO`, `TBD`, `[insert ...]`, or `<placeholder>`.

## Report

After writing files, print a short completion summary:

- `FEATURE_SPEC` path
- Paths to created artifacts (UX, UI spec, prototype)
- Handoff gate status (`passed` or `failed`) for: SSOT alignment, traceability closure, state coverage, implementation readiness, context continuity, interaction fidelity, no-placeholder
- Any `[NEEDS CLARIFICATION]` items (if present)
