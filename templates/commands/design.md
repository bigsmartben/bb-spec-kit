---
description: Generate UX artifacts (JTBD, journey, flows) plus a high-fidelity static HTML prototype from the current feature spec.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

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

2. Validate prerequisites:
   - If `FEATURE_DIR` does not exist: **ERROR** and instruct to run `/speckit.specify` first.
   - If `FEATURE_SPEC` does not exist: **ERROR** and instruct to run `/speckit.specify` first.

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
   - **Traceability**: map Spec requirements (FR-### and/or scenarios) → screens/components

### C) Static HTML prototype (`prototype/`)

Create a self-contained static prototype (no build tooling required):

1. `prototype/index.html`
   - A hub page linking to the key screens
   - Includes shared navigation and a consistent layout

2. `prototype/pages/*.html`
   - One HTML file per key screen (minimum 3 screens unless the feature is smaller)
   - Each page includes representative content, forms, and error/empty states (can be in-page sections)

3. `prototype/assets/styles.css`
   - Design tokens via CSS variables (color, spacing, typography)
   - Components styled to appear “high-fidelity” (not wireframes)
   - Responsive layout rules (mobile + desktop)
   - Visible focus states and reduced-motion support

4. `prototype/assets/app.js`
   - Mock data + minimal interactivity for:
     - Tabs/modals/toasts
     - Form validation feedback
     - Switching between “states” (loading/empty/error) via simple toggles
   - No external dependencies

5. `prototype/README.md`
   - How to view (open files locally)
   - Optional local server command examples

## Execution rules

1. **Do not invent requirements**: if the spec is missing key UX details (primary actor, core flow, success criteria), add up to **3** `[NEEDS CLARIFICATION: ...]` markers in `ui/ui-spec.md` and proceed with reasonable defaults, explicitly labeled as assumptions.
2. **Coverage gate**: every in-scope `FR-###` from `FEATURE_SPEC` MUST be mapped to at least one screen in `ui/ui-spec.md` (traceability table). If the spec does not use FR IDs, map scenarios/user stories instead.
3. **Accessibility is not optional**: all interactive elements must have keyboard focus styles and labels; error states must be described with text (not color only).
4. **Static prototype constraints**:
   - Use semantic HTML (`header`, `nav`, `main`, `form`, `button`, `label`, `table`, etc.)
   - Avoid heavy JavaScript; keep it understandable and modular
   - Use mock data that looks realistic for the domain (names, IDs, timestamps)
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
5. **No-placeholder gate**
   - Final generated artifacts MUST NOT contain unresolved placeholders such as `TODO`, `TBD`, `[insert ...]`, or `<placeholder>`.

## Report

After writing files, print a short completion summary:

- `FEATURE_SPEC` path
- Paths to created artifacts (UX, UI spec, prototype)
- Handoff gate status (`passed` or `failed`) for: SSOT alignment, traceability closure, state coverage, implementation readiness, no-placeholder
- Any `[NEEDS CLARIFICATION]` items (if present)

## ISS-MCP Evidence Source Policy

- For rigorous reasoning involving code fact retrieval, repository fact assertions, call-chain analysis, architecture-boundary verification, dependency mapping, or impact-scope tracing, you MUST use `ISS-MCP` (Index Search Service) as the primary evidence source.
- This requirement applies to any `Existing` claim and to all repo-derived entries referenced in design artifacts.
- You MUST NOT rely only on memory, unstated assumptions, or local keyword search as the primary basis for repository facts.
- You MAY fall back to local tools (`codebase_search`, `search_files`, `read_file`) only when `ISS-MCP` is unavailable, returns no results, or cannot cover required fields; all such conclusions MUST be explicitly labeled as degraded evidence.
- If required evidence remains unavailable after fallback, use `TODO(<FIELD>): ISS-MCP/local evidence missing` and list it in the design impact report.
