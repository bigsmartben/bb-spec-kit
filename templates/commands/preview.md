---
description: Generate/overwrite specs/<feature>/preview.html as a reviewer-facing review view (Product/Technical/Test) with interactive HTML navigation and verbatim appendices.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Usage / Mode *(MANDATORY)*

This command supports a **stage mode** as the first token in `$ARGUMENTS`:

- `spec` : Spec stage only (spec.md as SSOT). Requires `spec.md`.
- `uiux` : Design stage. Requires `/speckit.design` outputs under `FEATURE_DIR`:
  - `ux/jtbd.md`, `ux/journey.md`, `ux/flow.md`
  - `ui/ui-spec.md`
  - `prototype/index.html`
- `plan` : Plan stage. Requires `plan.md`.
- `tasks` : Tasks stage. Requires `tasks.md` (and integrates `contracts/interface-details/*.md` when present).
- `all` : Full view. Requires only `spec.md` and includes any other artifacts when present.

Examples:

- `/speckit.preview all`
- `/speckit.preview spec`
- `/speckit.preview uiux`
- `/speckit.preview plan`
- `/speckit.preview tasks`

If `$ARGUMENTS` is empty, default to `all`.

If `$ARGUMENTS` contains additional text after the mode token, treat it as reviewer notes and incorporate it as a short note in the Overview page (without inventing requirements).

## Goal

Generate/overwrite a single reviewer-facing read view: `specs/<feature>/preview.html`.

This preview is **not** the SSOT. `spec.md` remains the SSOT for requirements and UDD (`Entity.field`).

The preview must be:

- **Review-first**: explicitly organized by review pages: Overview / Product / UX-UI / Backend / Frontend / Testing / Audit / Appendices
- **Human-first**: Chinese narrative text with bilingual terms where useful
- **Low drift**: prefer verbatim excerpts over paraphrase
- **Interactive**: HTML sections, tables, and collapsible appendices for reviewers

## Constraints

- **Manual only**: This command MUST NOT be auto-triggered by any other command (no handoffs).
- **Overwrite**: Always overwrite `preview.html`.
- **Minimum prerequisite**: Only `spec.md` is required.
- **Write scope**: Do not modify any other files besides `preview.html`.

## Output Language & Stability Contract *(MANDATORY)*

- **Default output language**: write narrative content in **Simplified Chinese (zh-CN)**.
- Keep stable IDs/tokens unchanged: `UC-###`, `FR-###`, `Entity.field`, `CaseID`, `AEI-###`, `operationId`.
- Keep normative keywords unchanged when quoted: `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`.
- Keep paths/code identifiers/CLI commands exactly as source.

## Execution Steps

0. **Parse mode**:
   - Parse `$ARGUMENTS`:
     - `MODE` = first token, case-insensitive; one of: `spec|uiux|plan|tasks|all`.
     - `EXTRA_NOTES` = remaining text after the first token (may be empty).
   - If `$ARGUMENTS` is empty: set `MODE=all`.
   - If `MODE` is not one of the allowed values: **ERROR** and STOP.
     - Show the allowed values and examples.

1. **Resolve paths**:
   - Run `{SCRIPT}` from repo root and parse JSON:
     - `FEATURE_DIR` (expected: `<repo>/specs/<feature>`)
     - `FEATURE_SPEC`
     - `IMPL_PLAN`
     - `TASKS`

2. **Validate**:
   - If `FEATURE_SPEC` does not exist: **ERROR** and STOP.
     - Instruct user to run `/speckit.specify` first, or set `SPECIFY_FEATURE` to the feature directory name for non-git repos.
   - Mode prerequisites (enforced):
     - If `MODE=plan` and `IMPL_PLAN` does not exist: **ERROR** and STOP (instruct to run `/speckit.plan`).
     - If `MODE=tasks` and `TASKS` does not exist: **ERROR** and STOP (instruct to run `/speckit.tasks`).
     - If `MODE=uiux` and any of these are missing under `FEATURE_DIR`: **ERROR** and STOP (instruct to run `/speckit.design`):
       - `ux/jtbd.md`, `ux/journey.md`, `ux/flow.md`, `ui/ui-spec.md`, `prototype/index.html`.

3. **Define output**:
    - `PREVIEW_FILE = FEATURE_DIR/preview.html`

4. **Load templates**:
    - Preferred: `.specify/templates/preview-template.html`
    - Fallback: `templates/preview-template.html`
   - If neither exists: **ERROR** and STOP.

5. **Load documents**:
   - Required: read full `spec.md` from `FEATURE_SPEC`.
   - Optional (load only if they exist):
     - Constitution (terminology authority): `.specify/memory/constitution.md`, else `memory/constitution.md`
   - Then load additional documents depending on `MODE`:
     - `MODE=spec`:
       - Do NOT load or depend on `plan.md`, `tasks.md`, `ux/`, `ui/`, `prototype/`.
     - `MODE=uiux`:
       - Load: `ux/jtbd.md`, `ux/journey.md`, `ux/flow.md`, `ui/ui-spec.md`, `prototype/index.html` (+ key screens under `prototype/pages/*.html` when referenced).
     - `MODE=plan`:
       - Load: `plan.md` from `IMPL_PLAN`.
       - Also load these if present: `data-model.md`, `quickstart.md`, `contracts/openapi.yaml`, `contracts/test-case-matrix.md`.
     - `MODE=tasks`:
       - Load: `tasks.md` from `TASKS`.
       - Also load these if present: `contracts/interface-details/*.md`, `contracts/openapi.yaml`, `contracts/test-case-matrix.md`, `data-model.md`.
     - `MODE=all`:
       - Load everything when present:
         - `plan.md`, `tasks.md`
         - `contracts/` directory (incl. `contracts/openapi.yaml`, `contracts/test-case-matrix.md`, `contracts/interface-details/*.md`)
         - `checklists/` directory
         - `ux/`, `ui/`, `prototype/` design artifacts
         - `research.md`, `data-model.md`, `quickstart.md`

6. **Generate/overwrite preview**:
    - Use the HTML template as the structure baseline (preserve the page set, page order, and table intent).
    - The HTML template is a single-file "review website" with hash-based tab pages.
    - **Do not delete pages**. For pages that are out-of-scope for the selected `MODE`, keep them but clearly mark key sections as `N/A (MODE=<mode>)` and explain what artifact/command would populate them.
    - Always add a short note on the Overview page if `EXTRA_NOTES` is provided.
    - Fill each page according to `MODE`:
       - **Overview page**:
          - Iteration snapshot (review status, owners, actors, scope summary, success criteria).
          - Artifact readiness matrix (spec/plan/tasks/data-model/contracts/interface-details/ux/ui/prototype/checklists/research/quickstart).
          - Quick metrics (UC/FR/UDD/task progress placeholders).
          - Process audit overview: Mermaid pipeline DAG + Mermaid timeline/gantt (auto-render when possible; fallback to source-only).
          - Top risks table.
       - **Product page**:
          - JTBD summary: prefer `ux/jtbd.md` excerpt; fallback to `spec.md` excerpt.
          - Scope/goals/non-goals: verbatim excerpt from `spec.md`.
          - Functional breakdown tree (capability -> FR -> scenario/edge).
          - UC index table; FR index table.
          - User flow Mermaid diagram source: prefer `ux/flow.md` or `spec.md`.
          - State machine PlantUML source: prefer `data-model.md` if present.
          - UI element contract table from `spec.md` (map UI -> `Entity.field`).
       - **UX/UI page**:
          - Links/status for `ux/journey.md`, `ux/flow.md`, `ui/ui-spec.md`, `prototype/index.html`.
          - Journey map summary table (verbatim/near-verbatim).
          - Screen inventory / IA / component inventory / state model / microcopy / a11y checklist.
       - **Backend page**:
          - OpenAPI interface inventory table (method/path/operationId/summary/auth/x-fr-ids/status) when available.
          - Data model entity summary table (from `data-model.md`).
          - PlantUML class diagram source from `data-model.md` when available.
          - Per-interface detail docs integration (MANDATORY when available): table + expandable highlights.
       - **Frontend page**:
          - Route/page map Mermaid source; component tree Mermaid source.
          - UI element definitions and mapping to `ui/ui-spec.md` when present.
          - Client state/data fetching strategy table.
       - **Testing page**:
          - AC acceptance checklist (explicit items).
          - Flow cross-reference table (reuse same flow IDs as Product/UX).
          - Test-case matrix summary (from `contracts/test-case-matrix.md` when available).
          - Coverage table (FR <-> operationId <-> CaseID <-> transition).
          - Edge/negative cases table.
       - **Audit page**:
          - NEEDS CLARIFICATION aggregation.
          - Assumptions & Decisions table.
          - Risks & Issues table.
          - Checklist index from `checklists/*.md` when present.
       - **Appendices page**:
          - Appendix A MUST include full `spec.md` verbatim.
          - If present, include full `plan.md`, `tasks.md`, `data-model.md`.
          - If present, include key excerpts from `ux/*`, `ui/ui-spec.md`, and index/excerpts for `interface-details/*.md`.
    - **Tasks-stage interface details integration (MANDATORY when available)**:
       - Read `contracts/interface-details/*.md` and extract per-interface highlights into Backend Review section:
          - call chain/evidence summary,
          - sequence diagram availability,
          - related dependencies,
          - performance notes.
       - If files are missing, mark this section as `N/A (not generated by /speckit.tasks yet)`.
    - Verbatim appendices:
       - Appendix A MUST include full `spec.md` verbatim.
       - If present, include full `plan.md`, `tasks.md`, `data-model.md`.
       - If present, include key excerpts from `ux/*`, `ui/ui-spec.md`, and index/excerpts for `interface-details/*.md`.
