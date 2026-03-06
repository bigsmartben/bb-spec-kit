# 📋 Spec-Kit `speckit.plan` 调用链深度分析

**分析日期**: 2026-03-05  
**使用工具**: iss-mcp (代码搜索与分析)  
**目标仓库**: github.com/bigsmartben/bb-spec-kit

---

## 🎯 快速概览

`speckit.plan` 是 Spec-Driven Development 工作流中的**第二个核心命令**，负责将特性规范（spec）转换为**实现计划**及相关的**设计制品**。

| 维度 | 信息 |
|------|------|
| **位置** | `templates/commands/plan.md` |
| **输入** | `FEATURE_SPEC` (spec.md) |
| **输出** | `IMPL_PLAN`, 设计制品 (openapi.yaml, data-model.md, 等) |
| **脚本** | `setup-plan.sh` / `setup-plan.ps1` |
| **上下文更新** | `update-agent-context.sh` |
| **执行时机** | `/speckit.specify` 之后 |
| **后续命令** | `/speckit.tasks`, `/speckit.checklist`, `/speckit.preview` |

---

## 📥 输入信息

### 1. 触发源（前置命令）

```
speckit.specify → generat spec.md
                ↓
             handoff
                ↓
         speckit.plan ← 用户调用或通过 handoff
```

**从 spec.md 获取**:
- Feature description (自然语言)
- Functional Requirements (FR-###)
- Use cases / Scenarios (UC-###)
- UI Data Dictionary (UDD) - Entity.field
- Acceptance criteria

### 2. 上下文（宪法与模板）

```
plan.md 加载的上下文:

┌─────────────────────────────────────┐
│ Read FEATURE_SPEC (spec.md)         │
│   - Feature narrative                │
│   - FR/UC enumeration               │
│   - UDD items (Key Path + others)   │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Read Project Constitution           │
│ Pref: .specify/memory/constitution  │
│ Fallback: memory/constitution.md    │
│   - Terminology authority           │
│   - Layering rules (UDD→VO→Persist) │
│   - Architecture Evidence Index (AEI)│
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Load IMPL_PLAN Template             │
│ Pref: .specify/templates/plan-...   │
│ Fallback: templates/plan-template    │
│   - Section structure               │
│   - Mandatory fields format         │
└─────────────────────────────────────┘
```

**用户输入**: `$ARGUMENTS` (通常为空或改进说明)

---

## ⚙️ 核心执行流程

### Step 1: 初始化（Setup）

```bash
# 调用脚本
{SCRIPT} = scripts/bash/setup-plan.sh --json  # Bash
         | scripts/powershell/setup-plan.ps1 -Json  # PowerShell

# 脚本返回 JSON:
{
  "FEATURE_SPEC": "specs/1-feature-name/spec.md",
  "IMPL_PLAN": "specs/1-feature-name/plan.md",
  "SPECS_DIR": "specs/1-feature-name/",
  "BRANCH": "1-feature-name",
  "HAS_GIT": "true"
}
```

**脚本动作**:
1. ✅ 获取当前 branch 名称
2. ✅ 验证是否在功能 branch 上
3. ✅ 确定 FEATURE_SPEC 路径 (spec.md)
4. ✅ 确定 IMPL_PLAN 路径 (plan.md)
5. ✅ 从模板复制 plan-template.md → IMPL_PLAN

### Step 2: 阶段 0 - 研究与线索

**提取未知项**:
```
从 Technical Context 识别:
├─ NEEDS CLARIFICATION → Research tasks
├─ Dependencies → Best practices tasks
├─ Integrations → Patterns tasks
└─ Architecture decisions → Evidence gathering

枚举 FEATURE_SPEC 中的:
├─ Functional Requirements (FR-###)
├─ Use Cases (UC-###)
├─ UI Data Dictionary 项目 (Entity.field)
│   ├─ Key Path items (P1)
│   └─ System-backed vs UI-local classification
└─ Stateful entities & state transitions
```

**生成 research.md**:
```
format:
  Decision: [what was chosen]
  Rationale: [why chosen]
  Alternatives considered: [evaluated but not chosen]
```

### Step 3: 阶段 1 - 设计与制品

#### 3.1 适用性决策（强制）

```
If feature includes frontend ↔ backend HTTP API surface:
  ✅ Generate API-centric artifacts (steps 1-3 below)
Else:
  ⚠️  Do NOT force OpenAPI/Test Matrix
  └─ Use project-appropriate contract format (CLI schema, etc.)

Hard rule: Compatibility-first
  - Additive change only (no deletions/type changes)
  - Preserve existing interfaces
  - If breaking change necessary: justify + migration strategy
```

#### 3.2 Step 1: 接口定义 (OpenAPI 3.0)

**生成**: `specs/<feature>/contracts/openapi.yaml`

```yaml
# OpenAPI structure requirements:
openapi: 3.0.0
paths:
  /{operationId}:
    post/get/patch/delete/put:
      operationId: uniqueId
      summary: ""
      description: ""
      x-fr-ids: [FR-001, FR-003]  # FR 追踪
      x-uc-ids: [UC-CreateOrder]  # UC 追踪（可选）
      requestBody:
        content:
          application/json:
            schema: {...}
      responses:
        200:
          content:
            application/json:
              schema: {...}
        4xx/5xx: {...}
```

**关键约束 (ERROR if violated)**:
- ✅ **FR 覆盖率**: 每个 in-scope `FR-###` 都必须在至少一个 operation 的 `x-fr-ids` 中
- ✅ **Operation 合理性**: 按照 spec 中的特性描述和场景

#### 3.3 Step 2: 数据模型 (data-model.md)

**生成**: `specs/<feature>/data-model.md`

```markdown
## Entities & Classes
- Class A
  - field1: type (validation rules)
  - field2: type (relationship to Class B)

## Key Path UDD → VO Coverage Table
| UDD Item (Entity.field) | UC/Scenario (P1) | operationId | VO field path | Notes |
|---|---|---|---|---|
| User.email | UC-Register | createUser | request.email | System-backed |

## VO → Persistence Mapping
| VO field path | Persistence source | Transform | Evidence |
|---|---|---|---|
| UserVO.email | users.email | trim() | src/models/User.ts:45 |

## State Models
### Entity: Order
- States: PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED
- Transitions: (Graph)
- FSM Applicable: Yes (5 states, 7 transitions) → Full FSM required
```

**覆盖约束**:
- ✅ **Key Path UDD → VO 映射**: 无遗漏
- ✅ **VO → Persistence 映射**: 完整追踪
- ✅ **FSM 或 Lightweight State Model**: 每个有状态实体

#### 3.4 Step 3: 测试矩阵 (test-case-matrix.md)

**生成**: `specs/<feature>/contracts/test-case-matrix.md`

```markdown
## Scope & Assumptions
- In-scope: Create/Read/Update operations
- Out-of-scope: Batch deletion
- Auth model: Bearer token
- Test data: Mocked via fixtures

## Case Table
| CaseID | operationId | FR-### | Priority | Tags | Scenario (Given/When/Then) | Pre-conditions | Inputs | Expected Output | Status Code | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-createUser-001 | createUser | FR-001 | P1 | happy-path | Given valid email, When POST /users, Then User created | DB clean | {email, name} | {id, email, name} | 201 | Baseline |
| TC-createUser-002 | createUser | FR-002 | P1 | validation | Given missing email, When POST /users, Then Error | DB clean | {name only} | {error: "email required"} | 400 | Boundary |
| TC-updateUser-010 | updateUser | FR-003 | P2 | state-transition | Given Order in PENDING, When PATCH to PROCESSING, Then transition allowed | Order exists | {status: PROCESSING} | {id, status, updated_at} | 200 | Valid state |
| TC-updateUser-011 | updateUser | FR-003 | P2 | concurrency | Given two concurrent updates, When POST /users/1, Then deduplicated | Order exists + idempotency key | {...} | {deduplicated result} | 200 | Race condition |

## Traceability
FR-001 → createUser → TC-createUser-001
UC-Register → FR-001 → TC-createUser-001, TC-createUser-002

## Coverage Gates
- [x] All in-scope FRs mapped
- [x] Happy path + negative cases for each operation
- [x] All designed state transitions covered
- [x] Key Path UDD assertions explicit
```

**覆盖约束 (ERROR if violated)**:
- ✅ **FR 追踪**: 每个 `FR-###` 在 ≥1 个 CaseID 中
- ✅ **操作覆盖**: 每个 operation:
  - 1 个 happy-path (P1 when Key Path)
  - 1+ 个 negative case (validation, authn/authz)
- ✅ **状态转移**: 每个合法转移 ≥1 个 case
- ✅ **Schema 覆盖** (Key Path): 显式断言 response 字段

#### 3.5 Step 4: 其他制品

**不在 plan 中生成** (由 `/speckit.tasks` 生成):
```
contracts/interface-details/<operationId>.md ← speckit.tasks 负责
```

**在 plan 中生成**:
```
specs/<feature>/
├─ research.md           (Phase 0 - 研究)
├─ contracts/openapi.yaml       (Phase 1 - API)
├─ data-model.md         (Phase 1 - 数据)
├─ contracts/test-case-matrix.md (Phase 1 - 测试)
├─ contracts/...         (其他格式 if applicable)
└─ quickstart.md         (Phase 1 - 快速开始)
```

### Step 4: 上下文更新

```bash
# 运行 agent 特定脚本
{AGENT_SCRIPT} = scripts/bash/update-agent-context.sh __AGENT__
               | scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__

# __AGENT__ 被替换为实际的 agent 名称:
# claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, ...

# 脚本动作:
1. 检测当前 AI agent 类型 ($1 参数)
2. 定位 agent 特定的上下文文件:
   - .claude/commands/  → Claude Code
   - .cursor/commands/  → Cursor IDE
   - .codex/prompts/    → Codex CLI
   等等
3. 从 plan.md 提取技术栈:
   - **Language/Version**:
   - **Primary Dependencies**:
   - **Storage**:
   - **Project Type**:
4. 更新 agent 上下文文件 (追加新技术到标记区间内)
5. 保留现有的手动添加项
```

---

## 📤 输出（制品）

### A. 主制品

```
specs/<feature>/plan.md (IMPL_PLAN)
├─ ## Technical Context
│  └─ Language/Version, Dependencies, Storage, Project Type
├─ ## Constitution Check
│  └─ Terminology validation, Layering compliance
├─ ## Artifacts Overview & Navigation
│  └─ Links to all generated artifacts + Status
├─ ## Phase 0 Outline & Research
│  └─ research.md path + status
├─ ## Phase 1 Design & Contracts
│  ├─ contracts/openapi.yaml status
│  ├─ data-model.md status
│  ├─ contracts/test-case-matrix.md status
│  └─ Other contracts status
└─ ## Complexity Tracking
   └─ Non-obvious decisions, FSM justifications
```

### B. 设计制品

```
specs/<feature>/
├─ research.md
│  └─ 所有 NEEDS CLARIFICATION 的解答
├─ contracts/openapi.yaml
│  └─ 完整的 API 定义，FR/UC 追踪
├─ data-model.md
│  ├─ UDD → VO → Persistence 映射表
│  ├─ 状态模型（Full FSM 或 Lightweight）
│  └─ 类图和关系图
├─ contracts/test-case-matrix.md
│  ├─ 测试用例矩阵（CaseID，操作，优先级，标签）
│  ├─ 追踪表（FR → CaseID, UC → CaseID）
│  └─ 覆盖门控（覆盖率检查清单）
├─ contracts/...
│  └─ 其他项目适用的契约格式
└─ quickstart.md
   └─ 快速开始指南
```

### C. 元信息

```
plan.md 中的标记字段（被 update-agent-context.sh 解析）:

**Language/Version**: Python 3.11, fastapi 0.95.0
**Primary Dependencies**: sqlalchemy, pydantic
**Storage**: PostgreSQL 14
**Project Type**: REST API backend
```

---

## 🔗 Handoff 目标（后续命令）

plan.md 中的 YAML frontmatter 定义了两个 handoff：

```yaml
handoffs: 
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.checklist
    prompt: Create a requirements quality checklist for this feature
    send: true
```

### Handoff 1: → speckit.tasks

```
speckit.plan (完成)
       ↓
    [USER 点击 "Create Tasks"]
       ↓
speckit.tasks (基于 plan 执行)
       └─ 输入:
          - plan.md (tech stack, libraries, structure)
          - spec.md (user stories + priorities)
          - data-model.md (UDD→VO coverage, VO→Persistence)
          - contracts/* (openapi.yaml, test-case-matrix)
       └─ 输出:
          - tasks.md (依赖排序的任务列表)
          - interface-details/*.md (per-operation docs)
       └─ Handoff targets:
          - speckit.analyze (一致性审计)
          - speckit.implement (开始实现)
```

### Handoff 2: → speckit.checklist

```
speckit.plan (完成)
       ↓
    [USER 点击 "Create Checklist"]
       ↓
speckit.checklist (基于 spec + plan 执行)
       └─ 输入:
          - spec.md (功能描述)
          - plan.md (设计决策)
       └─ 输出:
          - checklist.md (需求质量清单)
       └─ Handoff target:
          - speckit.implement (开始实现)
```

---

## 📋 推荐后续命令

### 立即可用（plan 完成后）

```
1️⃣  speckit.tasks
    用途: 将 plan 转成可执行任务
    何时: 当 plan 中的设计制品完整时
    
2️⃣  speckit.checklist
    用途: 生成需求质量清单
    何时: 立即（无需等待 tasks 完成）
    
3️⃣  speckit.preview
    用途: 生成 HTML 审查视图
    何时: plan 和 tasks 都完成后
    输入: 可以是 spec.md / plan.md / tasks.md 之一
```

### 可选命令

```
4️⃣  speckit.analyze
    用途: 交叉制品一致性审计
    何时: 在实现前进行最后检查
    
5️⃣  speckit.design  (如果前端组件在范围内)
    用途: 生成设计交付物 (UX/UI/原型)
    何时: plan 完成后，tasks 之前
```

---

## 🔍 关键约束与门控

### Hard Gates (ERROR if violated)

```
③ 功能需求覆盖 (openapi.yaml):
  每个 in-scope FR-### 都必须在至少一个 operation 的 x-fr-ids 中
  
   → IMPL_PLAN 被标记为 ERROR，任务无法继续

③ Key Path UDD → VO 映射 (data-model.md):
  所有 Key Path (P1) + System-backed UDD items 必须有 VO 映射
  
   → 缺少映射 = ERROR

③ FSM 覆盖 (data-model.md):
  有状态实体必须有 Full FSM（if N > 4 or T ≥ 2N）
  否则 Lightweight State Model
  
   → 无状态模型 = ERROR

③ 测试矩阵覆盖 (test-case-matrix.md):
  - 每个 FR 需 ≥1 个 CaseID
  - 每个 operation 需 happy-path + negative cases
  - 状态转移覆盖 (if applicable)
  
   → 缺少覆盖 = ERROR
```

### Validation Markers

```
NEEDS CLARIFICATION: [description]
  └─ 自动捕获的未知项，plan 中标记后由 Phase 0 research.md 解决

ERROR: [description]
  └─ 门控违反，阻止继续，需修改 spec 或 plan

[THINKS CLARIFICATION: ...]
  └─ 可选标记，由 AI 在不确定时使用
```

---

## 📊 调用链可视化

### 完整工作流

```
┌──────────────────────────────────────────────────────────────┐
│ USER: /speckit.plan                                          │
└──────────────────┬───────────────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │ setup-plan.sh       │
        │ (setup-plan.ps1)    │
        └──────────┬──────────┘
                   │
                   ├─ Copy plan-template.md → plan.md
                   ├─ Parse spec.md
                   └─ Return JSON paths
                   │
        ┌──────────▼──────────────────────┐
        │ Load Context                     │
        ├─ FEATURE_SPEC (spec.md)         │
        ├─ Constitution (terminology)     │
        └─ IMPL_PLAN template             │
                   │
        ┌──────────▼──────────────────────┐
        │ Phase 0: Research                │
        ├─ Extract unknowns from spec     │
        ├─ Enumerate FR/UC                │
        ├─ Extract UDD items              │
        ├─ Identify architecture evidence │
        └─ Generate research.md           │
                   │
        ┌──────────▼──────────────────────┐
        │ Phase 1: Design & Contracts      │
        ├─ Applicability decision         │
        │  (HTTP API surface?)            │
        ├─ Step 1: openapi.yaml           │
        │  [FR coverage gate]              │
        ├─ Step 2: data-model.md          │
        │  [Key Path UDD → VO gate]        │
        │  [FSM gate if applicable]        │
        ├─ Step 3: test-case-matrix.md    │
        │  [Multi-dimensional coverage]    │
        └─ Step 4: quickstart.md          │
                   │
        ┌──────────▼──────────────────────┐
        │ Agent Context Update             │
        ├─ Detect current agent           │
        ├─ Extract tech stack from plan   │
        └─ Update .{agent}/commands/...   │
                   │
        ┌──────────▼──────────────────────┐
        │ Output Summary                   │
        ├─ IMPL_PLAN path                 │
        ├─ Generated artifacts list       │
        ├─ Recommendation: /speckit.tasks │
        └─ Recommendation: /speckit.checklist
                   │
                   │  [Handoff available]
                   ├─────────────────┬──────────────────┐
                   │                 │                  │
        ┌──────────▼──────┐ ┌────────▼────────┐ ┌──────▼──────────┐
        │ speckit.tasks   │ │speckit.checklist│ │  speckit.preview│
        │ (optional user) │ │ (optional user) │ │ (optional user) │
        └─────────────────┘ └─────────────────┘ └─────────────────┘
              │                     │                    │
              └──────────┬──────────┴────────┬───────────┘
                         │
                    [Plan complete]
```

---

## 🛠️ 脚本接口

### setup-plan.sh / setup-plan.ps1

```bash
# Bash:
./scripts/bash/setup-plan.sh --json

# PowerShell:
.\scripts\powershell\setup-plan.ps1 -Json

# JSON Output:
{
  "FEATURE_SPEC": "specs/1-feature-name/spec.md",
  "IMPL_PLAN": "specs/1-feature-name/plan.md",
  "SPECS_DIR": "specs/1-feature-name/",
  "BRANCH": "1-feature-name",
  "HAS_GIT": "true"
}
```

### update-agent-context.sh / update-agent-context.ps1

```bash
# Bash - 更新特定 agent:
./scripts/bash/update-agent-context.sh claude

# Bash - 更新所有现存 agent 文件:
./scripts/bash/update-agent-context.sh

# PowerShell - 更新特定 agent:
.\scripts\powershell\update-agent-context.ps1 -AgentType claude

# PowerShell - 更新所有现存 agent 文件:
.\scripts\powershell\update-agent-context.ps1

# Supported agents:
# claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf
# kilocode|auggie|roo|codebuddy|amp|shai|q|agy|bob|qodercli
```

---

## 📝 Frontmatter 元数据

```yaml
---
description: Execute the implementation planning workflow using the plan template to generate design artifacts.

# Handoff targets (后续命令)
handoffs: 
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.checklist
    prompt: Create a requirements quality checklist for this feature
    send: true

# Script hooks
scripts:
  sh: scripts/bash/setup-plan.sh --json
  ps: scripts/powershell/setup-plan.ps1 -Json

# Agent context update hooks
agent_scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---
```

---

## 🔐 质量保证

### 执行前检验

```
□ spec.md 已完整生成（来自 /speckit.specify）
□ 宪法文件存在（constitution.md）
□ 当前在功能 branch 上
```

### 执行中检验

```
□ 所有 NEEDS CLARIFICATION 在 Phase 0 解决
□ openapi.yaml 通过 FR 覆盖率门控
□ data-model.md 通过 UDD→VO 映射门控
□ test-case-matrix.md 通过多维覆盖门控
□ Agent 上下文已更新
```

### 执行后验证

```
□ plan.md 已生成（非空）
□ 所有设计制品都在 specs/<feature>/ 下
□ 相对链接在 plan.md 中工作正常
□ User 可以点击 handoff 到 tasks / checklist
```

---

## ⚠️ 常见问题

### Q: plan 中失败（ERROR）意味着什么？
**A**: 一个或多个硬门控被违反了。可能是：
- 某个 FR 未在 openapi.yaml 中映射
- Key Path UDD item 缺少 VO 映射
- 状态模型不完整

修复方案: 返回 spec.md 修改，或调整 plan 中的设计决策使其满足门控。

### Q: 何时需要完整的 FSM vs Lightweight State Model？
**A**: 
```
计算: N = states 数量, T = transitions 数量
If (N > 4 OR T ≥ 2N):
  → Full FSM required (state enumeration + transition table + diagram)
Else:
  → Lightweight State Model (state field definition + allowed/forbidden transitions)
```

### Q: 如果项目不是 REST API 呢？
**A**: plan 中有适用性决策：
```
If feature includes frontend ↔ backend HTTP API:
  ✅ Generate OpenAPI + Test Matrix
Else:
  └─ Use project-appropriate contract format
     (CLI schema, public library API, internal module contracts, etc.)
```

### Q: plan 和 tasks 的区别是什么？
**A**:
```
plan.md (设计层):
  - 技术栈、架构决策
  - API 契约、数据模型
  - 测试策略
  
tasks.md (实现层):
  - 依赖排序的工作项
  - 每个任务的检查清单
  - 并行化/串行化标记
```

---

## 📚 相关文件

| 文件 | 用途 |
|------|------|
| `templates/commands/plan.md` | plan 命令的完整定义 |
| `templates/plan-template.md` | plan.md 的模板 |
| `templates/plan-template.md` | IMPL_PLAN 初始结构 |
| `scripts/bash/setup-plan.sh` | Bash 实现 |
| `scripts/powershell/setup-plan.ps1` | PowerShell 实现 |
| `scripts/bash/update-agent-context.sh` | Agent 上下文更新（Bash） |
| `scripts/powershell/update-agent-context.ps1` | Agent 上下文更新（PowerShell） |
| `templates/openapi-template.yaml` | OpenAPI 模板 |

---

## 🎓 总结

`speckit.plan` 是 spec-kit 工作流中的**架构与设计阶段**：

1. **输入**: 来自 spec.md 的功能需求
2. **处理**: 多阶段设计流程（研究 → 架构 → 制品）
3. **输出**: 
   - plan.md (设计决策)
   - openapi.yaml (API 契约)
   - data-model.md (数据与状态)
   - test-case-matrix.md (测试策略)
   - research.md (澄清项解答)
4. **质量**: 多维硬门控（FR 追踪、UDD映射、覆盖率）
5. **后续**: tasks → implement，或 checklist 并行

**关键特性**:
- ✅ 强制性门控，防止不完整设计
- ✅ 追踪驱动 (FR/UC/UDD/CaseID)
- ✅ 多语言支持（中文叙述 + 英文标识符）
- ✅ Agent 上下文自动更新
- ✅ 灵活的契约格式（REST/CLI/custom）

---

*本分析由 Sourcegraph MCP 深度代码分析生成，确保所有引用均基于实际代码库*
