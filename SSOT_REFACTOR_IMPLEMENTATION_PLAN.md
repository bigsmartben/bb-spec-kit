# Spec-Kit SSOT 与职责分离重构实施清单

> 目标：把当前 `script / command / template` 的“分层意识”升级为“可验证的单一来源架构”，降低规则漂移、跨文件重复定义与维护成本。

---

## 1. 重构范围与原则

### 1.1 范围（本轮）

- SDD 核心主链：`/speckit.specify -> /speckit.plan -> /speckit.tasks -> /speckit.implement`
- 三类核心构件：
  - `scripts/`（确定性本地动作）
  - `templates/commands/`（阶段编排）
  - `templates/*-template.*`（产物结构）
- Agent 元数据与派生链：`src/specify_cli/agent_registry.py` 及相关脚本/文档同步点

### 1.2 核心原则（执行约束）

1. **单一来源（SSOT）**：同一规则只允许一个权威来源。
2. **职责分离**：
   - Script 只做确定性 side effect；
   - Command 只做流程编排；
   - Template/Schema 只做产物结构。
3. **可测试一致性**：跨层依赖必须有 CI 自动校验。

---

## 2. 目标架构（落地版本）

新增并固化 3 类“规则层”对象：

1. **Agent Metadata Registry（已存在，继续扩展）**
   - 文件：`src/specify_cli/agent_registry.py`
2. **Workflow Registry（新增）**
   - 文件：`src/specify_cli/workflow_registry.py`
3. **Artifact Schema（新增）**
   - 目录建议：`schemas/`（如 `schemas/spec.schema.yaml`）

并为脚本引入可机读契约：

- `scripts/contracts/*.json`

---

## 3. 分阶段实施计划（建议按 PR 拆分）

## Phase 0：对齐当前行为（低风险，先消除漂移）

**目标**：先把“文档说法”与“脚本真实行为”对齐。

### P0-1：统一 feature 编号策略 SSOT

- 涉及文件：
  - `templates/commands/specify.md`
  - `scripts/bash/create-new-feature.sh`
  - `scripts/powershell/create-new-feature.ps1`（若行为不一致需同步）
- 动作：
  - 明确并固定采用“全局最大编号递增”或“short-name 作用域递增”之一；
  - Command 文档与脚本实现必须一致；
  - 增加测试防回归。

### P0-2：形成《边界声明》文档

- 新增：`docs/architecture/workflow-ssot-boundaries.md`
- 内容：Script / Command / Template 的禁止事项与允许事项。

---

## Phase 1：收敛 Artifact 结构 SSOT

**目标**：让 `*-template`（或 schema）成为结构唯一来源，降低 command 内嵌 schema。

### P1-1：tasks 结构收敛（优先）

- 涉及文件：
  - `templates/tasks-template.md`
  - `templates/commands/tasks.md`
- 动作：
  - 将固定结构（章节、表头、DAG 区块、task line 规则）尽量迁移到 template/schema；
  - `tasks.md` command 保留“如何提取/编排”逻辑，不重复定义结构。

### P1-2：plan 结构收敛

- 涉及文件：
  - `templates/plan-template.md`
  - `templates/commands/plan.md`
- 动作：
  - 将稳定字段标签与章节结构集中在 template/schema；
  - command 仅保留阶段流程与 gate。

### P1-3：引入 Schema（可选但推荐）

- 新增目录：`schemas/`
- 建议最小集：
  - `schemas/spec.schema.yaml`
  - `schemas/plan.schema.yaml`
  - `schemas/tasks.schema.yaml`

---

## Phase 2：脚本契约化（Execution Contract）

**目标**：避免“prompt 描述脚本”与“脚本真实输出”漂移。

### P2-1：新增脚本契约文件

- 新增：
  - `scripts/contracts/create-new-feature.json`
  - `scripts/contracts/setup-plan.json`
  - `scripts/contracts/check-prerequisites.json`
  - `scripts/contracts/update-agent-context.json`

### P2-2：command 前置引用契约

- 涉及：`templates/commands/*.md`
- 动作：在命令文档中引用 contract 字段，不再重复定义输出 key 列表。

---

## Phase 3：Agent 派生链收敛

**目标**：agent 信息“一处登记，多处派生”。

### P3-1：扩展 agent registry 字段

- 文件：`src/specify_cli/agent_registry.py`
- 建议新增字段：
  - `context_file`
  - `skills_dir`
  - `release_enabled`
  - `docs_enabled`

### P3-2：降低 shell/ps 硬编码映射

- 涉及文件：
  - `scripts/bash/update-agent-context.sh`
  - `scripts/powershell/update-agent-context.ps1`
- 动作：通过 Python 导出 metadata（JSON）给脚本消费，减少重复 case/switch。

### P3-3：文档同步改自动校验

- 涉及文件：
  - `README.md`（supported-agent-keys block）
  - 相关测试

---

## Phase 4：CLI 模块拆分（中期）

**目标**：拆解 `__init__.py` 巨石，降低维护复杂度。

### 建议模块

- `src/specify_cli/cli.py`（Typer 注册）
- `src/specify_cli/ui.py`（Banner/Tracker/交互）
- `src/specify_cli/services/init_service.py`
- `src/specify_cli/services/template_service.py`
- `src/specify_cli/services/agent_command_service.py`
- `src/specify_cli/services/git_service.py`

---

## 4. 文件级变更矩阵（第一批）

| 目标 | 关键文件 | 变更类型 | 风险等级 |
|---|---|---|---|
| 统一编号策略 | `templates/commands/specify.md`, `scripts/bash/create-new-feature.sh`, `scripts/powershell/create-new-feature.ps1` | 行为/文档对齐 | 中 |
| 收敛 tasks 结构 SSOT | `templates/tasks-template.md`, `templates/commands/tasks.md` | 结构职责迁移 | 中 |
| 收敛 plan 结构 SSOT | `templates/plan-template.md`, `templates/commands/plan.md` | 结构职责迁移 | 中 |
| 引入脚本 contract | `scripts/contracts/*.json`, `templates/commands/*.md` | 新增契约层 | 中 |
| 收敛 agent 派生链 | `src/specify_cli/agent_registry.py`, `scripts/*/update-agent-context.*`, `README.md` | 跨层统一 | 中-高 |
| 拆分 CLI 巨石 | `src/specify_cli/__init__.py` + 新模块 | 代码结构重组 | 高 |

---

## 5. CI 测试新增计划（必须）

## 5.1 新增测试文件建议

- `tests/test_architecture_consistency.py`
- `tests/test_script_contracts.py`
- `tests/test_artifact_schema_consistency.py`
- `tests/test_workflow_graph_consistency.py`

## 5.2 关键校验项

1. **Agent 一致性**
   - `README` 的 supported-agent-keys 与 `documented_agent_keys()` 一致。
2. **Script Contract 一致性**
   - command frontmatter 引用脚本存在；
   - 脚本 `--json` 输出 key 与 contract 匹配。
3. **Template/Command 边界一致性**
   - command 不得重定义与 template/schema 冲突的结构。
4. **Workflow 链路一致性**
   - `specify -> plan -> tasks -> implement` 输入输出依赖闭环。

---

## 6. 验收标准（Definition of Done）

满足以下条件后，可认定本轮“SSOT 与职责分离重构”完成：

1. 核心阶段（specify/plan/tasks/implement）无跨层规则冲突。
2. 至少 3 个核心脚本已具备 contract 文件并通过一致性测试。
3. `tasks` 与 `plan` 的结构权威来源明确（template/schema），command 不再重复定义。
4. Agent 支持链路中的新增/修改点减少到“registry 优先”。
5. 新增架构一致性测试全部通过。

---

## 7. 推荐 PR 切分（实操）

1. **PR-1（对齐与文档）**：编号策略 + 边界文档 + 最小测试
2. **PR-2（tasks/plan 结构收敛）**：template/schema 与 command 解耦
3. **PR-3（脚本 contract）**：contracts + contract tests
4. **PR-4（agent 派生链）**：registry 扩展 + 脚本降硬编码
5. **PR-5（CLI 拆分）**：`__init__.py` 模块化

每个 PR 均要求：

- 行为不破坏现有主流程；
- 测试覆盖对应变更点；
- 更新 README/CHANGELOG（如涉及用户可见行为）。

---

## 8. 备注

本清单强调“先收敛规则来源，再做代码拆分”。

原因：

- 如果先拆代码、不先锁定 SSOT，漂移会在新模块中复制扩散；
- 先定义规则层和契约层，再模块化，重构风险显著更低。

---

## 9. 本轮已落地（当前仓库状态）

以下事项已在当前仓库完成并通过测试验证：

1. **编号策略对齐（Specify ↔ Script）**
   - `templates/commands/specify.md` 已明确：编号策略由脚本 SSOT 决定，采用全局最大编号递增，不在 command 中重算。

2. **边界文档落地**
   - 新增：`docs/architecture/workflow-ssot-boundaries.md`
   - 明确 Script / Command / Template(Schema) 三层职责与冲突优先级。

3. **结构职责收敛**
   - `templates/commands/tasks.md` 与 `templates/commands/plan.md` 已补充 `Structure SSOT Boundary`。
   - `templates/tasks-template.md` 与 `templates/plan-template.md` 已补充结构 SSOT 注记与骨架约束。

4. **脚本契约文件已新增（核心 4 个）**
   - `scripts/contracts/create-new-feature.json`
   - `scripts/contracts/setup-plan.json`
   - `scripts/contracts/check-prerequisites.json`
   - `scripts/contracts/update-agent-context.json`

5. **命令模板已引用脚本契约**
   - `templates/commands/specify.md`
   - `templates/commands/plan.md`
   - `templates/commands/tasks.md`
   - `templates/commands/implement.md`

6. **一致性测试已新增并通过**
   - 新增测试：`tests/test_script_contracts.py`
   - 增强测试：`tests/test_speckit_commands.py`
   - 当前验证结果：`111 passed`

7. **Phase 3 最小落地（只读一致性校验）已完成**
   - `tests/test_script_contracts.py` 新增：
     - `test_update_agent_context_allowed_agent_types_matches_registry_and_scripts`
   - 校验内容：
     - `scripts/contracts/update-agent-context.json` 的 `allowed_agent_types`
     - `scripts/bash/update-agent-context.sh` 的 `update_specific_agent` case labels
     - `scripts/powershell/update-agent-context.ps1` 的 `Update-SpecificAgent` switch labels
     三者保持一致；并且该集合是 `agent_registry` 导出的 CLI agent key 子集。
   - 当前约束说明：`update-agent-context` 现阶段未维护 Cline 专用 context 文件，因此断言允许相对 registry 存在 `cline` 的已知差异。
   - 当前验证结果（专项）：
     - `pytest -q tests/test_script_contracts.py tests/test_agent_consistency.py`
     - `13 passed`
