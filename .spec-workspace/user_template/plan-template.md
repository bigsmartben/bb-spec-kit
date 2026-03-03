# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [spec.md](./spec.md)

---

## Summary

### Feature Overview（功能Overview（概述））

[简要描述本次功能的核心价值和业务目标，2-3 句话说明白]

### Key Changes（关键变更点）

- **新增**: [列举主要新增的模块/接口]
- **修改**: [列举主要修改的模块/接口]
- **删除**: [列举主要删除的模块/接口]

### Success Criteria（成功标准）

- [ ] [可量化的验收标准 1]
- [ ] [可量化的验收标准 2]
- [ ] [可量化的验收标准 3]

---

## Constitution Check

*GATE: Must pass before Phase 0. Re-check after Phase 4 design.*

### Propagation Consistency Check（传递一致性检查）（Spec → Plan）

- [ ] 术语一致性: Plan 术语在 Spec §7.1 有定义
- [ ] ID 追溯一致性: Story / SC / F 映射在 Spec §2、§4、§6 中一致且可追溯
- [ ] 状态流转一致: 与 Spec §3 状态机图及“状态与功能需求追溯表”一致
- [ ] 接口契约一致: 与 Spec §4 功能需求一致
- [ ] Field Specification 覆盖完整性: `contracts/api.contract-table.md` 对 Spec §4 每个功能的 Field Specification（字段规格）表逐行映射，无缺项

> ⚠️ **冻结后变更管控**：若 Spec 的 Field Specification 在 Phase 1 完成后发生变更，必须回退并重走 Phase 1（更新 `contracts/api.contract-table.md` 等产物），随后重新生成冻结上下文（如 `ai-view-context.xml`）。禁止带旧冻结上下文进入后续阶段。

### Dependency Validity Check（依赖合法性检查）

- [ ] 组件依赖图无环（ArchUnit 验证）
- [ ] 分层约束符合 memory/constitution.md §4
- [ ] 对象分离到位（DTO/VO/Entity/PO），符合 memory/constitution.md §4 对象边界约束

---

## Technical Context

### Context Compression (Required)

> 只写本次差异,不重复抄录全量上下文。

```text
CTX: {LANGUAGE} {VERSION}; {RUNTIME_FRAMEWORK}; {BUILD_TOOL}; {STORAGE_STRATEGY}; {TEST_FRAMEWORK}
REF: memory/constitution.md §2-§8
DELTA: {仅列出本次变更项}
```

---

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md                         # This file (总控台)
├── architecture.md                 # Phase 0: 架构与术语口径
├── contracts/
│   ├── api.contract-table.md       # Phase 1: 字段表 SSoT
│   ├── api.openapi.yaml            # Phase 1: 可选导出视图
│   ├── ux.flow.md                  # Phase 2: 交互主链路（Mermaid flowchart）
│   ├── smoke-tests.md              # Phase 2: 主链路 Smoke 用例
│   ├── I-001-*.md                  # Phase 5: Interface Design（接口设计）
│   └── I-002-*.md                  # Phase 5: Interface Design（接口设计）
├── research.md                     # Phase 3: 技术研究（完备性检查、服务级时序、技术结论）
├── data-model.md                   # Phase 4: 类模型 + Logical Schema（非 DDL）
├── test-matrix.md                  # Phase 4: 全量测试矩阵
└── tasks.md                        # Post-Plan output (/speckit.tasks)
```

---

## Phase 0: Architecture Design and Terminology Baseline（架构设计与术语口径） (Architecture)

### Goal（目标）

建立本功能的分层边界、模块拓扑与领域对象口径（VO/DTO/Entity/PO），作为后续各阶段的统一前置约束。

### Outputs（输出产物）

- `architecture.md` — 架构约束与组件图

### Execution Checks（执行检查）

- [ ] 固化 VO/DTO/Entity/PO 定义、分层归属与转换边界
- [ ] 输出模块/子系统粗粒度组件图（Mermaid）
- [ ] 与 `memory/constitution.md §4` 对齐，无循环依赖

---

## Phase 1: Interface Contract SSoT（接口契约主源） (Contract SSoT)

### Goal（目标）

将 `spec` 的用户操作 / 系统交互映射为字段级接口 Contract SSoT（唯一真相源），并在需要时导出 OpenAPI 视图。

### API Inventory

> **SSoT**: [contracts/api.contract-table.md](./contracts/api.contract-table.md) — 接口字段语义 Single Source of Truth（唯一真相源）。
> **Optional View**: [contracts/api.openapi.yaml](./contracts/api.openapi.yaml) — 可选导出，不得反向成为主源。

| Interface ID | Method | Type | Purpose | Layer | Status | Spec Link |
|--------------|--------|------|---------|-------|--------|-----------|
| I-001 | POST | API | [用途] | Adapter | 🆕 New | F-001 |
| I-002 | GET | Query | [用途] | Provider | ⚠️ Modified | F-002 |

### Outputs（输出产物）

- `contracts/api.contract-table.md` — 字段级 Contract SSoT
- `contracts/api.openapi.yaml` — 可选导出视图

### Execution Checks（执行检查）

- [ ] 分析 `spec.md`（重点 §4、§6、§7.4），识别所有用户操作 / 系统交互 → 在 API Inventory 中定义接口清单
- [ ] 基于 Spec §4 Field Specification 与可见数据规则，生成 Contract SSoT → `contracts/api.contract-table.md`
- [ ] 对比现有 VO 层并标注字段 `存量/新增`
- [ ] 可选导出 OpenAPI → `contracts/api.openapi.yaml`（若导出则必须与字段表一致）

---

## Phase 2: Interaction Main Flow and Smoke Validation（交互主链路与冒烟验证） (UX Flow + Smoke)

### Goal（目标）

先固化可执行的用户交互主链路，再以 Smoke 用例验证“最小可跑通”闭环。

### Outputs（输出产物）

- `contracts/ux.flow.md` — Mermaid `flowchart` 主链路
- `contracts/smoke-tests.md` — 主链路 Smoke 用例

### Execution Checks（执行检查）

- [ ] `ux.flow.md` 使用 Mermaid `flowchart`，覆盖核心用户步骤/系统交互
- [ ] 接口节点引用 Interface ID 与字段表关键字段
- [ ] 每条主链路至少 1 条 Happy Path + 1 条关键失败路径 Smoke
- [ ] Smoke 用例与流程节点双向可追溯

---

## Phase 3: Technical Research and Feasibility（技术预研与可行性） (Research)

### Goal（目标）

基于契约主源、交互主链路与 Smoke 结果进行完备性检查与技术可行性探索。

### Outputs（输出产物）

- `research.md` — 技术预研报告

### Execution Checks（执行检查）

- [ ] **时序图推理（服务级别）**：复杂或外部集成链路输出宏观时序验证
- [ ] **CRUD/完备性检查**：对比字段表契约与现有代码，确认上下文字段与行为完整性
- [ ] **技术结论输出**：针对性能、核心算法、中间件给出明确选型与可行性结论
- [ ] *(注意：不包含直接修改表结构/DDL的内容)*

---

## Phase 4: Model Design and Full Test Matrix（模型设计与全量测试） (Data Model + Full Test Matrix)

### Goal（目标）

完成类模型/状态模型与逻辑表结构（非 DDL）定义，并产出全量测试矩阵。

### Outputs（输出产物）

- `data-model.md` — Class Model（类模型） + Logical Schema（非 DDL）
- `test-matrix.md` — 全量测试矩阵

### Execution Checks（执行检查）

- [ ] **时序图推理（组件级别）**：补充组件之间交互时序
- [ ] **UML 类图**：核心属性与关系定义
- [ ] **状态迁移细化**：将 spec 状态机映射到类字段/方法
- [ ] **Logical Schema**：列/类型/索引/约束为逻辑表达，禁止可执行 DDL
- [ ] **全量测试矩阵**：覆盖状态机、功能需求、接口自动化、追溯关系

---

## Phase 5: Interface Design（Interface Design（接口设计））

### Goal（目标）

形成 Coding 前最小颗粒度设计，作为实现阶段直接输入。

### Outputs（输出产物）

- `contracts/I-XXX-*.md` — 每个接口的详细设计文档

### Execution Checks（执行检查）

- [ ] **源头引用**：消费 `data-model.md` 类定义，采纳 `research.md` 结论
- [ ] **契约还原**：以字段表为主源（必要时参考 OpenAPI 导出）
- [ ] **时序图推理（类级别）**：细化到类与方法调用
- [ ] **伪代码逻辑编写**：包含接口核心实现步骤

---

## Execution Plan（执行计划）

```yaml
plan:
  id: [plan-id-001]

  steps:
    - step_id: step-00
      title: "Phase 0: 架构设计与术语口径 (Architecture)"
      output: architecture.md

    - step_id: step-01
      title: "Phase 1: 接口契约主源 (Contract SSoT)"
      output: contracts/api.contract-table.md (+ optional api.openapi.yaml)

    - step_id: step-02
      title: "Phase 2: 交互主链路与冒烟验证 (UX Flow + Smoke)"
      output: contracts/ux.flow.md, contracts/smoke-tests.md

    - step_id: step-03
      title: "Phase 3: 技术预研与可行性 (Research)"
      output: research.md

    - step_id: step-04
      title: "Phase 4: 模型设计与全量测试 (Data Model + Full Test Matrix)"
      output: data-model.md, test-matrix.md

    - step_id: step-05
      title: "Phase 5: Interface Design（接口设计）"
      output: contracts/I-XXX-*.md

  dependencies:
    - step-01 依赖 step-00 完成
    - step-02 依赖 step-01 完成
    - step-03 依赖 step-01、step-02 完成
    - step-04 依赖 step-01、step-03 完成
    - step-05 依赖 step-01、step-03、step-04 完成
```

---

## Context Dependency Matrix（上下文依赖矩阵） (Context Dependency Matrix)

| Phase | LoadRequired（必须加载） | Produce（产出） |
|-------|----------------|----------------|
| Phase 0 架构设计 | spec.md, memory/constitution.md | architecture.md |
| Phase 1 接口契约主源 | spec.md（重点 §4、§6、§7.4）, architecture.md | api.contract-table.md, API Inventory, (optional) api.openapi.yaml |
| Phase 2 交互+冒烟 | spec.md §2, api.contract-table.md | ux.flow.md, smoke-tests.md |
| Phase 3 技术研究 | spec.md §7.2, api.contract-table.md, ux.flow.md, smoke-tests.md, 代码库 | research.md |
| Phase 4 模型+全量测试 | spec.md §3（含状态与功能追溯）, api.contract-table.md, research.md | data-model.md, test-matrix.md |
| Phase 5 接口详设 | api.contract-table.md, (optional) api.openapi.yaml, data-model.md, research.md, test-matrix.md | contracts/I-XXX-*.md |

---

**Note**: 本模板由 `/speckit.plan` 命令填充。详见 `.specify/templates/commands/plan.md`
