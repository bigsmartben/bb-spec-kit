# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### [PRINCIPLE_1_NAME]
<!-- Example: I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### [PRINCIPLE_2_NAME]
<!-- Example: II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### [PRINCIPLE_3_NAME]
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### [PRINCIPLE_4_NAME]
<!-- Example: IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### [PRINCIPLE_5_NAME]
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

## Terminology & Layering

This section defines non-negotiable terminology and layering rules to prevent semantic drift across phases.

### Terms

- **UDD (UI Data Dictionary)**: The single source of truth for *user-visible information* definitions (meaning, calculation/criteria, boundaries, display rules). UDD is **not** a database schema.
- **UDD Item**: A UDD field item. Reference format uses `Entity.field` as the stable UDD Item ID.
- **System-backed UDD Item**: A user-visible information item whose value is provided by, or must be validated/confirmed by, the system via an interface contract (VO). These items MUST be mappable to at least one VO field.
- **UI-local UDD Item**: A user-visible information item that is purely UI-local (e.g., local state, formatting-only derived fields). These items do NOT require a VO source, but MUST declare their derivation rules in the UDD.
- **Interface VO (View Object)**: The outward-facing interface contract schemas in `contracts/` (OpenAPI or other contract formats). VO is **not equal** to UDD and is often a superset: `VO ⊃ UDD` (technical/non-user-visible fields may exist).
- **Persistence Model**: Storage/cache/index structures. Persistence MUST NOT define or override UDD semantics.
- **Domain Entity (Optional)**: Introduce only when needed for complex business rules, state machines, or cross-interface invariants. Domain is not mandatory for every feature.

### Layering Rules (MUST / MUST NOT)

- **Spec phase (user perspective)** MUST define UDD and use it to describe what the user sees. Spec MUST NOT introduce storage schemas, endpoints, or frameworks unless mandated as a hard constraint.
- **Plan phase (architecture perspective)** MUST design Interface VO (contracts) first, then map VO fields to Persistence. Domain is optional.
- **Tasks/Implement phases (development/implementation perspective)** MUST NOT invent new semantics for user-visible fields. If a semantic gap is discovered, it MUST be pushed upstream to Spec/Plan (UDD/VO/mapping), not patched ad-hoc in code.

## Output Language & Stability

This section defines output-language and token-stability requirements for all downstream commands.

- Narrative content for reviewer/stakeholder-facing artifacts SHOULD default to Simplified Chinese (`zh-CN`) unless project governance specifies otherwise.
- Stable IDs/tokens MUST remain unchanged across phases: `UC-###`, `FR-###`, `Entity.field`, `AEI-###`, `operationId`, `CaseID`.
- Normative keywords MUST remain in canonical form when quoted or used as policy terms: `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`.
- Markers used by command workflows MUST NOT be translated or rewritten: `NEEDS CLARIFICATION`, `ERROR`.
- File paths, code identifiers, and CLI commands MUST be preserved verbatim.

### Key Path Gate (coverage enforcement)

- **Key Path** is defined by Spec priority (e.g., `P1` Use Cases / scenarios).
- **Enforcement scope**: Key Path + **System-backed** UDD Items.
- **Coverage assertion**: Every in-scope UDD Item MUST be mapped to at least one VO field in `contracts/` (global union coverage). UI-local items are excluded from this gate.
- Non-Key Path items SHOULD be mapped; missing mappings produce warnings, not blockers.

## Interface Traceability (OpenAPI)

This section applies only when the feature includes a **frontend ↔ backend HTTP API surface** owned by this repository and documented in `contracts/openapi.yaml`.

- **FRID format**: Use `FR-###` exactly as written in the Spec.
- **UC collision prevention**: If the Spec is UC-structured, every traceability table MUST include a `UC ID` column in addition to `FRID`.
- **Stable interface identity**: Use OpenAPI `operationId` as the stable interface identifier (unique across the API surface).
- **FR coverage gate** *(hard gate)*:
  - Every in-scope `FR-###` MUST map to at least one OpenAPI `operationId`.
  - If any in-scope FR is unmapped, the plan MUST be treated as **ERROR** until coverage is complete.
- **OpenAPI traceability fields** *(when OpenAPI is applicable)*:
  - Each operation MUST include `x-fr-ids: [FR-...]` (non-empty).
  - If the Spec is UC-structured, operations SHOULD include `x-uc-ids: [UC-...]`.

## Dependency Matrix
<!-- Third-Party Dependency Matrix (direct and transitive/intermediary dependencies). -->
<!-- Fill as a Markdown table. Include libraries AND intermediary services (SaaS/APIs/queues/caches/etc.). -->
| Component | Type (Direct/Transitive/Intermediary) | Version | License | Source | Owner | Usage | Change Risk | Upgrade Path |
|----------|----------------------------------------|---------|---------|--------|-------|-------|------------|-------------|
[DEPENDENCY_MATRIX]
<!-- Example row: | requests | Direct | 2.32.3 | Apache-2.0 | PyPI | Platform | HTTP client | Medium | Review minors quarterly | -->

## Architecture Evidence Index
<!-- Repo-derived architectural index to support evidence-based planning and design. -->
<!-- Fill as Markdown table rows matching the header below. -->
<!-- Requirements: use concrete file paths + symbols; do NOT invent “Existing” code. -->
<!-- IndexID MUST be stable (do not renumber unless meaning changes). Downstream artifacts reference IndexID as SSOT. -->
| IndexID | Area | Responsibility | Entry Point (file:symbol) | Interfaces (HTTP/CLI/Event/etc.) | Persistence Touchpoints | Status (Existing/Planned/New code) | Notes |
|---------|------|----------------|---------------------------|----------------------------------|-------------------------|------------------------------------|-------|
[ARCHITECTURE_EVIDENCE_INDEX]
<!-- Example row: | AEI-001 | API | HTTP routing + auth | backend/src/api/router.ts:registerRoutes | HTTP (OpenAPI) | db/users (planned) | Existing | TODO(OPENAPI): confirm operationId naming | -->

## [SECTION_2_NAME]
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

[SECTION_2_CONTENT]
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## [SECTION_3_NAME]
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

[SECTION_3_CONTENT]
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Evidence-Based Reasoning
<!-- Applies to plan and implementation phases -->
All reasoning in plan and implementation phases must be grounded in a codebase evidence chain.
Evidence chains should trace from entry points through call paths to concrete dependencies and usage sites.

When an **Architecture Evidence Index** is present:

- The index is the **single source of truth (SSOT)** for repository-level entry points and major boundaries.
- Any downstream artifact (plan, data model, tasks, interface detail docs) that references an `Existing` entry point or boundary MUST cite the corresponding `AEI-###` IndexID instead of restating the boundary definition.
- Do NOT create or maintain a second, duplicated "repo boundary index" outside the constitution.

## Dependency Change Risk
<!-- Applies to downstream plan.research -->
Any change that introduces a new third-party or intermediary dependency in the Dependency Matrix must be treated as a High-Risk item in plan.research.

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
