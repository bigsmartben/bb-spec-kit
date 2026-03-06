---
description: Generate/overwrite specs/<feature>/preview.html as a reviewer-facing review view (Product/Technical/Test) with interactive navigation and verbatim appendices. This view is not the SSOT and is regenerated on demand.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Constitution Evidence Source Policy (MANDATORY)

- Load constitution policy from:
  - Preferred: `.specify/memory/constitution.md`
  - Fallback: `memory/constitution.md`
- Treat `## Evidence Source Policy (ISS-MCP)` as policy SSOT for repository-fact assertions in this command.
- If both constitution files are missing, use the bootstrap policy in `templates/constitution-template.md` and explicitly label conclusions as degraded governance context.
- For repository fact retrieval, call-chain analysis, architecture-boundary verification, dependency mapping, and impact-scope tracing, follow that policy exactly.

## Usage / Input File *(MANDATORY)*

This command requires an explicit **input file** as the first token in `$ARGUMENTS`:

- `/speckit.preview <input-file> [reviewer-notes...]`
- `<input-file>` can be an absolute path or a repo-root relative path.
- Allowed input basenames are strictly:
  - `spec.md` -> `MODE=spec`
  - `plan.md` -> `MODE=plan`
  - `tasks.md` -> `MODE=tasks`

Examples:

- `/speckit.preview specs/001-foo/spec.md`
- `/speckit.preview specs/001-foo/plan.md 请重点看接口一致性`
- `/speckit.preview /abs/path/to/specs/001-foo/tasks.md`

If `$ARGUMENTS` is empty: **ERROR** and STOP.
- Show usage: `/speckit.preview <spec.md|plan.md|tasks.md> [reviewer-notes...]`

If `$ARGUMENTS` contains additional text after `<input-file>`, treat that remaining text as reviewer notes and incorporate it as a short note in the Overview page (without inventing requirements).

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
- **Input required**: `<input-file>` is mandatory and must be one of `spec.md|plan.md|tasks.md`.
- **Write scope**: Do not modify any other files besides `preview.html`.

## Output Language & Stability Contract *(MANDATORY)*

- **Default output language**: write narrative content in **Simplified Chinese (zh-CN)**.
- Keep stable IDs/tokens unchanged: `UC-###`, `FR-###`, `Entity.field`, `CaseID`, `AEI-###`, `operationId`.
- Keep normative keywords unchanged when quoted: `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`.
- Keep paths/code identifiers/CLI commands exactly as source.

## Structured-to-Human Mapping Contract *(MANDATORY)*

Convert compressed structured language into reviewer-friendly charts/tables/narrative. The preview MUST keep IDs unchanged while adding readable interpretation.

- `UC + FR Index` → Product page: capability tree (`Capability -> FR-### -> Scenario/Edge`) + compact trace index.
- `Given/When/Then` scenarios → Product/Testing pages: actor/system outcome table and scenario checklist rows.
- `Entity.field` (UDD) → Product/Frontend pages: UI/UDD mapping tree + compact validation/display index.
- `OpenAPI (operationId, x-fr-ids)` → Backend/Testing pages: interface inventory + FR coverage matrix.
- `contracts/test-case-matrix.md` (`CaseID`) → Testing page: `FR <-> operationId <-> CaseID <-> transition` coverage table.
- `tasks.md` DAG adjacency list → Overview/Testing pages: Mermaid DAG source + critical-path notes.
- Within the same page/tab, do not duplicate the same semantics in multiple blocks. If a Mermaid diagram and a table convey the same meaning, keep the Mermaid diagram as primary and downgrade table content to a compact index only when necessary.
- For mapping-heavy data (`UC->FR`, `operationId->VO/PO`, `Entity.field->UI`), use Mermaid tree-style structures (`mindmap` or tree-like `flowchart`) as the primary representation. Index-like fields should be rendered as de-emphasized compact notes.

## Compression-Decoding Rules *(MANDATORY)*

- Preserve normative words when quoted, and add human explanation in Chinese:
   - `MUST` → `必须（MUST）`
   - `MUST NOT` → `禁止（MUST NOT）`
   - `SHOULD` → `建议（SHOULD）`
   - `SHOULD NOT` → `不建议（SHOULD NOT）`
   - `MAY` → `可选（MAY）`
- For each referenced ID (`UC-###`, `FR-###`, `CaseID`, `operationId`, `AEI-###`), add a short human-readable label/summary in adjacent column or note (without changing the ID token).
- For `Entity.field`, always split into:
   - Entity
   - Field
   - User-visible meaning
   - Validation/display rule

## Human-Readable Narrative Contract *(MANDATORY)*

For each review page (Overview/Product/UX-UI/Backend/Frontend/Testing/Audit/Appendices), include:

- A short **3-sentence narrative summary** (`业务目标 / 当前成熟度 / 主要风险`).
- A **Review Questions** block with exactly 3 reviewer questions for that page.

For Overview page, additionally include a **Readability Scorecard** with these dimensions (0-100 or High/Medium/Low):

- Completeness
- Traceability
- Testability
- Reviewability

## Diagram Priority & Fallback Contract *(MANDATORY)*

For each diagram-capable section:

1. If valid Mermaid source exists: keep source + render output.
2. If only PlantUML-like content exists in source artifacts, transcode it into Mermaid (semantic-equivalent) and output Mermaid only.
3. If no diagram source but structured index exists: produce Mermaid tree-style representation first; use compact index rows only for lookup metadata.
4. If neither exists: mark `N/A (MODE=<mode>)` + explicit missing artifact path and command to generate it.

Appendices must include a navigation index table before verbatim blocks (artifact, anchor, why reviewer should read).

## Fill Recipes (Deterministic Output) *(MANDATORY)*

To reduce variability, generate key blocks using these deterministic recipes:

1. **3-Sentence Summary recipe (per page)**
    - Sentence 1: `目标（Goal）` — what this page validates.
    - Sentence 2: `成熟度（Maturity）` — Ready / Partial / Missing + evidence path.
    - Sentence 3: `风险（Risk）` — top risk + owner/next action.

2. **Review Questions recipe (exactly 3)**
    - Q1: completeness question.
    - Q2: traceability/consistency question.
    - Q3: risk/testability/operability question.

3. **N/A fallback row recipe**
    - `Status`: `N/A (MODE=<mode>)`
    - `Evidence`: missing artifact path
    - `Next`: command to generate (e.g., `/speckit.plan`, `/speckit.tasks`, `/speckit.design`)

4. **ID explanation recipe**
    - Keep original token in dedicated column (`FR-001`, `operationId`, `CaseID`).
    - Add adjacent column: `Readable Meaning` (one short sentence, no invented behavior).

## Output Completeness Gate *(MANDATORY)*

Before writing `preview.html`, run this hard gate. If any check fails, regenerate the output (do not ship partial HTML):

1. **Template fidelity gate**
   - MUST start from the loaded HTML template file; do not emit a newly invented minimal HTML shell.
   - MUST preserve the template's page skeleton, tab navigation, and section anchors.
2. **Page presence gate**
   - MUST include all pages with stable IDs/anchors: `overview`, `product`, `uxui`, `backend`, `frontend`, `testing`, `audit`, `appendices`.
3. **Per-page payload gate**
   - Every page MUST include:
     - 3-sentence summary
     - exactly 3 review questions
     - at least one evidence table
   - If evidence is unavailable, fill table rows with `N/A (MODE=<mode>)` + `Evidence` + `Next`.
4. **Appendix integrity gate**
   - Appendix navigation index table MUST exist.
   - Appendix A MUST include full `spec.md` verbatim (no truncation).
5. **No-placeholder gate**
   - Final HTML MUST NOT contain unresolved placeholders like `TODO`, `FILL`, `TBD`, `<placeholder>`.

## MODE=spec Enrichment Contract *(MANDATORY)*

When `MODE=spec`, do not degrade most pages to generic N/A. Derive reviewer content from `spec.md` with deterministic extraction:

1. **Overview**
   - Compute quick metrics from `spec.md`: counts for `UC-###`, `FR-###`, `Entity.field`, scenario rows (`Given/When/Then` tables).
   - Fill artifact readiness matrix with explicit statuses for `spec/plan/tasks/data-model/contracts/interface-details/ux/ui/prototype/checklists/research/quickstart`.
2. **Product**
   - Build capability tree `UC -> FR -> scenario/edge` from spec sections.
   - Build UI/UDD mapping tree `UI -> Entity.field -> rule`.
   - Render a compact trace index (`UC-###`, `FR-###`, `Entity.field`) as lookup metadata only (de-emphasized).
3. **UX/UI**
   - Use spec scenarios/flows to generate a derived journey summary table (do not output only N/A if spec has scenarios).
   - If no design artifacts, mark design-file-specific fields as `N/A (MODE=spec)` but keep a spec-derived journey/state summary.
4. **Backend**
   - Build FR contract-readiness table with one row per `FR-###`:
     - `FR ID`, `Readable Meaning`, `operationId` (`N/A (MODE=spec)` when absent), `Next`.
   - If OpenAPI is missing, this page is Partial (not empty).
5. **Frontend**
   - Build UI contract table from all `Entity.field` rows in spec:
     - `Entity`, `Field`, `User-visible meaning`, `Validation/display rule`, `Source`.
   - Include spec-derived route/state map from UC flow/state machine when available.
6. **Testing**
   - Build FR coverage seed table with one row per `FR-###`:
     - `FR ID`, `Scenario refs`, `operationId`, `CaseID`, `Status/Next`.
   - Build edge/negative case table from `Failure / edge behavior` lines in spec.
7. **Audit**
   - Build assumptions/decisions table from in-scope/out-of-scope/constraints.
   - Build risks/issues table from explicitly stated risks and unresolved dependencies.

## Readability Score Rubric *(MANDATORY)*

Score each Overview dimension using one of these forms:

- Numeric form: 0-100
- Tier form: `High` / `Medium` / `Low`

Rubric guidance:

- **Completeness**
   - High / >=80: required artifacts present for current MODE
   - Medium / 50-79: some optional artifacts missing
   - Low / <50: required artifacts missing or sections mostly N/A
- **Traceability**
   - High / >=80: clear links across UC/FR/operationId/CaseID
   - Medium / 50-79: partial mapping or unresolved links
   - Low / <50: broken/missing mapping chain
- **Testability**
   - High / >=80: AC + coverage + edge cases present
   - Medium / 50-79: partial matrix/edge coverage
   - Low / <50: lacks concrete verifiable cases
- **Reviewability**
   - High / >=80: concise summaries + clear risks/questions
   - Medium / 50-79: readable but fragmented
   - Low / <50: mostly raw excerpts without guidance

## Mini Examples *(Reference Output Style)*

Use these mini examples as style references (do not copy blindly; adapt to real evidence):

1. **3-Sentence Summary (Overview) example**
   - 目标：本页用于确认需求、接口与测试链路是否形成可评审闭环。
   - 成熟度：当前为 Partial，`spec.md` 与 `plan.md` 已就绪，`contracts/test-case-matrix.md` 缺失。
   - 风险：测试追踪链未闭环，Owner=QA，下一步执行 `/speckit.plan` 补齐测试矩阵输入。

2. **Review Questions example (Product page)**
   - 范围边界是否已明确区分 in-scope / out-of-scope，并可追溯到 `spec.md`？
   - 每条 `FR-###` 是否有对应场景与可验证结果（Given/When/Then）？
   - 成功指标是否可量化并可由测试用例验证？

3. **N/A fallback row example**
   - Status: `N/A (MODE=spec)`
   - Evidence: `contracts/openapi.yaml` (missing for this mode)
   - Next: run `/speckit.plan` when frontend-backend HTTP API is in scope

4. **ID explanation example**
   - `FR-003` | Readable Meaning: 用户提交后系统必须（MUST）在 2 秒内返回可见反馈。
   - `operationId=createOrder` | Readable Meaning: 创建订单主流程接口，覆盖 `FR-001, FR-003`。
   - `CaseID=TC-API-014` | Readable Meaning: 验证创建订单超时重试与错误提示路径。

## Execution Steps

0. **Parse input file**:
   - Parse `$ARGUMENTS`:
     - `INPUT_FILE` = first token (mandatory).
     - `EXTRA_NOTES` = remaining text after `INPUT_FILE` (may be empty).
   - If `INPUT_FILE` is missing: **ERROR** and STOP.
     - Show usage examples for `spec.md|plan.md|tasks.md`.
   - Determine `MODE` by `basename(INPUT_FILE)`:
     - `spec.md` -> `MODE=spec`
     - `plan.md` -> `MODE=plan`
     - `tasks.md` -> `MODE=tasks`
   - If basename is not one of `spec.md|plan.md|tasks.md`: **ERROR** and STOP.
     - Show allowed basenames and examples.

1. **Resolve paths**:
   - Run `{SCRIPT}` from repo root and parse JSON:
     - `REPO_ROOT`
     - `FEATURE_DIR` (expected: `<repo>/specs/<feature>`)
     - `FEATURE_SPEC`
     - `IMPL_PLAN`
     - `TASKS`
   - Resolve `INPUT_FILE_ABS`:
     - If `INPUT_FILE` is absolute, use as-is.
     - If `INPUT_FILE` is relative and is a bare basename (`spec.md|plan.md|tasks.md`), resolve as `FEATURE_DIR/<basename>`.
     - Otherwise (relative path with directories), resolve from `REPO_ROOT`.

2. **Validate**:
   - Validate in this order:
     1. `INPUT_FILE_ABS` exists and is readable; otherwise **ERROR** and STOP.
     2. `basename(INPUT_FILE_ABS)` is one of `spec.md|plan.md|tasks.md`; otherwise **ERROR** and STOP.
     3. `INPUT_FILE_ABS` must be under `FEATURE_DIR`; otherwise **ERROR** and STOP.
        - Explain that input file must belong to the active feature directory.
     4. Required sibling artifacts by `MODE`:
        - `MODE=spec`: `FEATURE_SPEC` MUST exist; if missing, instruct to run `/speckit.specify`.
        - `MODE=plan`: `FEATURE_SPEC` and `IMPL_PLAN` MUST exist; if plan missing, instruct to run `/speckit.plan`.
        - `MODE=tasks`: `FEATURE_SPEC`, `IMPL_PLAN`, and `TASKS` MUST exist; if plan missing, instruct to run `/speckit.plan`; if tasks missing, instruct to run `/speckit.tasks`.
   - For non-git repos, keep existing guidance about setting `SPECIFY_FEATURE` when path resolution fails.

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
     - `MODE=plan`:
       - Load: `plan.md` from `IMPL_PLAN`.
       - Also load these if present: `data-model.md`, `quickstart.md`, `contracts/openapi.yaml`, `contracts/test-case-matrix.md`.
     - `MODE=tasks`:
       - Load: `tasks.md` from `TASKS`.
       - Also load these if present: `contracts/interface-details/*.md`, `contracts/openapi.yaml`, `contracts/test-case-matrix.md`, `data-model.md`.

6. **Generate/overwrite preview**:
    - Use the HTML template as the structure baseline (preserve the page set, page order, and table intent).
    - The HTML template is a single-file "review website" with hash-based tab pages.
    - Enforce **Output Completeness Gate** and **MODE=spec Enrichment Contract** before final write.
    - **Do not delete pages**. For pages that are out-of-scope for the selected `MODE`, keep them but clearly mark key sections as `N/A (MODE=<mode>)` and explain what artifact/command would populate them.
      - Apply deterministic fill recipes and score rubric above; do not leave summary/question/score sections empty.
      - `MODE=spec` special rule: only fields that require post-spec artifacts (e.g., `operationId`, `CaseID`, interface details) may be `N/A`; UC/FR/UDD/scenario-derived sections MUST be concretely filled from `spec.md`.
    - Always add a short note on the Overview page if `EXTRA_NOTES` is provided.
    - Fill each page according to `MODE`:
       - **Overview page**:
          - Iteration snapshot (review status, owners, actors, scope summary, success criteria).
          - 3-sentence narrative summary + 3 review questions.
          - Readability scorecard (completeness/traceability/testability/reviewability).
          - Artifact readiness matrix (spec/plan/tasks/data-model/contracts/interface-details/ux/ui/prototype/checklists/research/quickstart).
          - Quick metrics (UC/FR/UDD/task progress placeholders).
          - Process audit overview: Mermaid pipeline DAG + Mermaid timeline/gantt (auto-render when possible; fallback to source-only).
          - Top risks table.
       - **Product page**:
          - 3-sentence narrative summary + 3 review questions.
          - JTBD summary: prefer `ux/jtbd.md` excerpt; fallback to `spec.md` excerpt.
          - Scope/goals/non-goals: verbatim excerpt from `spec.md`.
          - Bilingual design terminology glossary (EN term + zh-CN term + short definition + evidence path).
          - Functional breakdown tree (capability -> FR -> scenario/edge) using Mermaid.
          - Requirement trace index should be compact/de-emphasized and must not duplicate full tree semantics.
          - User flow Mermaid diagram source: prefer `ux/flow.md` or `spec.md`.
          - State machine Mermaid source: prefer `data-model.md` if present.
          - UI/UDD mapping as Mermaid tree (`UI -> Entity.field -> rule`) with a compact index for validation/display rules.
       - **UX/UI page**:
          - 3-sentence narrative summary + 3 review questions.
          - Links/status for `ux/journey.md`, `ux/flow.md`, `ui/ui-spec.md`, `prototype/index.html`.
          - Journey map summary table (verbatim/near-verbatim).
          - Screen inventory / IA / component inventory / state model / microcopy / a11y checklist.
       - **Backend page**:
          - 3-sentence narrative summary + 3 review questions.
          - Module 1 (Interface Inventory Mapping): one merged table with `interface(method+path+operationId) / functional capability / Request VO / Response VO / PO mapping / FR refs / status`.
          - Module 2 (Data Model): Mermaid state machine + Mermaid UML class diagram (no PlantUML output).
          - Module 3 (Per-Interface Detailed Design): each interface MUST include:
            - `3.1` mandatory interface field spec:
              - `3.1.1` protocol (`url`, `method`, auth, curl example)
              - `3.1.2` request field specification
              - `3.1.3` response field specification
            - `3.2` Mermaid sequence diagram
            - `3.3` Mermaid UML class diagram
            - `3.4` core algorithm description
            - `3.5` file change list
       - **Frontend page**:
          - 3-sentence narrative summary + 3 review questions.
          - Route/page map Mermaid source; component tree Mermaid source.
          - UI element definitions and mapping to `ui/ui-spec.md` when present.
          - Client state/data fetching strategy table.
       - **Testing page**:
          - 3-sentence narrative summary + 3 review questions.
          - AC acceptance checklist (explicit items).
          - Flow cross-reference table (reuse same flow IDs as Product/UX).
          - Test-case matrix summary (from `contracts/test-case-matrix.md` when available).
          - Coverage table (FR <-> operationId <-> CaseID <-> transition).
          - Edge/negative cases table.
       - **Audit page**:
          - 3-sentence narrative summary + 3 review questions.
          - NEEDS CLARIFICATION aggregation.
          - Assumptions & Decisions table.
          - Risks & Issues table.
          - Checklist index from `checklists/*.md` when present.
       - **Appendices page**:
          - 3-sentence narrative summary + 3 review questions.
          - Appendix navigation index (artifact + anchor + purpose).
          - Appendix A MUST include full `spec.md` verbatim.
          - If present, include full `plan.md`, `tasks.md`, `data-model.md`.
          - If present, include key excerpts from `ux/*`, `ui/ui-spec.md`, and index/excerpts for `interface-details/*.md`.
    - **Tasks-stage interface details integration (MANDATORY when available)**:
       - Read `contracts/interface-details/*.md` and extract per-interface highlights into Backend Review section:
          - protocol summary (`url`, `method`, auth, curl example),
          - request/response field highlights,
          - Mermaid sequence/class diagram availability,
          - core algorithm summary,
          - file change list summary,
          - call chain/dependency/performance notes.
       - If files are missing, mark this section as `N/A (not generated by /speckit.tasks yet)`.
    - Verbatim appendices:
       - Appendix A MUST include full `spec.md` verbatim.
       - If present, include full `plan.md`, `tasks.md`, `data-model.md`.
       - If present, include key excerpts from `ux/*`, `ui/ui-spec.md`, and index/excerpts for `interface-details/*.md`.
