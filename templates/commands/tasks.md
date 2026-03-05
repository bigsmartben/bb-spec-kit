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

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

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
       - Each interface detail doc MUST include:
         1) Interface Reference Table (method/path/operationId/x-fr-ids/request/response schema refs)
         2) UDD Coverage (Key Path):
            - List the **Key Path + System-backed** UDD Items this interface covers
            - For each UDD Item, provide the corresponding `VO field path` (schema path) as evidence
            - If an interface has no Key Path scope, explicitly note: `Key Path coverage: N/A`
         3) Evidence & Call Chain (call-chain drilldown; file paths + symbols; each step marked `Existing` vs `Planned/New code`)
            - If the project constitution includes an Architecture Evidence Index (SSOT) with stable `AEI-###` IDs:
              - Any step marked `Existing` MUST cite the corresponding `AEI-###` for the boundary/entrypoint it references.
              - Do NOT restate the repo boundary index here; reference `AEI-###` and keep details operation-scoped.
         4) Related Applications & Dependency Inventory (for this operation only): for each dependency record app/system name, ownership (internal/2nd-party/3rd-party), call direction (inbound/outbound), protocol/interface, timeout & retry policy, and failure/degradation mode
         5) Sequence Diagram (PlantUML; MUST include every dependency from the inventory and all remote calls: 2nd-party, 3rd-party, middleware, queues, caches, etc.)
         6) Relevant Code Class Diagram (PlantUML; mandatory; only code relevant to this interface/feature)
            - The class diagram MUST be consistent with the operation call chain and dependency inventory for this interface
            - Include only in-repo code classes/modules directly involved in this operation (controller/service/domain/repository/gateway/adapter as applicable)
            - Do NOT model external systems as internal code classes; represent those in sequence diagram and dependency inventory
         7) Core Algorithm Pseudocode (business-critical logic only)
         8) Change List (resources: DB/config/infra; source code modules/files; API/schema deltas)
         9) Performance Analysis (latency budget, critical path, external call timeouts/retries, caching, concurrency, failure modes, observability)
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
   - Generate a DAG (both Mermaid and adjacency list):
     - Interface-level dependencies (IFxx -> IFyy)
     - Task-level dependencies (T### -> T###)
   - Identify parallel execution opportunities and mark them with `[P]` consistently with the DAG
   - Validate completeness: each interface is independently deliverable and verifiable

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
   - DAG section including:
     - Interface DAG (Mermaid)
     - Task DAG (Mermaid)
     - Task DAG (Adjacency List)

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

Every task MUST strictly follow this format:

```text
- [ ] T### [P?] [Type:<Research|Interface|Test|Infra|Docs>] [IFxx?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order
3. **[P] marker**: Include ONLY if task is parallelizable:
   - No dependencies on incomplete tasks (per DAG)
   - No shared-file conflict (tasks should target different files/areas)
4. **[Type:...] label**: REQUIRED for every task
   - Allowed values: Research, Interface, Test, Infra, Docs
5. **[IFxx] label**:
   - REQUIRED for `Type:Interface` and `Type:Test` tasks
   - OPTIONAL for other types
6. **[USx] label (optional)**:
   - OPTIONAL only
   - Primary user-story traceability MUST be captured in a mapping table, not enforced per task line
7. **Description**: Clear action with exact file path (or explicit N/A only for tasks that do not modify repository files)

**Examples**:

- ✅ CORRECT: `- [ ] T001 [Type:Infra] Create project structure in src/ and tests/ per plan.md`
- ✅ CORRECT: `- [ ] T010 [P] [Type:Test] [IF01] Add contract test in tests/contract/test_login.py`
- ✅ CORRECT: `- [ ] T012 [P] [Type:Interface] [IF01] Implement login handler in src/api/login.py`
- ✅ CORRECT: `- [ ] T014 [Type:Interface] [IF01] Wire route in src/api/routes.py (depends on T012)`
- ❌ WRONG: `- [ ] Create User model` (missing ID and required labels)
- ❌ WRONG: `T001 [US1] Create model` (missing checkbox)
- ❌ WRONG: `- [ ] [Type:Interface] [IF01] Implement login` (missing Task ID)
- ❌ WRONG: `- [ ] T001 [Type:Interface] Implement login` (missing IF label)
- ❌ WRONG: `- [ ] T001 [Type:Interface] [IF01] Implement login` (missing file path or N/A)

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
