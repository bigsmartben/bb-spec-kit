---
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Start the implementation in phases
    send: true
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## Execution Contract (SSOT)

**Inputs**: Feature spec, plan, data model, contracts  
**Outputs**: tasks.md, interface detail docs, coverage checklist  
**Task Format**: `- [ ] T### [P?] [Type:...] [IFxx?] Description with file path`  
**Task Types**: Research | Interface | Test | Infra | Docs  
**Interface Rules**:  
- Organize by interface delivery units (IF01, IF02, ...)
- Each interface: ≥1 Test + ≥1 Implementation task
- If test-case-matrix exists, reference CaseID explicitly

**Diagram Rules (Canonical)**:
- All diagrams are operation-scoped (no cross-interface duplication)
- Sequence Diagram (Mermaid): MUST include ALL dependencies from Section 2 dependency inventory
- Sequence Diagram (Mermaid): MUST be class-level for in-repo interactions (no generic `API` participant)
- Sequence Diagram (Mermaid): MUST cover all internal class participants in the operation path and show key call/message directions between them
- Sequence Diagram (Mermaid): each in-repo participant/call MUST be traceable to Section 2 evidence (`[path:line] :: [symbol]`)
- Sequence Diagram (Mermaid): if dependency timeout/retry/failure-degradation behavior exists, include at least one critical non-happy path
- UML Class Diagram (Mermaid): MUST reflect Section 2 evidence chain with concrete class names and relationships; module-only placeholders are not allowed; external systems are not modeled as internal classes
- Both diagrams MUST be consistent with Evidence & Call Chain + Dependency Inventory

**DAG Rules (Canonical)**:  
- Adjacency List is PRIMARY (machine-parseable SSOT)
- Mermaid Task DAG OPTIONAL (human visualization)
- Every `[P]` task has zero blocking edges per DAG
- Every edge cites valid TaskID present in checklist

**Severity Policy**:  
- Missing AEI-### citation for Existing boundary: **CRITICAL** (SSOT violation)
- Interface without ≥1 Test task: **CRITICAL** (coverage gap)
- UDD mismatch (spec vs interface detail): **HIGH** (design not ready)
- Scope noise in diagrams (irrelevant classes/steps): **MEDIUM** (clarity issue)

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

## Outline

1. **Setup**: Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**:
     - plan.md (tech stack, libraries, structure)
     - spec.md (user stories with priorities + UDD items via `Entity.field`)
     - data-model.md (incl. Key Path UDD→VO coverage table + VO→Persistence mapping)
     - contracts/ (interface contracts; MUST exist and be non-empty)
   - **Optional**: research.md (decisions), quickstart.md (test scenarios)
   - If any required document is missing: **ERROR** and STOP. Instruct the user to run `/speckit.plan` first.

3. **Execute task generation workflow**:
   - Load plan.md and extract tech stack, libraries, project structure
   - Load spec.md and extract user stories with their priorities (P1, P2, P3, etc.)
   - Load data-model.md:
     - Extract entities (if present) and map to interfaces and user stories
     - Extract Key Path UDD→VO coverage table (Key Path + System-backed UDD Items)
     - Extract VO→Persistence mapping (minimum viable)
   - If `contracts/test-case-matrix.md` exists:
     - Treat it as the source of truth for interface-level verification coverage (it is design, not executable code)
     - Use its `CaseID` rows to generate concrete `Type:Test` tasks (see rules below)
   - Build an **Interface Inventory** (primary delivery units):
     - If `contracts/openapi.yaml` exists:
       - Treat each OpenAPI operation (`operationId`) as an interface delivery unit
       - Sort operations lexicographically by `operationId`
       - Assign sequential Interface IDs: IF01, IF02, ...
       - Generate (or update) per-operation interface detail docs under:
         - `contracts/interface-details/<operationId>.md`
       - Use the interface detail template as the structure baseline (preserve headings; fill/replace placeholders; keep it operation-scoped):
           - Preferred: `.specify/templates/interface-detail-template.md`
           - Fallback: `templates/interface-detail-template.md`
       - Each interface detail doc MUST follow template: `Section 1: Reference | 2: Evidence Baseline & Dependencies | 3: Interface Detailed Design (3.1-3.5) | 4: Performance`
       - Section 1 MUST include concrete OpenAPI linkage fields for this operation (`operationId`, `method`, `path`, and `OpenAPI operation ref`)
       - Diagram rules (Canonical SSOT in Execution Contract):
         - Sequence & UML class diagrams (`Section 3.2` and `Section 3.3`) MUST be Mermaid and MUST be consistent with Section 2 (Evidence + Inventory)
         - Sequence diagram MUST be class-level for in-repo interactions (no generic `API` participant)
         - Sequence diagram MUST cover all internal class participants in the operation path and show key call/message directions between them
         - Sequence diagram MUST include at least one critical non-happy path when dependency timeout/retry/failure-degradation behavior exists
         - UML class diagram MUST use concrete class names and explicit class relationships; module-only placeholders are not allowed
         - External dependencies NOT modeled as internal classes; see Section 2.3 for ownership/protocol/timeout/retry
       - Evidence requirement: Any `Existing` boundary step MUST cite `AEI-###` (per constitution SSOT); do NOT duplicate repo boundary index
       - Map each interface to the user stories it serves (from spec.md)
     - Else if contracts/ exists and contains one or more `*.md` contract docs:
       - Sort contract doc paths lexicographically
       - Assign sequential Interface IDs: IF01, IF02, ...
       - Map each interface to the user stories it serves (from spec.md)
   - If research.md exists: Extract decisions for setup tasks
   - Generate tasks organized by **interfaces** (see Task Generation Rules below)
   - Enforce coverage gates:
     - If `contracts/openapi.yaml` exists: Every OpenAPI `operationId` MUST appear in Interface Inventory
     - Else if using `contracts/*.md`: Every contract doc MUST appear in Interface Inventory
     - Every interface MUST have:
       - at least one implementation task: `[Type:Interface] [IFxx]`
       - at least one test/verification task: `[Type:Test] [IFxx]`
     - If `contracts/test-case-matrix.md` exists:
       - Every interface MUST have at least one `Type:Test` task that explicitly references the concrete `CaseID` set it covers
       - Each such test task MUST list required mocks/fixtures extracted from those `CaseID` rows
   - Generate a DAG (Adjacency List as SSOT; optional Mermaid visualization):
     - Interface-level dependencies (IFxx -> IFyy)
     - Task-level dependencies (T### -> T###)
   - Mark `[P]` tasks consistently with DAG (see Execution Contract: DAG Rules)
   - Validate completeness: each interface independently deliverable & verifiable

4. **Generate tasks.md**: Use the tasks template as structure (preferred: `.specify/templates/tasks-template.md`; fallback: `templates/tasks-template.md`), fill with:
   - Correct feature name from plan.md
   - Task Types section (required)
   - Interface Inventory section (required)
   - Phase 0 (Optional): Research spikes (only if there are explicit unknowns/decisions to investigate)
   - Phase 1: Setup tasks (project initialization)
   - Phase 2: Foundations (blocking prerequisites for all interfaces)
   - Phase 3+: One interface section per InterfaceID (in delivery order)
     - Each interface section MUST include:
       - goal
       - contract reference (OpenAPI `operationId` + file path, or contract doc path; if any)
       - served user stories (traceability)
       - definition of done
       - tasks: tests/verification (`Type:Test`) and implementation (`Type:Interface`)
   - Final Phase: Polish & cross-cutting concerns
   - All tasks MUST follow the strict checklist format (see Task Generation Rules below)
   - Every task MUST include concrete file paths (or explicit N/A only for tasks that do not modify repository files)
   - DAG section:
     - Task DAG (Adjacency List) — PRIMARY SSOT for machine parsing
     - Interface DAG (Mermaid) — OPTIONAL human visualization

   - Also generate a coverage checklist (soft gate for implementation):
     - Create/overwrite `FEATURE_DIR/checklists/udd-vo-coverage.md`
     - Checklist items MUST validate the *design/traceability artifacts*, not code execution:
       - Key Path (P1) UCs: all referenced `→ ref: Entity.field` are defined as UDD Items (no dangling refs)
       - Key Path + System-backed UDD Items: each has at least one VO mapping (from the plan’s UDD→VO coverage table)
       - UI-local UDD Items: derivation rules are explicitly defined and not mis-modeled as interface-returned data

5. **Report**: Output path to generated tasks.md and summary:
   - Total task count
   - Task count per interface
   - Parallel opportunities identified
   - Verification criteria for each interface
   - Suggested MVP scope (typically Interface IF01 only)
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, type label, optional interface label, file paths)
   - Matrix status:
     - If `contracts/test-case-matrix.md` exists: confirm `CaseID`-referenced test-task generation
     - If missing: explicitly flag fallback mode (quickstart/spec-derived verification tasks) and note that matrix-driven CaseID coverage is unavailable
   - Recommend running `/speckit.preview` to generate/update reviewer-facing `preview.html` including interface detail docs context.

Context for task generation: {ARGS}

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by interface delivery units so each interface can be delivered and verified independently.

**Automated tests are OPTIONAL**: Only generate automated test tasks if explicitly requested in the feature specification or if the user requests a TDD approach.

**Verification is REQUIRED**: Every interface MUST have at least one `Type:Test` task. If automated tests are not requested/available, the `Type:Test` task can be scripted verification (e.g., quickstart.md smoke validation).

### Checklist Format (REQUIRED)

`- [ ] T### [P?] [Type:<Research|Interface|Test|Infra|Docs>] [IFxx?] Description with file path`

- **Checkbox** (`- [ ]`): ALWAYS start
- **Task ID** (T###): Sequential, execution order
- **[P]**: Mark if parallelizable (zero blocking edges per DAG, no shared-file conflict)
- **[Type:...]**: REQUIRED; one of Research|Interface|Test|Infra|Docs
- **[IFxx]**: REQUIRED for Type:Interface & Type:Test; OPTIONAL otherwise
- **Description**: Exact file path (or explicit `N/A` only if no file edits)

**Examples**: ✅ `- [ ] T001 [Type:Infra] Create structure in src/` | ✅ `- [ ] T010 [P] [Type:Test] [IF01] Add test in tests/contract/test_login.py` | ❌ `- [ ] Create model` (missing ID)

### Task Organization

1. **From OpenAPI (contracts/openapi.yaml)** - PRIMARY ORGANIZATION WHEN PRESENT:
   - Each OpenAPI operation (`operationId`) becomes an interface delivery unit (IF01, IF02, ...)
   - For each operationId:
     - Generate (or update) `contracts/interface-details/<operationId>.md` before generating tasks
     - Ensure each generated interface detail doc is operation-scoped and contains a complete Related Applications & Dependency Inventory for that operation only
     - If `contracts/test-case-matrix.md` exists:
       - Select the test cases whose `operationId` matches this interface’s `operationId`
       - Emit at least one `Type:Test` task for this interface that:
         - Lists the covered `CaseID`s explicitly in the task description
         - Names the intended test artifact path(s) (stack-appropriate). If unknown, write `NEEDS CLARIFICATION` and add a `Type:Research` task to determine the test framework + path conventions.
         - Lists required mocks/fixtures extracted from those `CaseID` rows (optionally cross-check with `contracts/interface-details/<operationId>.md` sequence diagram / call chain)
       - If no test framework is established or automated tests are not appropriate, generate a `manual-script` verification task that updates `specs/<feature>/quickstart.md` with runnable commands and references the `CaseID`s it covers.
     - Else (no test-case matrix):
       - Include at least one verification task (`Type:Test` [IFxx]) and at least one implementation task (`Type:Interface` [IFxx])
   - Map each interface → served user stories from spec.md (traceability table)

2. **From Contracts (contracts/*.md)** - PRIMARY ORGANIZATION WHEN OPENAPI IS ABSENT:
   - Each contract doc becomes an interface delivery unit (IF01, IF02, ...)
   - For each interface (IFxx), include:
     - Tests/verification tasks (`Type:Test` [IFxx]) before or alongside implementation
     - Implementation tasks (`Type:Interface` [IFxx]) with concrete file paths
   - Map each interface → served user stories from spec.md (traceability table)

3. **From Data Model (data-model.md)**:
   - Map each entity to the interface(s) that require it
   - If an entity is shared by multiple interfaces: put it in Foundations or the earliest dependent interface

4. **From Setup/Infrastructure**:
   - Shared infrastructure -> Setup (Phase 1) or Foundations (Phase 2)
   - Interface-specific infrastructure -> within that interface section (Phase 3+)

### Phase Structure

- **Phase 0 (Optional)**: Research spikes (only when explicit unknowns/decisions exist)
- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundations (blocking prerequisites - MUST complete before interfaces)
- **Phase 3+**: Interfaces (delivery units) in delivery order
  - Within each interface: Tests/Verification -> Implementation -> Integration
  - Each interface should be independently deliverable and verifiable
- **Final Phase**: Polish & Cross-Cutting Concerns

### DAG Requirements (REQUIRED)

The generated tasks.md MUST include:

1. **Interface DAG (Mermaid)**: Dependencies between interfaces (IFxx)
2. **Task DAG (Mermaid)**: Dependencies between tasks (T###)
3. **Task DAG (Adjacency List)**: One edge per line:

```text
T010 -> T012  # reason
T012 -> T014  # reason
```

**Consistency checks**:
- Every edge references valid TaskIDs present in the checklist.
- Every `[P]` task MUST have no incoming edges from unfinished tasks that would serialize it.
