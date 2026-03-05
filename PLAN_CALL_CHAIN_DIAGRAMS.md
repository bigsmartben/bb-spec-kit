# 📊 Speckit.Plan 调用链 - 可视化图表

## 1. 完整时序图 (Sequence Diagram)

```
User                AI Agent           Scripts          File System       Models
 │                    │                  │                  │               │
 │ /speckit.plan      │                  │                  │               │
 ├───────────────────>│                  │                  │               │
 │                    │                  │                  │               │
 │                    │  Run setup-plan.sh (--json)         │               │
 │                    ├─────────────────>│                  │               │
 │                    │                  │·Load spec.md    │               │
 │                    │                  ├─────────────────>│               │
 │                    │                  │                  │· Read FEATURE_SPEC
 │                    │                  │<─────────────────┤               │
 │                    │                  │·Copy plan-template
 │                    │                  ├─────────────────>│               │
 │                    │                  │                  │· Create IMPL_PLAN
 │                    │                  │·Return JSON      │               │
 │                    │<─────────────────┤                  │               │
 │                    │ {FEATURE_SPEC, IMPL_PLAN, ...}      │               │
 │                    │                  │                  │               │
 │                    │ Load Context     │                  │               │
 │                    ├───────────────────────────────────>│               │
 │                    │                  │                  │ Read spec.md   │
 │                    │<───────────────────────────────────┤               │
 │                    │ spec.md content                      │               │
 │                    │                  │                  │               │
 │                    ├───────────────────────────────────>│               │
 │                    │                  │                  │ Read constitution.md
 │                    │<───────────────────────────────────┤               │
 │                    │ constitution.md (terminology)       │               │
 │                    │                  │                  │               │
 │                    │ Phase 0: Research                   │               │
 │                    │·Extract unknowns (NEEDS CLARIF.)   │               │
 │                    │·Generate research.md               │               │
 │                    │                  │                  │               │
 │                    ├───────────────────────────────────>│               │
 │                    │                  │                  │ Write research.md
 │                    │<───────────────────────────────────┤               │
 │                    │ research.md generated               │               │
 │                    │                  │                  │               │
 │                    │ Phase 1: Design & Contracts        │               │
 │                    │                  │                  │               │
 │                    │ Step 1: OpenAPI                     │               │
 │                    ├───────────────────────────────────>│               │
 │                    │                  │                  │ Gen openapi.yaml
 │                    │                  │                  │ [FR coverage gate]
 │                    │<───────────────────────────────────┤               │
 │                    │ openapi.yaml generated              │               │
 │                    │                  │                  │               │
 │                    │ Step 2: Data Model                  │               │
 │                    ├───────────────────────────────────>│               │
 │                    │                  │                  │ Gen data-model.md
 │                    │                  │                  │ [Key Path UDD → VO]
 │                    │                  │                  │ [FSM gate if needed]
 │                    │<───────────────────────────────────┤               │
 │                    │ data-model.md generated             │               │
 │                    │                  │                  │               │
 │                    │ Step 3: Test Matrix                 │               │
 │                    ├───────────────────────────────────>│               │
 │                    │                  │                  │ Gen test-case-matrix.md
 │                    │                  │                  │ [Multi-dimensional gates]
 │                    │<───────────────────────────────────┤               │
 │                    │ test-case-matrix.md generated       │               │
 │                    │                  │                  │               │
 │                    │ Agent Context Update                │               │
 │                    │  Run update-agent-context.sh (__AGENT__)
 │                    ├─────────────────>│                  │               │
 │                    │                  │ Detect agent     │               │
 │                    │                  │ Extract tech     │               │
 │                    │                  ├─────────────────>│               │
 │                    │                  │                  │ Update .{agent}/command/
 │                    │                  │<─────────────────┤               │
 │                    │<─────────────────┤ Agent context    │               │
 │                    │ Plan Complete    │                  │               │
 │<───────────────────┤                  │                  │               │
 │ Recommendation: tasks/checklist/preview
 │
 │  [User clicks "Create Tasks" or "Create Checklist"]
 │
 ├─ /speckit.tasks ──────────> (based on plan.md + contracts/*)
 │
 └─ /speckit.checklist ──────> (based on spec.md + plan.md)
```

---

## 2. 输入/处理/输出流

```
                    ┌──── BEFORE: /speckit.specify ────┐
                    │                                   │
                    │  spec.md (Functional Requirements)│
                    │  ├─ Feature narrative             │
                    │  ├─ FR-###, UC-###                │
                    │  ├─ UDD items (Entity.field)      │
                    │  └─ Acceptance scenarios          │
                    │                                   │
                    └───────────────┬────────────────────┘
                                    │
                                    ▼
                    ┌──── INPUT: /speckit.plan ────────────┐
                    │                                      │
                    │  FEATURE_SPEC (spec.md)              │
                    │  + Constitution (terminology)        │
                    │  + IMPL_PLAN template               │
                    │  + Repository conventions            │
                    │                                      │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │  PROCESS: 4 Steps               │
                    │                                │
                    │  1. Setup phase                 │
                    │     ├─ Setup scripts            │
                    │     └─ Load templates           │
                    │                                │
                    │  2. Phase 0: Research           │
                    │     ├─ Extract unknowns         │
                    │     └─ Generate research.md     │
                    │                                │
                    │  3. Phase 1: Design             │
                    │     ├─ OpenAPI (+ FR gate)      │
                    │     ├─ Data model (+ UDD gate)  │
                    │     ├─ Test matrix (+ coverage) │
                    │     └─ Quickstart               │
                    │                                │
                    │  4. Context Update              │
                    │     └─ Agent files              │
                    │                                │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │  OUTPUT: specs/<feature>/       │
                    │                                │
                    │  plan.md (IMPL_PLAN)           │
                    │  ├─ Technical Context          │
                    │  ├─ Constitution Check         │
                    │  ├─ Artifacts Overview         │
                    │  └─ Phase reports              │
                    │                                │
                    │  research.md (Phase 0)         │
                    │  ├─ All decisions              │
                    │  ├─ Rationales                 │
                    │  └─ Alternatives               │
                    │                                │
                    │  contracts/openapi.yaml        │
                    │  ├─ API operations             │
                    │  ├─ x-fr-ids (FR tracing)      │
                    │  └─ x-uc-ids (UC tracing)      │
                    │                                │
                    │  data-model.md (Phase 1)       │
                    │  ├─ Entities & relationships   │
                    │  ├─ UDD → VO → Persistence     │
                    │  ├─ State models (FSM/Lightweight)
                    │  └─ Class diagrams             │
                    │                                │
                    │  contracts/test-case-matrix.md │
                    │  ├─ Test cases (CaseID)        │
                    │  ├─ Traceability (FR→CaseID)   │
                    │  └─ Coverage gates             │
                    │                                │
                    │  quickstart.md                 │
                    │  └─ Getting started guide      │
                    │                                │
                    │  .{agent}/commands/update      │
                    │  └─ Agent context updated      │
                    │                                │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌──── AFTER: Ready for Tasks ─────┐
                    │                                 │
                    │  → /speckit.tasks               │
                    │     (依赖排序的工作项)            │
                    │                                 │
                    │  → /speckit.checklist           │
                    │     (需求质量清单)               │
                    │                                 │
                    │  → /speckit.preview             │
                    │     (HTML 审查视图)              │
                    │                                 │
                    └─────────────────────────────────┘
```

---

## 3. 控制流决策树

```
                            ┌─ /speckit.plan ─┐
                            │                 │
                      ┌─────▼──────┐
                      │  Setup Phase │
                      │  (scripts)   │
                      ├─────┬──────┤
                      │ Error?      │
                      └─────┬──────┘
                            │
                    ┌───────No────────┐
                    │                 │
         ┌──────────▼─────────┐
         │  Phase 0: Research │
         │  Extract unknowns  │
         │  Generate research │
         ├──────────┬─────────┤
         │ Error?   │
         └──────────┬─────────┘
                    │
             ┌──────No──────┐
             │              │
    ┌────────▼───────────┐
    │ Phase 1: Design    │
    │ Applicability?     │
    ├─Yes───────┬────No─┤
    │           │       │
    ▼           ▼       ▼
  OpenAPI  Custom  Skip
 +FRGate  contract ApiArtifacts
    │           │       │
    └─────┬─────┴───────┘
          │
    ┌─────▼──────────────┐
    │  Data Model        │
    │ [UDD→VO gate]      │
    │ [FSM gate]         │
    ├────────┬───────────┤
    │ Error? │
    └────────┬───────────┘
             │
        ┌────No───┐
        │         │
    ┌───▼──────────────┐
    │  Test Matrix     │
    │ [Coverage gates] │
    ├────────┬─────────┤
    │ Error? │
    └────────┬─────────┘
             │
        ┌────No───┐
        │         │
    ┌───▼──────────────────┐
    │  Agent Context       │
    │  Update              │
    ├────────┬─────────────┤
    │ Done   │
    └────────┬─────────────┘
             │
    ┌────────▼──────────────┐
    │  Recommend:           │
    │  → /speckit.tasks     │
    │  → /speckit.checklist │
    │  → /speckit.preview   │
    └───────────────────────┘
```

---

## 4. 依赖关系图

```
spec.md (from /speckit.specify)
  ├─ FR-###, UC-###
  ├─ UDD items
  ├─ Acceptance scenarios
  └─ Feature narrative
       │
       ▼
   ┌─ setup-plan.sh ─┐
   │                 │
   ▼                 ▼
plan.md ◄────────┐   IMPL_PLAN path
(template)       │
                 │
constitution.md  ├─┐
(terminology)    │ │
                 │ │
openapi-         │ │
template.yaml    │ │
                 │ │
plan-template.md │ │
                 │ │
                 ▼ │
         ┌──────────▼───────────┐
         │  /speckit.plan       │
         │                      │
         │  Phase 0: Research   │
         │  ├─ research.md ◄────┘
         │  │
         │  Phase 1: Design
         │  ├─ contracts/
         │  │  └─ openapi.yaml ◄─── FR coverage gate
         │  ├─ data-model.md ◄────── UDD→VO gate
         │  │                        FSM gate
         │  ├─ test-case-matrix.md ◄─ Multi-gate
         │  └─ quickstart.md
         │
         │  update-agent-context.sh
         │  └─ .{agent}/commands/...
         │
         └──────────┬──────────┘
                    │
         ┌──────────┴──────────┬──────────┐
         │                     │          │
         ▼                     ▼          ▼
    /speckit.   /speckit.   /speckit.
     tasks       checklist   preview
```

---

## 5. 硬门控与状态转移

```
┌─────────────────────────────────────────┐
│      PLAN EXECUTION STATE MACHINE       │
└─────────────────────────────────────────┘

State: SETUP
├─ Action: Run setup-plan.sh
├─ Outputs: JSON paths
├─ Gate: None
└─ Transition: RESEARCH (if success)
   └─ FAILED (if setup error)

State: RESEARCH
├─ Action: Extract unknowns, generate research.md
├─ Outputs: research.md
├─ Gate: None
└─ Transition: DESIGN (if research complete)

State: DESIGN
├─ Action: Generate openapi.yaml, data-model.md, test-case-matrix.md
├─ Outputs: All contracts + models
├─ Gates:
│  ├─ [HARD] openapi.yaml FR coverage: every FR-### ∈ x-fr-ids
│  │        ERROR if: any FR-### unmapped
│  ├─ [HARD] data-model.md UDD→VO mapping: Key Path + System-backed items
│  │        ERROR if: any mapped item missing VO
│  ├─ [HARD] data-model.md FSM: if N>4 or T≥2N, Full FSM required
│  │        ERROR if: missing or incomplete FSM
│  └─ [HARD] test-case-matrix.md coverage: FR, operationId, state transitions
│           ERROR if: gaps in coverage
└─ Transition: CONTEXT_UPDATE (if all gates pass)
   └─ FAILED (if any gate violated)

State: CONTEXT_UPDATE
├─ Action: Run update-agent-context.sh
├─ Outputs: .{agent}/commands/... updated
├─ Gate: None (informational only)
└─ Transition: COMPLETE (always)

State: COMPLETE
├─ Outputs: plan.md + all artifacts
├─ Status: ✅ Plan ready for tasks/checklist
└─ Recommendation: 
   ├─ /speckit.tasks (next workflow step)
   ├─ /speckit.checklist (parallel track)
   └─ /speckit.preview (optional review)

State: FAILED
├─ Cause: Gate violation(s)
├─ Status: ❌ Plan incomplete
└─ Recovery: Fix spec.md or plan content, then re-run /speckit.plan
```

---

## 6. 追踪维度（Traceability Matrix）

```
┌──────────────────────────────────────────┐
│   MULTI-DIMENSIONAL TRACEABILITY         │
└──────────────────────────────────────────┘

Spec Layer (spec.md)
├─ FR-001: "User can create account"
├─ UC-Register: [Scenario+Acceptance]
└─ UDD: {User.email, User.name, ...}
       │
       ▼ (flows into)
       
Implementation Plan Layer (plan.md + contracts/)
├─ FR-001 mapped to operationId: createUser (openapi.yaml)
│   └─ x-fr-ids: [FR-001]
├─ UDD items mapped to VO fields:
│   ├─ User.email → UserVO.email
│   └─ User.name → UserVO.name
└─ State transitions mapped to test cases:
       │
       ▼ (flows into)
       
Task Layer (tasks.md - future)
├─ Task-1: Implement user schema
│   └─ Related FR-001, operationId=createUser
├─ Task-2: Add email validation
│   └─ Related assertions in test-case-matrix
└─ Task-3: Implement user creation endpoint
       │
       ▼ (flows into)
       
Test Layer (test-case-matrix.md)
├─ TC-createUser-001 (happy-path)
│   ├─ FR-001 ✓
│   ├─ operationId: createUser ✓
│   ├─ CaseID: TC-createUser-001 ✓
│   └─ Scenario: Given valid email, When POST /users, Then 201 Created
├─ TC-createUser-002 (validation)
│   ├─ FR-001, FR-002 ✓
│   ├─ operationId: createUser ✓
│   ├─ CaseID: TC-createUser-002 ✓
│   └─ Scenario: Given missing email, When POST /users, Then 400 Bad Request

Verification Path:
spec.md → openapi.yaml → test-case-matrix.md → tasks.md → implementation code

Quality Assertions:
- No orphan FRs (every FR-### appears in openapi.yaml)
- No orphan test cases (every TC relates to ≥1 FR-###)
- No orphan UDD items (Key Path + System-backed → VO in data-model)
- No orphan operations (every operationId relates to ≥1 FR-###)
```

---

## 7. 脚本调用堆栈

```
User: /speckit.plan
       │
       ├─ [CLI Agent]
       │
       └─ templates/commands/plan.md (frontmatter: scripts)
          │
          ├─ scripts/bash/setup-plan.sh --json
          │  ├─ scripts/bash/common.sh (load functions)
          │  ├─ get_feature_paths() (extract paths)
          │  ├─ check_feature_branch() (validate branch)
          │  └─ Return JSON: {FEATURE_SPEC, IMPL_PLAN, ...}
          │
          ├─ [AI Agent processes spec.md]
          │  └─ Load context, execute phases
          │
          └─ scripts/bash/update-agent-context.sh __AGENT__
             ├─ scripts/bash/common.sh (load functions)
             ├─ Detect agent type (__AGENT__ param)
             ├─ Find agent context file (.{agent}/commands/...)
             ├─ Extract tech stack from plan.md
             │  ├─ **Language/Version**:
             │  ├─ **Primary Dependencies**:
             │  ├─ **Storage**:
             │  └─ **Project Type**:
             └─ Append to agent context file (between markers)
```

---

## 8. 门控详解

```
┌──────────────────────────────────────────┐
│         HARD GATES (ERROR if violated)   │
└──────────────────────────────────────────┘

Gate 1: FR Coverage in openapi.yaml
├─ Location: openapi.yaml + plan.md
├─ Rule: Every in-scope FR-### MUST appear in ≥1 operation's x-fr-ids
├─ Violation: ERROR
├─ Example:
│  Spec says: FR-001, FR-002, FR-003
│  openapi.yaml has:
│    POST /users
│      x-fr-ids: [FR-001]    ✓ FR-001 found
│    GET /users/:id
│      x-fr-ids: [FR-002]    ✓ FR-002 found
│    PATCH /users/:id
│      x-fr-ids: [FR-001, FR-003]    ✓ FR-003 found
│  Result: ✅ PASS (all FRs accounted for)

Gate 2: Key Path UDD → VO Mapping
├─ Location: data-model.md
├─ Rule: All Key Path (P1) + System-backed UDD items MUST map to VO fields
├─ Violation: ERROR
├─ Example:
│  UDD has (P1, System-backed):
│    ├─ User.email
│    ├─ User.name
│    └─ User.phone
│  data-model.md has mapping table:
│    User.email → UserVO.email ✓
│    User.name → UserVO.name ✓
│    User.phone → [missing]    ✗  ERROR
│  Recovery: Either add VO field or mark as out-of-scope

Gate 3: FSM Coverage (when applicable)
├─ Location: data-model.md
├─ Rule: If N>4 or T≥2N, Full FSM required; else Lightweight State Model OK
├─ Violation: ERROR
├─ Example:
│  Entity: Order
│  States: PENDING, PROCESSING, COMPLETED, FAILED (N=4)
│  Transitions: 4 (T=4)
│  Applicability: T≥2N? → 4≥8? → NO → Lightweight Model OK
│
│  Entity: Payment
│  States: CREATED, AUTHORIZED, CAPTURED, FAILED, REFUNDING, REFUNDED (N=6)
│  Applicability: N>4? → YES → Full FSM REQUIRED
│  Must include: State enum, transition table, PlantUML diagram

Gate 4: Test Case Matrix Coverage (multi-dimensional)
├─ Location: contracts/test-case-matrix.md
├─ Rules:
│  ├─ Every FR-### appears in ≥1 CaseID row
│  ├─ Every operationId has ≥1 happy-path (P1 when Key Path)
│  ├─ Every operationId has ≥1 negative case
│  ├─ Every state transition has ≥1 test case
│  ├─ Every meaningful HTTP status code covered
│  └─ Key Path UDD outputs assert fields explicitly
├─ Violation: ERROR
├─ Example (simplified):
│  Required FRs: FR-001, FR-002, FR-003
│  Test cases:
│    TC-create-001: FR-001 ✓
│    TC-create-002: FR-002 ✓
│    TC-update-001: FR-003 ✓
│  Operations: POST /users (create), PATCH /users/:id (update)
│    POST /users: ✓ happy-path (TC-001), ✓ negative (TC-002)
│    PATCH /users: ✓ happy-path, ✓ state transition
│  Result: ✅ PASS
```

---

## 9. 示例：完整的 plan 输出文件结构

```
specs/5-user-registration/
├─ spec.md                          ← from /speckit.specify
│
├─ plan.md                          ← IMPL_PLAN (主输出)
│  ├─ ## Technical Context
│  │  ├─ **Language/Version**: Python 3.11
│  │  ├─ **Primary Dependencies**: fastapi, sqlalchemy
│  │  ├─ **Storage**: PostgreSQL 14
│  │  └─ **Project Type**: REST API
│  ├─ ## Constitution Check
│  ├─ ## Artifacts Overview & Navigation
│  ├─ ## Phase 0: Outline & Research
│  │  └─ research.md status: Generated
│  └─ ## Phase 1: Design & Contracts
│     ├─ contracts/openapi.yaml: Generated
│     ├─ data-model.md: Generated
│     ├─ contracts/test-case-matrix.md: Generated
│     └─ quickstart.md: Generated
│
├─ research.md                      ← Phase 0 output
│  ├─ Tech stack decision: FastAPI because [rationale]
│  ├─ Database choice: PostgreSQL because [rationale]
│  └─ Authentication approach: JWT tokens because [rationale]
│
├─ contracts/
│  ├─ openapi.yaml                  ← API definition
│  │  ├─ POST /users (createUser)
│  │  │  └─ x-fr-ids: [FR-001, FR-002]
│  │  ├─ GET /users/:id (getUser)
│  │  │  └─ x-fr-ids: [FR-003]
│  │  └─ PATCH /users/:id (updateUser)
│  │     └─ x-fr-ids: [FR-004]
│  │
│  └─ test-case-matrix.md           ← Test strategy
│     ├─ TC-createUser-001: Happy path
│     ├─ TC-createUser-002: Validation (email required)
│     ├─ TC-getUser-001: Happy path
│     └─ TC-updateUser-001: State transition
│
├─ data-model.md                    ← Data & state
│  ├─ ## Entities
│  │  └─ User {id, email, name, status, created_at}
│  ├─ ## Key Path UDD → VO Coverage
│  │  ├─ User.email → UserVO.email ✓
│  │  ├─ User.name → UserVO.name ✓
│  │  └─ User.status → UserVO.status ✓
│  ├─ ## VO → Persistence Mapping
│  │  ├─ UserVO.email → users.email ✓
│  │  └─ ...
│  └─ ## State Models
│     └─ User status: PENDING → VERIFIED (Lightweight Model)
│
└─ quickstart.md                    ← Quick reference
   └─ 快速开始指南、测试数据、环境设置
```

---

## 10. 异常处理路径

```
Error Scenarios:

Scenario A: Setup Phase Failure
    /speckit.plan
         │
    [setup-plan.sh fails]
         │
    ❌ Cannot extract paths
    └─ Recovery: Check if on proper feature branch, verify git status

Scenario B: FR Coverage Gate Violation  
    Phase 1: Design
         │
    [openapi.yaml generated but missing FR-003]
         │
    ❌ ERROR: FR-003 not mapped
    ├─ Status: Plan marked as ERROR
    ├─ Location: plan.md, section "Artifacts Overview"
    └─ Recovery: 
      - Add missing FR-003 to an operation in openapi.yaml
      - OR reclassify FR-003 as out-of-scope and document in plan.md
      - Re-run /speckit.plan

Scenario C: UDD → VO Mapping Gap
    Phase 1: Data Model
         │
    [UDD has User.phone but VO mapping missing]
         │
    ❌ ERROR: Key Path UDD item unmapped
    ├─ Status: Plan marked as ERROR
    └─ Recovery:
      - Add UserVO.phone field, or
      - Mark User.phone as UI-local (not system-backed), or
      - Reclassify as non-Key Path
      - Re-run /speckit.plan

Scenario D: FSM Incompleteness
    Phase 1: Data Model
         │
    [Order has 6 states but no state diagram]
         │
    ❌ ERROR: FSM required but missing
    ├─ Status: Plan marked as ERROR
    └─ Recovery:
      - Add Full FSM (state enumeration, transition table, PlantUML)
      - OR reclassify Order as non-stateful (if valid)
      - Re-run /speckit.plan

Recovery Pattern:
    Error detected
         │
    Diagnose root cause
         │
    Fix spec.md or plan.md
         │
    Re-run /speckit.plan
         │
         └─→ Re-execute from Phase that failed
             (most phases are idempotent)
```

---

*完整调用链可视化 - 基于 sourcegraph-mcp 深度分析*
