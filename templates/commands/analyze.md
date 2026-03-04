---
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before implementation. This command MUST run only after `/speckit.tasks` has successfully produced a complete `tasks.md`.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

**Constitution Authority**: The project constitution is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks—not dilution, reinterpretation, or silent ignoring of the principle. If a principle itself needs to change, that must occur in a separate, explicit constitution update outside `/speckit.analyze`.

Constitution path (terminology authority):
- Preferred: `.specify/memory/constitution.md`
- Fallback: `memory/constitution.md`

## Execution Steps

### 1. Initialize Analysis Context

Run `{SCRIPT}` once from repo root and parse JSON for FEATURE_DIR and AVAILABLE_DOCS. Derive absolute paths:

- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md
- CONTRACTS_DIR = FEATURE_DIR/contracts/
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

### 3. Build Semantic Models

Create internal representations (do not include raw artifacts in output):

- **Requirements inventory**: Each functional + non-functional requirement with a stable key (derive slug based on imperative phrase; e.g., "User can upload file" → `user-can-upload-file`)
- **FR/UC inventories** (when IDs exist): Extract `FR-###` and `UC-###` identifiers and their short titles/phrases
- **User story/action inventory**: Discrete user actions with acceptance criteria
- **Task coverage mapping**: Map each task to one or more requirements or stories (inference by keyword / explicit reference patterns like IDs or key phrases)
- **Constitution rule set**: Extract principle names and MUST/SHOULD normative statements
- **Interface inventory**: Parse Interface Inventory from tasks.md (InterfaceID → `operationId` or contract doc path)
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

#### G. Test Case Matrix Alignment *(if `contracts/test-case-matrix.md` exists)*

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

6. **Tasks ↔ Matrix consistency (post-/speckit.tasks validation)**
   - Extract all `CaseID` tokens mentioned in `tasks.md` `Type:Test` tasks
   - Every referenced `CaseID` MUST exist in `contracts/test-case-matrix.md`
   - For interface-tagged tasks `[IFxx]`:
     - If Interface Inventory maps `IFxx` to an `operationId`, verify referenced CaseIDs are for that same `operationId`
   - If any referenced CaseID is missing/mismatched: report **CRITICAL** (implementation will ERROR later)

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

**Metrics:**

- Total Requirements
- Total Tasks
- Coverage % (requirements with >=1 task)
- Ambiguity Count
- Duplication Count
- Critical Issues Count
- If `contracts/test-case-matrix.md` exists:
  - Total CaseIDs
  - CaseIDs per `operationId` (top 5 by count; and list any 0-count OpenAPI ops when applicable)
  - `% operationId with happy-path coverage` (best-effort; explicit tag preferred)

### 7. Provide Next Actions

At end of report, output a concise Next Actions block:

- If CRITICAL issues exist: Recommend resolving before `/speckit.implement`
- If only LOW/MEDIUM: User may proceed, but provide improvement suggestions
- Provide explicit command suggestions: e.g., "Run /speckit.specify with refinement", "Run /speckit.plan to adjust architecture", "Manually edit tasks.md to add coverage for 'performance-metrics'"

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
