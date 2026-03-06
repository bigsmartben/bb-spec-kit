---
description: "Per-operation interface detailed design template (OpenAPI only)"
---

# Interface Detail: [operationId]

> **Scope**: This document is operation-scoped (one `operationId` only).
> It is design (not implementation) and must be grounded in repo evidence.

## 1. Interface Reference *(mandatory)*

| Field | Value |
| --- | --- |
| operationId | `[operationId]` |
| Method | `[GET|POST|PUT|PATCH|DELETE]` |
| Path | `[/path]` |
| OpenAPI operation ref | `contracts/openapi.yaml#/paths[/path]/[method]` |
| Summary | `[summary]` |
| x-fr-ids | `[FR-###, ...]` |
| x-uc-ids (optional) | `[UC-###, ...]` |
| Auth / Security | `[e.g., bearerAuth / session / N/A]` |
| Request schema | `#/components/schemas/[RequestVO]` (or `N/A`) |
| Success response | `[200|201|204]` → `#/components/schemas/[ResponseVO]` (or `N/A`) |
| Error responses | `[4xx/5xx]` → `#/components/schemas/Error` (or project-specific) |

## 2. UDD Coverage (Key Path) *(mandatory)*

> Include **Key Path + System-backed** UDD items covered by this operation.
> If none: write `Key Path coverage: N/A` and explain why.

| UDD Item (Entity.field) | UC/Scenario (P1) | VO field path | Notes |
| --- | --- | --- | --- |
| `[Entity.field]` | `[UC-### / Scenario]` | `[#/components/schemas/.../properties/...]` | `[UI-local/derived/technical]` |

## 3. Evidence & Call Chain *(mandatory)*

Call-chain drilldown (operation-scoped). Each step marked `Existing` or `Planned/New code`.  
**SSOT Rule**: Any `Existing` boundary step MUST cite `AEI-###` (per constitution). Do not duplicate repo boundary index here.

| Step | Layer/Component | Evidence (file:symbol) | Status | Notes |
| --- | --- | --- | --- | --- |
| 1 | `[Router/Controller]` | `[path:line] :: [symbol]` | `Existing` | `[AEI-### if boundary]` |
| 2 | `[Service]` | `[path:line] :: [symbol]` | `Planned/New code` |  |

## 4. Related Applications & Dependency Inventory *(mandatory)*

> List **all** dependencies used by this operation (internal modules, 2nd-party, 3rd-party, middleware, queues, caches).

| Dependency | Ownership | Direction | Protocol / Interface | Timeout | Retry | Failure / Degradation | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `[name]` | `[internal/2nd-party/3rd-party]` | `[inbound/outbound]` | `[HTTP/gRPC/DB/Queue/Cache]` | `[e.g., 1s]` | `[policy]` | `[behavior]` | `[path:line] / N/A` |

## 5. Sequence Diagram *(mandatory)*

PlantUML. Must include ALL dependencies from Section 4 (Dependency Inventory).
MUST be **class-level** for in-repo interactions (e.g., `OrderController`, `OrderService`, `OrderRepository`) instead of generic `API`.
Must cover all internal class participants in the operation path and show key call/message directions between them.
Each in-repo participant/call MUST be traceable to Section 3 Evidence (`[path:line] :: [symbol]`).
If Section 4 defines timeout/retry/failure-degradation behavior, include at least one critical non-happy path using `alt`/`opt`.
External dependencies are modeled as system participants (not internal classes).
See `/speckit.tasks` Execution Contract: Diagram Rules (SSOT).

```plantuml
@startuml
title [operationId] sequence

actor Client
participant [ControllerClass]
participant [ServiceClass]
participant [RepositoryClass]
participant [ExternalSystem]

Client -> [ControllerClass]: [method] [path]
activate [ControllerClass]

[ControllerClass] -> [ServiceClass]: [request DTO]
[ServiceClass] -> [RepositoryClass]: [query/command]
[ServiceClass] -> [ExternalSystem]: [protocol call]

alt dependency timeout / failure
  [ServiceClass] -> [ServiceClass]: [retry or degrade policy]
end

[ControllerClass] --> Client: [status] [response]
deactivate [ControllerClass]
@enduml
```

## 6. Relevant Code Class Diagram *(mandatory)*

Operation-scoped PlantUML. MUST be consistent with Section 3 (Evidence) & Section 4 (Inventory).
Include only in-repo code structures involved in this operation, with concrete class-level details.
At minimum include: class name, role/responsibility, key attributes or methods, and relevant class relationships (e.g., inheritance/composition/dependency where applicable).
External systems NOT modeled as classes; see Section 4 for ownership/protocol/timeout/retry.
Module-only placeholders are not allowed.
See `/speckit.tasks` Execution Contract: Diagram Rules (SSOT).

```plantuml
@startuml
' Concrete classes directly relevant to this operation (no module placeholders)
class [ControllerClass] {
  +[handleMethod]([RequestDTO]): [ResponseDTO]
}
class [ServiceClass] {
  +[executeMethod]([Input]): [Output]
}
class [RepositoryClass] {
  +[queryOrSave]([Model]): [Result]
}

[ControllerClass] --> [ServiceClass] : uses
[ServiceClass] --> [RepositoryClass] : depends on
' add inheritance/composition/dependency relations relevant to this operation
@enduml
```

## 7. Core Algorithm Pseudocode *(optional)*

```text
[Keep business-critical logic only]
```

## 8. Change List *(mandatory)*

### 8.1 Resources (DB / config / infra)

| Area | Change | Evidence / Plan |
| --- | --- | --- |
| DB | `[migration/table/index]` | `[path] / Planned` |
| Config | `[env/feature flag]` | `[path] / Planned` |
| Infra | `[queue/topic/cache]` | `[path] / Planned` |

### 8.2 Source code modules/files

| File/Module | Change | Status |
| --- | --- | --- |
| `[path]` | `[what changes]` | `Planned/New code` |

### 8.3 Contract/schema deltas

| Item | Delta |
| --- | --- |
| OpenAPI | `[new operation / schema updates]` |

## 9. Performance Analysis *(mandatory)*

- **Latency budget**: `[e.g., p95 < 200ms]`
- **Critical path**: `[calls in order]`
- **External call budgets**: `[timeouts/retries/circuit breakers]`
- **Caching**: `[what/where/TTL]`
- **Concurrency**: `[hot paths / locking / idempotency]`
- **Failure modes**: `[dependency failures and degradation]`
- **Observability**: `[logs/metrics/traces; key fields]`

