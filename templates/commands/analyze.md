---
description: Perform cross-artifact consistency analysis across spec.md, plan.md, and tasks.md. Use after task generation to identify gaps, duplications, and inconsistencies before implementation.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --mode analyze --input "{ARGS}" --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -Mode analyze -InputFile "{ARGS}" -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Usage / Input File *(MANDATORY)*

This command requires an explicit **input file** as the first token in `$ARGUMENTS`:

- `/sdd.analyze <plan.md|tasks.md> [notes...]`
- `<plan.md|tasks.md>` can be an absolute path or a repo-root relative path under `specs/<feature>/`.

Examples:

- `/sdd.analyze specs/001-foo/tasks.md`
- `/sdd.analyze /abs/path/to/specs/001-foo/plan.md 请重点检查术语一致性`

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

Identify inconsistencies, duplications, ambiguities, and underspecified items across the feature’s generated artifacts before implementation.

This command is the **single post-hoc audit / verification entry point** for cross-artifact reasoning quality and constraint compliance.

Important: This audit does **not** replace the minimal generation-time hard gates in `/sdd.plan`, `/sdd.tasks`, or `/sdd.implement`. Those gates exist to fail fast; this command exists to catch drift, gaps, and mismatches before code is written.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

**Constitution Authority**: The project constitution is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks—not dilution, reinterpretation, or silent ignoring of the principle. If a principle itself needs to change, that must occur in a separate, explicit constitution update outside `/sdd.analyze`.

Constitution path (terminology authority):
- Preferred: `.specify/memory/constitution.md`
- Fallback: `memory/constitution.md`

## Execution Steps

### 1. Initialize Analysis Context

Run `{SCRIPT}` once from repo root and parse JSON for FEATURE_DIR and AVAILABLE_DOCS from explicit input-file-derived context. Derive absolute paths:

- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md
- CONTRACTS_DIR = FEATURE_DIR/contracts/
- INTERFACE_DETAILS_DIR = FEATURE_DIR/contracts/interface-details/ (if present)
- OPENAPI = FEATURE_DIR/contracts/openapi.yaml (if present)
- TEST_CASE_MATRIX = FEATURE_DIR/contracts/test-case-matrix.md (if present)

Abort with an error message if any required file is missing (instruct the user to run missing prerequisite command).
For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From spec.md:**

- Overview/Context
- Functional Requirements
- Non-Functional Requirements
- User Stories
- Edge Cases (if present)

**From plan.md:**

- Architecture/stack choices
- Data Model references
- Phases
- Technical constraints

**From tasks.md:**

- Task IDs
- Descriptions
- Phase grouping
- Parallel markers [P]
- Referenced file paths
- Interface Inventory (InterfaceID ↔ `operationId`/contract reference)
- Any explicit `CaseID` references in `Type:Test` tasks (if present)

**From constitution:**

- Load the constitution for principle validation and terminology checks:
  - Preferred: `.specify/memory/constitution.md`
  - Fallback: `memory/constitution.md`

**From design artifacts (if present):**

- `data-model.md`: UDD items, Key Path coverage tables, VO→Persistence mapping (if the plan produces them)
- `contracts/`: OpenAPI/contract schemas (Interface VO) to validate UDD→VO coverage claims
- `contracts/test-case-matrix.md` (if present): verification design + traceability; treat as read-only source-of-truth for CaseIDs
- `contracts/interface-details/*.md` (if present): per-interface detailed design packets; treat as read-only source-of-truth for operation-scoped evidence chains and dependency inventory

### 3. Build Semantic Models

Create internal representations (do not include raw artifacts in output):

- **Requirements inventory**: Each functional + non-functional requirement with a stable key (derive slug based on imperative phrase; e.g., "User can upload file" → `user-can-upload-file`)
- **FR/UC inventories** (when IDs exist): Extract `FR-###` and `UC-###` identifiers and their short titles/phrases
- **User story/action inventory**: Discrete user actions with acceptance criteria
- **Task coverage mapping**: Map each task to one or more requirements or stories (inference by keyword / explicit reference patterns like IDs or key phrases)
- **Constitution rule set**: Extract principle names and MUST/SHOULD normative statements
- **Interface inventory**: Parse Interface Inventory from tasks.md (InterfaceID → `operationId` or contract doc path)
- **Interface detail model** (if present): Parse each relevant `contracts/interface-details/<operationId>.md` into:
  - UDD Coverage list: `UDD Item (Entity.field)` → `VO field path`
  - Evidence & Call Chain steps: `file:symbol` + `Existing|Planned/New code` (+ any cited `AEI-###`)
  - Dependency inventory (names + ownership + direction + protocol + timeout/retry + failure mode)
- **Test matrix model** (if present): Parse `CaseID` rows (CaseID → operationId → FR/UC refs → tags/priority/test level → fixtures/mocks → expected status/error)

### 4. Detection Passes (Token-Efficient Analysis)

Focus on high-signal findings. Limit to 50 findings total; aggregate remainder in overflow summary.

#### A. Duplication Detection

- Identify near-duplicate requirements
- Mark lower-quality phrasing for consolidation

#### B. Ambiguity Detection

- Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria
- Flag unresolved placeholders (TODO, TKTK, ???, `<placeholder>`, etc.)

#### C. Underspecification

- Requirements with verbs but missing object or measurable outcome
- User stories missing acceptance criteria alignment
- Tasks referencing files or components not defined in spec/plan

#### D. Constitution Alignment

- Any requirement or plan element conflicting with a MUST principle
- Missing mandated sections or quality gates from constitution

#### E. Coverage Gaps

- Requirements with zero associated tasks
- Tasks with no mapped requirement/story
- Non-functional requirements not reflected in tasks (e.g., performance, security)

#### F. Inconsistency

- Terminology drift (same concept named differently across files)
- Data entities referenced in plan but absent in spec (or vice versa)
- UDD/VO layering drift:
  - Spec references `Entity.field` (UDD Items) that have no downstream VO mapping evidence for Key Path + System-backed scope
  - Plan/contracts define user-visible fields without corresponding UDD item definitions (missing UDD single source of truth)
- Task ordering contradictions (e.g., integration tasks before foundational setup tasks without dependency note)
- Conflicting requirements (e.g., one requires Next.js while other specifies Vue)

#### G. OpenAPI Field Alignment *(if OpenAPI exists)*

OpenAPI defines the system's data contract. This section ensures requirements and contracts stay synchronized with API specifications.

1. **Schema field presence**
   - Track schema.properties in OpenAPI
   - Verify every request/response field in spec requirements has a corresponding schema.property definition
   - Flag additions to OpenAPI without spec acknowledgment as design drift
   - Flag spec requirements referencing fields not in any OpenAPI schema as underspecification

2. **Parameter alignment**
   - Parameters in spec contract (path/query/header) MUST exist in OpenAPI
   - Validate dataType and validation constraints match between spec and OpenAPI

3. **Edge case coverage**
   - For each schema field, check that nullable/minLength/pattern constraints are explicit in OpenAPI
   - Flag missing or implicit constraints that contradicts spec requirements

#### H. Test Case Matrix Alignment *(if `contracts/test-case-matrix.md` exists)*

Treat the matrix as a design + traceability artifact. This section is a **consistency check** only (no file writes).

Perform these checks and emit findings with precise locations:

1. **CaseID integrity**
   - Uniqueness: no duplicate `CaseID`
   - Format: `TC-<operationId>-###`
   - `operationId` referenced by CaseID matches the row’s `operationId` field (if both exist)

2. **OpenAPI alignment (when `contracts/openapi.yaml` exists)**
   - Every `operationId` present in matrix MUST exist in OpenAPI
   - Every in-scope OpenAPI `operationId` SHOULD have ≥1 CaseID row
   - If matrix is present, flag any OpenAPI `operationId` with **zero** cases as **HIGH** (verification gap)

3. **FR/UC traceability**
   - Every in-scope `FR-###` from spec SHOULD appear in ≥1 CaseID row
   - Any `FR-###` referenced in matrix MUST exist in spec (no dangling FRs)
   - If UC-structured: UC → FR → CaseIDs should be non-empty for Key Path/P1 UCs

4. **Happy path + negative-path sanity (quality heuristic; do not over-police)**
   - For each in-scope `operationId`, matrix SHOULD include:
     - ≥1 `happy-path` case (or equivalent explicit marker; if tags are absent, infer by scenario wording)
     - ≥1 negative case (validation/authz/not-found/conflict/etc.)
   - If an operation lacks both, report **MEDIUM** with a concrete recommendation

5. **Status-code coverage (best-effort)**
   - If OpenAPI response codes are easy to extract for an operation:
     - Ensure cases cover at least 1 representative 2xx and key 4xx/5xx that are meaningful for the feature
   - If unable to infer, report as **LOW** with "needs clearer matrix/OpenAPI structure" note (do not hallucinate)

6. **Tasks ↔ Matrix consistency (post-/sdd.tasks validation)**
   - Extract all `CaseID` tokens mentioned in `tasks.md` `Type:Test` tasks
   - Every referenced `CaseID` MUST exist in `contracts/test-case-matrix.md`
   - For interface-tagged tasks `[IFxx]`:
     - If Interface Inventory maps `IFxx` to an `operationId`, verify referenced CaseIDs are for that same `operationId`
   - If any referenced CaseID is missing/mismatched: report **CRITICAL** (implementation will ERROR later)

#### I. Interface Detail Docs Alignment *(if `contracts/interface-details/` exists or is expected)*

Treat interface detail docs as operation-scoped design packets (not implementation). This section verifies that `data-model.md` and `interface-details/<operationId>.md` are aligned and that evidence chains are relevant and properly cited.

Perform these checks and emit findings with precise locations:

1. **Presence / completeness (when OpenAPI is present)**
   - If `contracts/openapi.yaml` exists, then `contracts/interface-details/<operationId>.md` MUST exist for each in-scope `operationId`.
   - If any are missing: report **CRITICAL** (implementation will later ERROR and stop).

2. **UDD Coverage ↔ data-model consistency**
   - Extract the Key Path UDD→VO coverage table from `data-model.md` (Key Path + System-backed scope).
   - For each `operationId`:
     - Every Key Path + System-backed `UDD Item (Entity.field)` mapped to this `operationId` in `data-model.md` MUST appear in the interface detail doc’s UDD Coverage section (with the same `VO field path`).
     - Any UDD Item listed in interface detail docs MUST exist in the Spec UDD (no dangling `Entity.field` references).
   - Missing Key Path coverage: **HIGH** (or **CRITICAL** if it blocks a P1 UC’s observable output/input).
   - VO path mismatch (same UDD Item, different `VO field path`): **HIGH** (semantic drift risk).

3. **VO→Persistence mapping relevance**
   - For each `VO field path` referenced by an interface detail doc’s UDD Coverage:
     - It SHOULD have a corresponding row in `data-model.md` VO→Persistence mapping.
     - If missing for Key Path + System-backed scope: **HIGH** (design not implementation-ready).

4. **Evidence chain relevance and SSOT citations**
   - Evidence in interface detail docs MUST be operation-scoped:
     - If a call chain step is not relevant to the operation’s request/response behavior or persistence mapping, flag as **MEDIUM** (noise / weak relevance).
   - If the constitution includes an Architecture Evidence Index with `AEI-###` IDs:
     - Any evidence-chain step labeled `Existing` in interface detail docs MUST cite the corresponding `AEI-###` boundary/entrypoint it relies on.
     - Missing `AEI-###` citations for `Existing` boundary/entrypoint steps: **CRITICAL** (constitution/SSOT violation).

5. **Class diagram context consistency (PlantUML)**
   - For each `contracts/interface-details/<operationId>.md`:
     - Section 6 (Relevant Code Class Diagram) MUST be present and non-empty (not placeholder-only).
     - Class diagram scope MUST be operation-scoped:
       - Include only in-repo code classes/modules directly involved in this operation.
       - If classes/components in the diagram have no corresponding relevance in Section 3 call chain, flag as **MEDIUM** (scope noise).
     - External systems MUST NOT be modeled as internal code classes in Section 6:
       - If external dependencies (2nd/3rd-party, middleware, queues, caches, remote systems) are modeled as internal classes, flag as **HIGH** and recommend moving representation to Section 5 sequence diagram + Section 4 dependency inventory.
     - Structural alignment checks:
       - Any gateway/adapter/repository class shown in Section 6 SHOULD be reflected in either Section 3 evidence call chain or Section 4 dependency inventory context.
       - Missing corresponding context evidence for key boundary classes: **HIGH** (traceability gap).

### 5. Severity Assignment

Use this heuristic to prioritize findings:

- **CRITICAL**: Violates constitution MUST, missing core spec artifact, or requirement with zero coverage that blocks baseline functionality
- **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Style/wording improvements, minor redundancy not affecting execution order

### 6. Produce Compact Analysis Report

Output a Markdown report (no file writes) with the following structure:

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |

(Add one row per finding; generate stable IDs prefixed by category initial.)

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**Constitution Alignment Issues:** (if any)

**Unmapped Tasks:** (if any)

**Interface Detail Docs Alignment Issues:** (if any; when `contracts/interface-details/` is present or expected)

**Class Diagram Context Consistency Issues:** (if any; when `contracts/interface-details/` is present or expected)

**Metrics:**

- Total Requirements
- Total Tasks
- Coverage % (requirements with >=1 task)
- Ambiguity Count
- Duplication Count
- Critical Issues Count
- If `contracts/interface-details/` exists or is expected:
  - Total interface detail docs checked
  - Missing interface detail docs (count; list operationIds)
  - UDD Coverage mismatches (count)
  - Missing VO→Persistence rows for referenced `VO field path` (count)
  - Missing/empty class diagrams in Section 6 (count)
  - Class-diagram context mismatches (count)
- If `contracts/test-case-matrix.md` exists:
  - Total CaseIDs
  - CaseIDs per `operationId` (top 5 by count; and list any 0-count OpenAPI ops when applicable)
  - `% operationId with happy-path coverage` (best-effort; explicit tag preferred)

### 7. Provide Next Actions

At end of report, output a concise Next Actions block:

- If CRITICAL issues exist: Recommend resolving before `/sdd.implement`
- If only LOW/MEDIUM: User may proceed, but provide improvement suggestions
- Provide explicit command suggestions: e.g., "Run /sdd.specify with refinement", "Run /sdd.plan to adjust architecture", "Manually edit tasks.md to add coverage for 'performance-metrics'"

### 8. Offer Remediation

Ask the user: "Would you like me to suggest concrete remediation edits for the top N issues?" (Do NOT apply them automatically.)

## Operating Principles

### Context Efficiency

- **Minimal high-signal tokens**: Focus on actionable findings, not exhaustive documentation
- **Progressive disclosure**: Load artifacts incrementally; don't dump all content into analysis
- **Token-efficient output**: Limit findings table to 50 rows; summarize overflow
- **Deterministic results**: Rerunning without changes should produce consistent IDs and counts

### Analysis Guidelines

- **NEVER modify files** (this is read-only analysis)
- **NEVER hallucinate missing sections** (if absent, report them accurately)
- **Prioritize constitution violations** (these are always CRITICAL)
- **Use examples over exhaustive rules** (cite specific instances, not generic patterns)
- **Report zero issues gracefully** (emit success report with coverage statistics)

## Context

{ARGS}
