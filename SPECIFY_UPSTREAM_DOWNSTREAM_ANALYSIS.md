# Specify 指令完整上下游分析

## 概述

`/speckit.specify` 是 Spec-Driven Development (SDD) 工作流的**第一阶段指令**。它将用户的自然语言特性描述转化为结构化的功能规范，为后续的规划、任务分解和实现阶段奠定基础。

---

## 1. Specify 指令的位置与角色

```
                     ┌─────────────────────┐
                     │  User Feature Idea  │
                     │  (Natural Language) │
                     └──────────┬──────────┘
                                │
                                ▼
          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
          ┃   1️⃣  /speckit.specify           ┃
          ┃   Transform to Structured Spec   ┃
          ┗━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━┛
                       │
              ┌────────┴────────┐
              ▼                 ▼
    ✅ spec.md         📋 requirements.md
   (SSOT for           (Quality Checklist)
    requirements)
              │
              ├────→ /speckit.clarify (optional refinement loop)
              │
              └────→ /speckit.plan (Phase 2: Technical Planning)
                     └─────────────────→ More downstream stages
```

---

## 2. 上游输入源（Upstream Inputs）

### 2.1 直接输入

| 输入 | 来源 | 格式 | 说明 |
|------|------|------|------|
| **用户描述** | `/speckit.specify <feature-description>` | 自然语言文本 | 用户在 AI Agent 中输入的特性描述，例如："Build a chat system with real-time messaging and user presence" |
| **Git 仓库上下文** | 当前 Git 仓库 | Git refs | 用于检测现有分支号和特性编号（自动编号规则） |
| **规范模板** | `templates/spec-template.md` 或 `.specify/templates/spec-template.md` | Markdown | 规范的结构和必填章节定义 |
| **质量检查清单模板** | `templates/checklist-template.md` | Markdown | 用于验证规范质量的检查项模板 |

### 2.2 可选输入

| 输入 | 来源 | 格式 | 说明 |
|------|------|------|------|
| **项目宪法** | `.specify/memory/constitution.md` 或 `memory/constitution.md` | Markdown | 项目治理原则、术语定义、数据分层规则（UDD → VO → Persistence）— **强烈推荐首先运行 `/speckit.constitution`** |
| **PRD 文档**（可选） | Markdown、Word、TXT 等 | 多格式 | 用户可能提供的产品需求文档（需用 `/speckit.prd2spec` 进行转换） |

### 2.3 前置条件（Prerequisites）

1. **Git 仓库已初始化**：`git init` 或工作于已存在的 Git 仓库
2. **Spec-Kit 已启动化**：已运行 `specify init` 以部署模板和命令文件到 Agent 文件夹
3. **宪法优先**（推荐）：在第一次运行 `speckit.specify` 前，应先运行 `/speckit.constitution` 以建立术语权威和数据模型约定

---

## 3. Specify 指令的内部处理流程

### 3.1 脚本执行链

**触发脚本**：`scripts/bash/create-new-feature.sh` 或 `scripts/powershell/create-new-feature.ps1`

#### 执行步骤：

```mermaid
flowchart TD
    A["用户输入通过 AI Agent"] -->|via {SCRIPT}| B["create-new-feature.sh / .ps1"]
    B -->|Step 1| C["生成简短名称<br/>short-name"]
    C -->|Step 2a| D["Git 获取最新分支<br/>git fetch --all --prune"]
    D -->|Step 2b| E["扫描三个来源查找最高编号:<br/>1. 远程分支 (refs/heads/NNN-short-name)<br/>2. 本地分支<br/>3. specs/ 目录"]
    E -->|Step 2c| F["计算下一个分支编号<br/>next-num = max-found + 1"]
    F -->|Step 2d| G["创建分支并运行脚本<br/>git checkout -b NNN-short-name<br/>mkdir -p specs/NNN-short-name/"]
    G -->|JSON Output| H["返回 JSON 对象\n{<br/>  BRANCH_NAME: string<br/>  SPEC_FILE: path<br/>  FEATURE_DIR: path<br/>}"]
    H -->|AI Agent 处理| I["加载规范模板"]
    I -->|可选| J["加载宪法（术语权威）"]
    J --> K["填充规范结构"]
    K -->|输出| L["写入 spec.md"]
    L -->|创建| M["创建 checklists/requirements.md<br/>质量检查清单"]
    M -->|完成| N["✅ Specify 阶段完成<br/>可继续 clarify 或 plan"]
```

#### 脚本输出结构：

```json
{
  "BRANCH_NAME": "005-user-authentication",
  "SPEC_FILE": "/repo/specs/005-user-authentication/spec.md",
  "FEATURE_DIR": "/repo/specs/005-user-authentication",
  "CHECKLIST_FILE": "/repo/specs/005-user-authentication/checklists/requirements.md"
}
```

### 3.2 AI Agent 填充规范的关键规则

#### 必须遵循的约定（Output Language & Stability Contract）

| 规则 | 详情 |
|------|------|
| **默认输出语言** | 简体中文 (zh-CN)，除了保留元素外 |
| **保留元素** | `FR-###`, `UC-###`, `Entity.field`, `MUST/SHOULD/MAY`, `[NEEDS CLARIFICATION: ...]`, 代码段中的任何内容 |
| **结构稳定性** | 保留 spec-template.md 的章节顺序和标题，仅填充内容 |
| **占位符替换** | 所有 `[Placeholder]` 必须被具体内容替换或标记为 `[NEEDS CLARIFICATION: ...]`（最多 3 个） |
| **无歧义** | 无法确定时，使用知情推测（informed guesses）；只有在多种合理解释且影响不同时才标记为 NEEDS CLARIFICATION |

#### 关键生成逻辑：

1. **短名称生成**（2-4 词，kebab-case）
   - 从用户描述提取关键词
   - 例：`"I want to add OAuth2"` → `"oauth2-integration"`

2. **功能需求编号**（`FR-001`, `FR-002`, ...）
   - 每个需求必须包含：
     - `Capability`：系统 MUST/SHOULD/MAY... 的单句描述
     - `Given/When/Then`：最小可测试行为
     - `UDD 引用`：该需求涉及的用户可见数据 (`Entity.field`)
     - `故障处理`：至少一个失败条件

3. **UI 数据字典（UDD）定义**（如有用户可见信息）
   - 定义每个 `Entity.field`：
     - `User-visible meaning`：用户看到的含义
     - `Calculation/criteria`：业务计算方式或来源
     - `Boundaries & null rules`：边界和空值规则
     - `Display rules`：格式化、标签、颜色等
     - `Source Type`：`System-backed` 还是 `UI-local`
     - `Key Path`：`P1/P2/P3/N/A`（优先级）

4. **用例（UC）结构**（如适用）
   - Primary Actor / Preconditions / Main Flow / Postconditions

5. **成功标准**（Success Criteria）
   - 可量化的、技术无关的结果

---

## 4. Specify 指令的输出（Outputs）

### 4.1 主要产物

| 产物 | 文件路径 | 说明 |
|------|---------|------|
| **规范文档** | `specs/{NNN-short-name}/spec.md` | **单一信息源 (SSOT)** 包含所有需求、用户场景、UDD 定义、成功标准、验收使用场景等 |
| **质量检查清单** | `specs/{NNN-short-name}/checklists/requirements.md` | 用于验证规范完整性和质量的检查清单 |
| **Git 分支** | `{NNN-short-name}` | 新的特性分支，所有下游工作在此分支上进行 |

### 4.2 spec.md 的标准章节结构

根据 `templates/spec-template.md` 定义：

```markdown
# Feature Specification: [FEATURE_NAME]

## Artifacts Overview & Navigation (mandatory)
  - 导航表：本阶段输出 + 下游计划输出

## § 1 Global Context (mandatory)
  ### 1.1 Actors
    表：Actor 类型、权限、备注
  ### 1.2 System Boundary
    In Scope / Out of Scope 列表
  ### 1.3 UI Data Dictionary (UDD)
    表：Entity.field 定义（含 Source Type、Key Path）

## § 2 UC Overview (mandatory)
  表：UC ID、描述、主要 Actor、关系类型、优先级

## § 3 Detailed Requirements (mandatory)
  ### 3.1 User Scenarios & Testing
    每个 UC 的事件流、前置条件、后置条件
  ### 3.2 Acceptance Scenarios
    具体的 Given/When/Then 场景
  ### 3.3 Functional Requirements
    FR-001, FR-002, ... 每个条目：
    - Capability
    - Given/When/Then
    - UDD references (Reads/Displays, Writes/Updates)
    - Failure / edge behavior

## § 4 Non-Functional Attributes (optional)
  Performance, Security, Scalability, Accessibility, etc.

## § 5 Success Criteria & Measurables
  列表：可验证的成功标准

## § 6 Out-of-Scope & Future Considerations
  注明后续路线图中的相关项

## Clarifications *(populated by /speckit.clarify)*
  Session YYYY-MM-DD
  - 澄清问题和答案的记录
```

### 4.3 requirements.md（质量检查清单）

```markdown
# Specification Quality Checklist: [FEATURE_NAME]

## 检查项目

- [ ] 所有 [NEEDS CLARIFICATION] 已解决
- [ ] 每个 FR-### 都有可测试的 Given/When/Then
- [ ] UDD 条目都定义了 Source Type 和 Key Path
- [ ] 系统边界明确（In Scope vs Out of Scope）
- [ ] 没有遗留的占位符 [...]
- [ ] 与宪法术语一致
- ... (更多检查项)
```

---

## 5. Specify 的下游指令（Downstream Commands）

### 5.1 直接下游（Direct Consumers）

```
spec.md (Specify Output)
    │
    ├──→ /speckit.clarify (可选：澄清不明确之处)
    │   └──→ 更新 spec.md + Clarifications 章节
    │
    ├──→ /speckit.plan (推荐：生成技术计划)
    │   ├── Input: spec.md
    │   ├── Process: 选择技术栈、生成设计制品
    │   └── Output: plan.md, research.md, openapi.yaml, data-model.md, test-case-matrix.md, quickstart.md
    │
    └──→ /speckit.prd2spec (可选反向输入：PRD → Spec 转换)
        ├── Input: PRD 文档
        └── Output: 更新现有 spec.md（增量模式）
```

### 5.2 完整工作流链

```
1. /speckit.constitution        → constitution.md (项目治理 + 术语权威)
   ↓
2. /speckit.specify             → spec.md + requirements checklist
   ↓
3. /speckit.clarify (可选)      → spec.md (澄清问题 + 答案)
   ↓
4. /speckit.plan                → plan.md + 5 个设计制品
   ├── Phase 0: research.md (解决所有 NEEDS CLARIFICATION)
   ├── Phase 1: 设计制品生成
   │   ├── openapi.yaml (API 契约，覆盖所有 FR)
   │   ├── data-model.md (数据模型 + FSM)
   │   ├── test-case-matrix.md (测试矩阵)
   │   └── quickstart.md
   └── Phase 2: 更新 Agent 上下文
   ↓
5. /speckit.tasks               → tasks.md + interface-details/*.md
   └── 基于 plan.md + data-model.md 生成任务和接口细节
   ↓
6. /speckit.implement (可选)    → 执行所有分解的任务
   ↓
7. /speckit.analyze (可选)      → 项目一致性分析
```

### 5.3 Specify 的关键输出被下游消费的方式

#### Plan 的消费：

| Plan 消费的 Spec 元素 | 用途 |
|---|---|
| `FR-###` ID 列表 | FR 覆盖率门控：每个 FR 必须映射到至少一个 OpenAPI operation 的 `x-fr-ids` |
| `UC-###` 和事件流 | 用例覆盖率和场景驱动的测试矩阵 |
| `Entity.field` (UDD) | 生成 VO（Value Objects）覆盖表：Key Path + System-backed UDD Items 必须被完整映射 |
| `Out of Scope` 声明 | 设计时排除不在范围的项 |
| `Success Criteria` | 验收测试的基础 |

#### Tasks 的消费：

| Tasks 消费的元素 | 来源 |
|---|---|
| 用户故事优先级 | `spec.md § 2 UC Overview` 中的 Priority 列 |
| UDD 项清单 | `spec.md § 1.3` |
| 接口映射 | `plan.md` 中的 `contracts/openapi.yaml` 的 `operationId` |

#### 质量门控：

Clarify 阶段会反复引用 spec.md 中的：
- 功能范围的歧义
- 数据模型不清晰的部分
- 用户流程中的缺失步骤
- 非功能属性的不足

---

## 6. 与其他指令的关系

### 6.1 Constitution 指令的角色

```
Constitution (治理 + 术语权威)
       ↓
    术语定义 (Terminology)
    数据分层规则 (Layering: UDD → VO → Persistence)
    架构证据索引 (Architecture Evidence Index: AEI-###)
       ↓
    被 Specify 引用
    ├── 填充 UDD 定义时遵循分层
    ├── 术语一致性检查（避免同义词）
    └── （可选）Architecture Evidence Index 用于
        下游的 Plan + Tasks 中引用现有架构边界
```

**关键约束**：
- Specify 必须遵守 Constitution 中定义的术语和数据分层规则
- 如果 Constitution 中未定义某个术语，Specify 可在 UDD 中定义（并标注来源）
- Specify 输出不应与 Constitution 矛盾

### 6.2 Clarify 指令的作用

```
Clarify = Specify 的可选迭代改进
├── Input: 现有 spec.md
├── Process: 提问最多 20 个高针对性问题
│   └── 每个问题必须是多选或短答题
├── Output: spec.md（更新或补充）+ Clarifications 章节
└── 决策权：由用户回答问题，Agent 向下游推进
```

**触发时机**：
- `spec.md` 中标记过 3 个或更多 `[NEEDS CLARIFICATION]` 项
- 用户显式请求 `/speckit.clarify`
- 自动检测到功能范围或数据模型模糊

**不应该做**：
- Clarify 不应修改 Specify 生成的核心结构（§1-§5）
- 只添加 `## Clarifications` 章节和更新现有内容的细节
- 不应创建新的 FR-###

---

## 7. Handoffs（切换点）

### 7.1 从 Specify 出发的 Handoffs（在模板中定义）

```yaml
handoffs: 
  - label: "Build Technical Plan"
    agent: speckit.plan
    prompt: "Create a plan for the spec. I am building with..."
    send: false  # 默认不自动跳转；用户可点击

  - label: "Clarify Spec Requirements"
    agent: speckit.clarify
    prompt: "Clarify specification requirements"
    send: true   # 自动跳转（如用户同意）
```

### 7.2 典型工作流情景

**情景 A：用户自信地描述需求**
```
/speckit.specify → spec.md ✅ 
                 → (直接跳转) 
                 → /speckit.plan
```

**情景 B：需求存在歧义**
```
/speckit.specify → spec.md (有 NEEDS CLARIFICATION 标记)
                 → (用户选择) 
                 → /speckit.clarify → 澄清问答
                 → (更新的 spec.md)
                 → /speckit.plan
```

**情景 C：从 PRD 迭代**
```
有现有 spec.md
      ↓
/speckit.prd2spec (新 PRD 或更新的 PRD)
      ↓
更新或增量修改 spec.md
      ↓
/speckit.plan
```

---

## 8. 关键质量门控与约束

### 8.1 Specify 必须满足的条件（硬规则）

| 门控 | 检查 | 失败后果 |
|------|------|---------|
| **无遗留占位符** | 所有 `[...]` 必须被替换或标记为 NEEDS CLARIFICATION | Plan 阶段会发现并要求返回修正 |
| **NEEDS CLARIFICATION ≤ 3** | 最多 3 个未解决的澄清标记 | 超过时，强制触发 Clarify 阶段 |
| **FR 可测试性** | 每个 `FR-###` 都有 Given/When/Then | Plan 中的 Test Matrix 覆盖率门控会卡住 |
| **UDD 完整性** | 每个用户可见字段都在 UDD 中定义 | VO 覆盖表生成时会发现遗漏 |
| **系统边界明确** | § 1.2 的 In/Out of Scope 列表非空 | Plan 的范围检查会标记为 ERROR |
| **用户流清晰** | § 3.1 User Scenarios 有具体事件序列 | 无法生成有意义的任务分解 |

### 8.2 Specify 与 Constitution 的一致性检查

Specify 应在完成时交叉验证：
- ✅ 术语使用与 Constitution 中的定义一致（或明确标注新术语来源）
- ✅ UDD 分层遵守 Constitution 中的 UDD → VO → Persistence 规则
- ✅ 数据模型约束与 Constitution 中的 Domain Model 规则兼容

---

## 9. 常见使用模式与反模式

### 9.1 👍 推荐做法

```markdown
1. 优先运行 constitution 以建立术语权威和数据分层规则

2. 第一次运行 specify 时，提供清晰、具体的特性描述
   示例 ✅："Build a profile page showing user name, avatar, 
             followed/follower counts, and a bio that users 
             can edit inline. User must be logged in to view/edit."
   
   反例 ❌："Build user profiles" (太模糊)

3. 对复杂特性运行 clarify，直到 NEEDS CLARIFICATION ≤ 3

4. 在 plan 之前审查 spec.md 的质量检查清单

5. 使用 constitution 中定义的术语和 UDD 层次结构

6. 为每个 FR-### 定义明确的 UDD 引用（哪些字段涉及、是 Reads 还是 Writes）
```

### 9.2 ❌ 避免的反模式

| 反模式 | 为什么避免 | 正确做法 |
|--------|----------|--------|
| 不运行 constitution 就直接 specify | UDD 分层和术语不一致 | 总是先运行 constitution |
| 在 spec.md 中混用英文和中文术语 | 下游任务分配和验收测试混淆 | 遵守 Output Language Contract |
| FR-### 没有 Given/When/Then | Plan 的测试矩阵无法生成 | 每个 FR 都添加最小可测试行为 |
| UDD 项未标记 Key Path 或 Source Type | VO 覆盖表出现遗漏，导致数据模型不完整 | 使用模板中的表格，填满所有列 |
| Specify 完成后立即 Plan，跳过 Clarify | 发现歧义的时间推后到 Plan 或 Tasks 阶段 | 如有 NEEDS CLARIFICATION，先 clarify |
| 手工修改已生成的 spec.md 而不用 clarify | 破坏 Clarifications 章节的跟踪和 trace | 用 /speckit.clarify 进行迭代 |
| 假设 spec.md 中的措辞"足够清晰"而无用户确认 | 计划和实现中的假设偏差 | 显式推荐对关键假设进行 clarify |
```

---

## 10. 技术细节：Specify 脚本的分支编号机制

### 10.1 编号规则（确定性）

```bash
# 三个来源的最高编号搜索
1. 远程分支 (git ls-remote)
   匹配：refs/heads/NNN-short-name
   
2. 本地分支 (git branch)
   匹配：^[* ]*NNN-short-name$
   
3. specs 目录
   匹配：specs/NNN-short-name/

# 选择最高 NNN，加 1 作为新编号
next-num = max(remote, local, specs) + 1
```

### 10.2 短名称生成规则

- 2-4 个英文单词，用连字符连接
- 偏好动词-名词格式：`add-user-auth`, `fix-payment-timeout`
- 保留技术术语和缩写：`oauth2-api-integration`, `kafka-consumer`
- 示例：
  ```
  "Add OAuth2 integration for the API"     → oauth2-api-integration
  "Fix payment processing timeout bug"    → fix-payment-timeout
  "Create analytics dashboard"            → analytics-dashboard
  "Support real-time notifications"       → realtime-notifications
  ```

### 10.3 分支名称和文件结构

```
新分支名称：005-user-authentication
新规范目录：specs/005-user-authentication/
规范文件：  specs/005-user-authentication/spec.md
清单文件：  specs/005-user-authentication/checklists/requirements.md
计划文件：  specs/005-user-authentication/plan.md (created by /speckit.plan)
```

---

## 11. 相关文件清单

### 11.1 Specify 指令核心文件

| 文件 | 用途 | 修改权限 |
|------|------|--------|
| `templates/commands/specify.md` | Specify 指令定义（AI Agent 执行指南） | 只限指令逻辑修改 (bbspec-skill Type A) |
| `templates/spec-template.md` | Spec 输出的标准模板 | 只限模板结构修改 (bbspec-skill Type A) |
| `templates/checklist-template.md` | 质量检查清单的模板 | 只限清单检查项修改 |
| `scripts/bash/create-new-feature.sh` | 分支创建和路径生成脚本 | 需 bash/PowerShell 同步修改 |
| `scripts/powershell/create-new-feature.ps1` | PowerShell 版分支脚本 | 需与 bash 同步 |

### 11.2 依赖关系

```
specify.md
├── 调用 → create-new-feature.sh (脚本生成分支和路径)
├── 加载 → spec-template.md (产物模板)
├── 加载 → checklist-template.md (质量检查)
├── 读取 → constitution.md (术语权威和数据分层)
└── 输出 → spec.md (与下游 clarify/plan 共享)

clarify.md
├── 读取 → spec.md (Specify 的输出)
└── 更新 → Clarifications 章节（增量追加）

plan.md
├── 读取 → spec.md (需求和 UDD)
├── 读取 → constitution.md (术语和分层)
└── 输出 → plan.md + 5 个设计制品
```

---

## 12. 调试与故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| "分支已存在"错误 | 相同 short-name 的分支已被创建过 | 使用不同的 short-name，或使用现有分支 |
| spec.md 没有生成 | 脚本输出解析失败 | 检查 JSON 输出格式，确保 --json 标志正确 |
| "Cannot find constitution.md" 警告 | 宪法文件未创建 | 先运行 /speckit.constitution（推荐但非强制） |
| NEEDS CLARIFICATION 过多（>3） | 用户描述过于模糊 | 向用户提示运行 /speckit.clarify |
| Plan 阶段失败，FR 覆盖率不足 | Specify 阶段的 FR-### 不完整 | 返回 Specify，补充遗漏的需求 |

---

## 13. 总结与检查清单

### 13.1 Specify 上下游检查清单

- [ ] **上游**：Constitution 已创建并定义了术语和数据分层规则
- [ ] **输入**：用户提供了清晰、具体的特性描述
- [ ] **执行**：Specify 指令已生成 spec.md 和 requirements 清单
- [ ] **质量**：spec.md 中的占位符全部替换，NEEDS CLARIFICATION ≤ 3
- [ ] **验证**：Spec 与 Constitution 的术语一致
- [ ] **下一步**：根据澄清需求选择 Clarify 或直接 Plan

### 13.2 Specify 输出物交付标准

```markdown
✅ spec.md 完成标志
   - 无 [...] 占位符（除已解决的 NEEDS CLARIFICATION）
   - 每个 FR-### 都有 Given/When/Then
   - UDD 项都有 Source Type + Key Path + 显示规则
   - 系统边界明确且完整
   - 与 Constitution 术语一致

✅ requirements.md 完成标志
   - 清单项全部填充
   - 与 spec.md 内容对应
   - 可作为质量审查的 checklist

✅ 分支和文件结构
   - 新分支 {NNN-short-name} 已创建
   - specs/{NNN-short-name}/spec.md 存在
   - specs/{NNN-short-name}/checklists/requirements.md 存在
```

---

## 参考文献

- [Spec-Kit 官方文档](README.md)
- [Spec-Driven Development 概述](spec-driven.md)
- [快速开始指南](docs/quickstart.md)
- [bbspec-skill：精准修改指南](.agents/skills/bbspec-skill/SKILL.md)
- [AGENTS.md：Agent 支持和集成](AGENTS.md)

---

**最后更新**: 2026-03-05  
**分析者**: GitHub Copilot  
**状态**: 完成与验证
