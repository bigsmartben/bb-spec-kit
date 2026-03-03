# {PROJECT_NAME} Constitution

<!--
LLM-OPTIMIZED: This file is an AI-agent consumption format, not a human narrative document.
It combines governance principles + architectural constraints + coding standards as the single baseline in memory/.
Decision priority: constitution.md > spec.md/plan.md/tasks.md > code > personal preference.
-->

## §1 Project Positioning

- Name: `{PROJECT_NAME}`
- Type: `{PROJECT_TYPE}`
  - Backend track: `[Java | Python | Rust | Node.js]` × `[Microservice | Monolith | Serverless]`
  - Frontend track: `[H5 | WeChat Mini Program | Android | iOS | Flutter | React Native]`
  - SOLO mode: frontend + backend in one repository, with the backend/frontend options above
  - TEAM mode: multi-repository collaboration with independent backend/frontend/other role evolution
- Project Mode: `SOLO` | `TEAM`  <!-- Written by /speckit.constitution CREATE or by explicit mode update flow; mode change is a MAJOR semantic version change and MUST be flagged in Sync Impact Report -->
- Core Value: `{CORE_VALUE}`
- Target Users: `{TARGET_USERS}`
- Out of Scope: `{OUT_OF_SCOPE}`

## §2 Engineering Principles

### {PRINCIPLE_1_NAME}

{PRINCIPLE_1_DESCRIPTION}

### {PRINCIPLE_2_NAME}

{PRINCIPLE_2_DESCRIPTION}

### {PRINCIPLE_3_NAME}

{PRINCIPLE_3_DESCRIPTION}

### Core Engineering Constraints (Projects SHOULD include these)

- **Simplicity First**: Use the simplest viable solution; prohibit over-abstraction/over-design/over-optimization; any new abstraction MUST serve ≥3 real use cases
- **Test First**: test specification → test code → implementation → verification; no tests means no merge
- **Contract First**: interface definition → contract tests → implementation → integration; cross-module calls MUST have contract tests
- **Library First**: reusable libraries over tightly coupled applications; core logic SHOULD remain framework-independent
- **Documentation Driven**: WHAT/WHY in spec.md, HOW in plan.md; responsibilities MUST remain separated
- **Quality Order**: maintainability > cleverness, testability > speed, consistency > preference, explicitness > implicitness, visible failure over silent failure

### Dev/Ops Separation ⚠️ Fixed Principle (MUST NOT be removed)

Development (Dev) owns feature implementation and related non-functional targets (e.g., performance and secure coding). Operations (Ops/SRE) owns availability, CI/CD pipelines, SLA achievement, monitoring, alerting, and observability. AI agents generating governance artifacts MUST include this principle as a fixed constitutional constraint.

## §3 Technology Stack

| Category | Selection | Version |
|------|------|------|
| Language | `{LANGUAGE}` | `{VERSION_RANGE}` |
| Runtime | `{RUNTIME}` | `{VERSION_RANGE}` |
| Build | `{BUILD_TOOL}` | `{VERSION_RANGE}` |
| Test | `{TEST_FRAMEWORK}` | `{VERSION_RANGE}` |

Architecture: execution_model=`{EXECUTION_MODEL}` | data_flow=`{DATA_FLOW_PATTERN}` | deployment=`{DEPLOYMENT_MODE}` | persistence=`{PERSISTENCE_STRATEGY}`

Dependencies: source=`{ALLOWED_SOURCES}` | license_allowlist=`{ALLOWED_LICENSES}` | license_blocklist=`{FORBIDDEN_LICENSES}`

Performance: P95≤`{RESPONSE_TIME_THRESHOLD}` | concurrency≥`{CONCURRENT_REQUESTS}` | memory≤`{MEMORY_LIMIT}`

Security: authentication=`{AUTH_MECHANISM}` | authorization=`{AUTHORIZATION_MODEL}` | sensitive_fields=`{SENSITIVE_FIELDS}` | encryption=`{ENCRYPTION_PROTOCOL}`

## §4 Architectural Constraints

### Layering and Dependencies

- Dependency direction: Adapter→Core→Provider→Infrastructure (DAG, reverse/cross-layer dependencies are prohibited)
- Adapter layer: protocol adaptation, DTO/VO transformation, parameter validation
- Core layer: business logic, Entity/BO/DomainService, Repository interface definitions
- Provider layer: Repository implementations, PO/data model, downstream access
- Infrastructure layer: infrastructure configuration only, business logic is prohibited

### Object Boundaries

- DTO/VO only in Adapter | Entity/BO only in Core | PO only in Provider
- Transformation points: Adapter(DTO↔BO) | Provider(BO↔PO)
- Prohibited: direct two-layer jump transformations (DTO→PO), Core depending on Provider implementation classes

### Core Modules

- `{MODULE_1}`: {RESPONSIBILITY}
- `{MODULE_2}`: {RESPONSIBILITY}
- `{MODULE_3}`: {RESPONSIBILITY}

### Coding Standards

- Logging: use unified `{LOGGING_FRAMEWORK}`, structured logs, include `{LOG_CONTEXT_FIELDS}`; direct stdout is prohibited
- Exceptions: `{BUSINESS_EXCEPTION}`→`{SYSTEM_EXCEPTION}` hierarchy; global interception required; swallowing exceptions/exposing internal stack traces is prohibited
- Naming: language=`{NAMING_LANGUAGE}` | file=`{FILE_NAMING_STYLE}` | code=`{CODE_NAMING_STYLE}` | constant=`{CONSTANT_NAMING_STYLE}`

## §5 API Contract

protocol=`{PROTOCOL}` | versioning=`{VERSIONING_STRATEGY}` | compatibility=`{COMPATIBILITY_POLICY}`

response_shape: `{"{SUCCESS_FIELD}":bool, "{ERROR_CODE_FIELD}":str, "{MESSAGE_FIELD}":str, "{DATA_FIELD}":obj}`

error_codes: `{ERROR_CODE_SUCCESS}`=200 | `{ERROR_CODE_BAD_REQUEST}`=400 | `{ERROR_CODE_UNAUTHORIZED}`=401 | `{ERROR_CODE_FORBIDDEN}`=403 | `{ERROR_CODE_NOT_FOUND}`=404 | `{ERROR_CODE_INTERNAL_ERROR}`=500

## §6 Testing Standards

- Flow: test specification → test code → implementation → automated verification; failed checks MUST block next stage
- Coverage: unit≥`{UNIT_TEST_COVERAGE}`% | integration≥`{INTEGRATION_TEST_COVERAGE}`% | contract=100% | E2E=critical path 100%
- Prohibited: no-test delivery, excessive mocking, external-environment dependency, flaky tests (time/random/order dependent)

## §7 Domain Language

| Term | Definition |
|------|------|
| `{TERM_1}` | `{DEFINITION_1}` |
| `{TERM_2}` | `{DEFINITION_2}` |

Rules: code/docs/comments MUST use unified terminology; synonym drift is prohibited; new terms MUST update this table

## Governance

The constitution has priority over all other practices; changes require documented records, approval, and migration planning.

All PRs/reviews MUST verify constitutional compliance; complexity MUST have explicit justification; follow [GUIDANCE_FILE] for runtime development guidance.

**Version**: {CONSTITUTION_VERSION} | **Ratified**: {RATIFICATION_DATE} | **Last Amended**: {LAST_AMENDED_DATE}
