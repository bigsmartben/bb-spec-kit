---
description: Execute the implementation planning workflow using the plan template to generate design artifacts.
handoffs: 
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.checklist
    prompt: Create a requirements quality checklist for this feature
    send: true
scripts:
  sh: scripts/bash/setup-plan.sh --json
  ps: scripts/powershell/setup-plan.ps1 -Json
agent_scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Output Language & Stability Contract *(MANDATORY)*

Your job is to produce plan/design artifacts that are easy to read for Chinese stakeholders **without** introducing semantic drift or breaking downstream automation.

- **Default output language**: Write all *narrative content* in **Simplified Chinese (zh-CN)**.
- **Do NOT translate / do NOT rewrite** any of the following (keep exact tokens/casing/punctuation):
  - Constitution and template **Terminology / Terms** definitions (authority text)
  - Normative keywords: `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`
  - Markers and gates: `NEEDS CLARIFICATION`, `ERROR`, and any other literal gate tokens in the templates
  - Stable IDs and traceability tokens: `UC-###`, `FR-###`, CaseIDs, `Entity.field`
  - OpenAPI fixed field names and identifiers: `operationId`, `x-fr-ids`, `x-uc-ids`, schema property names
  - Status tokens used for evidence labeling: `Existing`, `Planned/New code`
  - File paths, code identifiers, CLI commands, and anything in code fences/backticks
- **Structure stability**: Preserve section order and headings from the copied `IMPL_PLAN` template (do not rename headings; only fill content).
- **Script-parsed labels (keep in English)**: In `plan.md` keep these exact field labels so agent context scripts can parse them:
  - `**Language/Version**:`
  - `**Primary Dependencies**:`
  - `**Storage**:`
  - `**Project Type**:`

## Constitution Evidence Source Policy (MANDATORY)

- Load constitution policy from:
  - Preferred: `.specify/memory/constitution.md`
  - Fallback: `memory/constitution.md`
- Treat `## Evidence Source Policy (ISS-MCP)` as policy SSOT for repository-fact assertions in this command.
- If both constitution files are missing, use the bootstrap policy in `templates/constitution-template.md` and explicitly label conclusions as degraded governance context.
- For repository fact retrieval, call-chain analysis, architecture-boundary verification, dependency mapping, and impact-scope tracing, follow that policy exactly.

## Outline

1. **Setup**: Run `{SCRIPT}` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**:
   - Read FEATURE_SPEC
   - Read the project constitution (terminology authority):
     - Preferred: `.specify/memory/constitution.md`
     - Fallback: `memory/constitution.md`
   - Apply constitution Terminology & Layering rules (UDD → Interface VO → Persistence; Domain optional; Key Path coverage gate)
   - If the constitution includes an **Architecture Evidence Index** with stable `AEI-###` IDs:
     - Treat it as the **single source of truth** (SSOT) for repository-level entry points and major boundaries.
     - Any time you mention an **Existing** entry point/boundary in plan/design artifacts, you MUST cite the corresponding `AEI-###`.
     - Do NOT duplicate the repo boundary index elsewhere (plan/tasks may include feature-scoped call chains, but they MUST reference `AEI-###` at boundary steps).
   - Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Fill `## Artifacts Overview & Navigation`:
     - Add/verify working relative links to the artifacts under `specs/<feature>/`
     - Keep the inventory as navigation + status only (do NOT redefine artifact dependency order here)
     - As each artifact is generated, update its `Status` to `Generated` (or `N/A` when truly inapplicable)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate design artifacts in strict dependency order:
     - `contracts/openapi.yaml` (OpenAPI 3.0; frontend ↔ backend HTTP API features only; MUST achieve full FR coverage)
     - `data-model.md` (incl. state model (Full FSM when applicable) + class diagrams)
     - `contracts/test-case-matrix.md` (derived from OpenAPI + data model + Spec; frontend ↔ backend HTTP API features only)
     - `contracts/` (other contract formats as appropriate for non-HTTP projects)
     - `quickstart.md`
   - NOTE: Per-operation interface detail docs under `contracts/interface-details/` are generated by `/speckit.tasks` (not `/speckit.plan`) when `contracts/openapi.yaml` is present.
   - Phase 1: Update agent context by running the agent script
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.
  - Recommend running `/speckit.preview` to generate/update reviewer-facing `preview.html`.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task
   - Enumerate all in-scope Functional Requirements (FR-###) from FEATURE_SPEC (and UC IDs if present)
   - Extract UDD (UI Data Dictionary) items from FEATURE_SPEC:
     - Identify Key Path scope (Priority = P1)
     - Classify items as `System-backed` vs `UI-local`
     - Build the Key Path + System-backed UDD Item set for downstream VO coverage gates
   - Determine whether this feature includes a frontend ↔ backend HTTP API surface (i.e., the frontend makes network calls to a backend owned by this repository)
   - Identify stateful entities and all Spec-described states/transitions
   - Discover existing routing/handler/service boundaries in the repo (evidence gathering):
     - Prefer starting from the constitution’s Architecture Evidence Index when present.
     - When recording evidence as `Existing`, cite `AEI-###` for the boundary/entrypoint being referenced.

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

0. **Applicability decision** (MANDATORY):
   - If the feature includes a **frontend ↔ backend HTTP API surface**, you MUST generate the API-centric artifacts below (Steps 1→3).
   - If the feature does **not** include a frontend ↔ backend HTTP API surface, you MUST NOT force OpenAPI/Test Matrix/Interface Detail documents.
     In that case, keep `/contracts/` for whatever contract format is appropriate for the project type (CLI schema, public library API, internal module contracts, etc.).
   - **Compatibility-first (hard rule)**: If the repository already has an existing contract surface (OpenAPI or non-HTTP contracts), you MUST preserve backward compatibility via **additive change only**:
     - Prefer reproducing current interfaces and evolving them via new optional fields, enum extensions, and new operations.
     - MUST NOT delete fields/operations, change types, narrow constraints, or redefine semantics.
     - If a breaking change is unavoidable, record explicit justification and a migration strategy in `plan.md` under `## Complexity Tracking`.

1. **Step 1 — Interface Definition (OpenAPI 3.0)** *(frontend ↔ backend HTTP API features only)*:
   - Create `specs/<feature>/contracts/openapi.yaml` using the OpenAPI 3.0 specification.
   - Use the OpenAPI template as the starting structure baseline (do not remove required fields; expand/replace placeholders):
     - Preferred: `.specify/templates/openapi-template.yaml`
     - Fallback: `templates/openapi-template.yaml`
   - Use `operationId` as the stable interface ID (unique across the API surface).
   - Each operation MUST include:
     - `operationId`
     - `summary` and/or `description`
     - `x-fr-ids: [FR-...]` (non-empty; use `FR-###` exactly as in the Spec)
     - `x-uc-ids: [UC-...]` when the Spec is UC-structured (recommended)
      - Request/response schemas; include fields explicitly indicated by Spec UI elements and acceptance scenarios
   - **FR coverage gate (ERROR if violated)**:
     - Enumerate all in-scope `FR-###` from FEATURE_SPEC (include `UC ID` column if applicable).
     - Verify every FR appears in at least one operation’s `x-fr-ids`.
     - If any FR is unmapped, treat the plan as **ERROR** and revise the API surface until coverage is complete.

2. **Step 2 — Data Model (incl. state model + class diagrams)**:
   - Create `specs/<feature>/data-model.md` based on FEATURE_SPEC + repo evidence.
   - **Minimal-change (hard rule)**: In existing repositories, the data model MUST be repo-convention-first and delta-oriented:
     - Start from existing schemas/types/naming conventions and propose the smallest change set that satisfies Spec/UDD/VO requirements.
     - MUST NOT perform 3NF-driven redesign unless directly required by feature constraints.
   - Include:
     - Entities/classes in scope, with relationships (only fields required by Spec UI/API; do not model every database column)
     - Validation rules derived from requirements
     - **Key Path UDD → VO coverage table (MANDATORY)**:
       - Add a table proving coverage for **Key Path (P1) + System-backed UDD items**:
         - `UDD Item (Entity.field)` | `UC/Scenario (P1)` | `operationId` (or contract id) | `VO field path` | `Notes (UI-local/derived/technical)`
       - ERROR if any Key Path + System-backed UDD item has no VO mapping (UI-local items are excluded from this gate)
     - **VO → Persistence mapping (minimum viable; Domain optional)**:
       - Add a table mapping each VO field to its persistence source (or planned source):
         - `VO field path` | `Persistence source` | `Transform/validation` | `Evidence (file/symbol or Planned/New code)`
     - For each stateful entity: produce a **state model** using the **FSM Gate** (hard rule)
       - Definitions:
         - `N` = number of distinct, user-meaningful lifecycle states (discrete nodes)
         - `T` = number of effective transitions (unique `FromState → ToState` edges)
       - Applicability: a **Full FSM** is applicable iff `N > 4 OR T ≥ 2N`
       - If Full FSM is applicable, include:
         - Exhaustive state enumeration (must cover Spec states)
         - Transition table
         - Transition pseudocode
         - PlantUML state diagram and/or class diagram (use Markdown fences: ```plantuml)
       - If Full FSM is not applicable, include a **Lightweight State Model** instead:
         - state field definition (if any)
         - allowed transitions list (event/guard optional)
         - forbidden transitions list
         - invariants (if any)
         - no PlantUML required
       - Exception policy: Full FSM below the threshold requires explicit justification in `plan.md` under `## Complexity Tracking`
     - A feature-scope class diagram (PlantUML) showing relationships and key fields
     - Evidence mapping table: Entity/Class ↔ repo types (file paths + symbols) or mark as `Planned/New code`

3. **Step 3 — Test Case Matrix** *(frontend ↔ backend HTTP API features only)*:
   - Create `specs/<feature>/contracts/test-case-matrix.md`.
   - Generate it from:
     - `contracts/openapi.yaml` (`operationId` + `x-fr-ids` + schemas)
     - Spec FR descriptions + acceptance scenarios
     - State model from `data-model.md` (Full FSM when applicable; otherwise Lightweight State Model)
   - Primary goal: make verification **implementable without further discovery** while maximizing coverage of:
     - Spec intent (FR/UC + acceptance scenarios)
     - Interface contract (request/response schema + status codes)
     - State machine transitions (valid + key invalid transitions)
   - Recommended document structure (keep it compact and skimmable):
     1) **Scope & Assumptions** (what is in/out; environment; auth model; test data constraints)
     2) **Case Table** (one row per CaseID; grouped by `operationId`)
     3) **Traceability Tables** (FR/UC ↔ cases; transitions ↔ cases)
     4) **Coverage Gates** (explicit pass/fail checklist; mark `N/A` only when truly inapplicable)
   - It MUST include:
     - A stable **CaseID** for every test case row:
       - Format: `TC-<operationId>-###` (e.g., `TC-createUser-001`)
       - Numbering: per `operationId`, ascending by `###` within that `operationId`
       - CaseIDs MUST remain stable unless the underlying behavior meaningfully changes
     - Each test case row MUST include the following fields (as Markdown table columns, or as structured fields within the row text):
       - `CaseID`
       - `operationId`
       - `FR-###` references (and `UC-...` references when applicable)
       - Priority: `P0|P1|P2|P3` (derive from Spec; default to `P1` only when clearly Key Path)
      - Tags (multi): e.g. `happy-path`, `validation`, `authn`, `authz`, `not-found`, `conflict`, `state-transition`, `pagination`, `idempotency`, `concurrency`, `rate-limit` (use only relevant tags)
       - Scenario summary (Given/When/Then or equivalent)
       - Preconditions and required state transition(s)
       - Inputs and expected outputs
       - Expected HTTP status code(s) and error shape (if applicable; reference OpenAPI error schema or define it explicitly)
       - Test level: `unit|integration|e2e|manual-script`
       - Required mocks/fixtures (explicit list)
       - Notes: determinism constraints (time/UUID/random), data setup/cleanup, and any observability assertions (logs/metrics) if required by Spec/NFRs
     - Traceability matrix (MUST be explicit, not implied):
       - FR → operationId(s) → CaseID(s) → (state transition(s) if applicable)
       - If UC-structured: UC → FR → CaseID(s)
    - Coverage gates (ERROR if violated for in-scope items):
       - **FR coverage**: every in-scope `FR-###` appears in ≥1 CaseID row
       - **Operation coverage**: every in-scope `operationId` has at least:
         - 1 `happy-path` case (Key Path/P1 when applicable)
        - 1 negative case derived from Spec acceptance scenarios or contract constraints (typically `validation`; include `authn`/`authz` only when explicitly in scope)
       - **Status-code coverage**: for each operation, include at least one case for each *meaningful* response class that exists in OpenAPI and is in-scope (2xx + key 4xx/5xx); mark rare/unsupported codes as `N/A` with rationale
       - **Schema coverage (Key Path)**: for Key Path + System-backed outputs, ensure cases explicitly assert presence/shape of the required response fields (do not rely on “happy path implies it”)
      - **State-model coverage (when applicable)**:
        - Every designed/allowed transition appears in ≥1 case
        - Include key invalid/forbidden transitions (attempt action in wrong state) as negative cases
     - Design heuristics (use judgement; avoid combinatorial explosion):
       - Prefer boundary-value coverage for numeric limits and string length/patterns
       - Prefer pairwise coverage for multi-parameter filtering/sorting when relevant (`pagination` tag)
       - Prefer idempotency cases for create/mutation operations when idempotency keys/dedup semantics exist (`idempotency` tag)
       - Prefer concurrency cases for state transitions prone to races (e.g., double-submit) (`concurrency` tag)
   - IMPORTANT: The test-case matrix is **not executable code**. It is a test design + traceability artifact that MUST be directly implementable into test scripts (or manual-script verification) without further discovery.

4. **Interface Detail Docs (per operation)** *(frontend ↔ backend HTTP API features only)*:
   - Do NOT generate per-operation interface detail docs during `/speckit.plan`.
   - These docs are generated by `/speckit.tasks` from `contracts/openapi.yaml` and are written to:
     - `specs/<feature>/contracts/interface-details/<operationId>.md`

5. **Agent context update**:
   - Run `{AGENT_SCRIPT}`
   - These scripts detect which AI agent is in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current plan
   - Preserve manual additions between markers

**Output**: `data-model.md`, `contracts/` (and OpenAPI/Test Matrix when applicable), `quickstart.md`, agent-specific file

## Key rules

- Use absolute paths
- Use PlantUML for diagrams in Markdown fences: ```plantuml
- All code-related design MUST include an evidence chain (file paths + symbols) and MUST NOT invent “existing” code paths
- ERROR on OpenAPI FR coverage violations when OpenAPI is applicable
- ERROR on gate failures or unresolved clarifications
