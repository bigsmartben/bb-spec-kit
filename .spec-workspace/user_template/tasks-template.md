# Task Breakdown and Execution Plan（任务拆解与Execution Plan（执行计划））: [FEATURE]

**Plan**: [plan.md](./plan.md) | **Date**: [DATE]

---

## Overview（概述）

本文档将规范驱动开发（SDD）前置设计阶段（Plan Phase 0-5）的产物拆解为可被实施代理或人类执行的原子工单。

### Gate Conditions（门禁条件） (Gate)
必须在 `plan.md` 标注的所有 Phase（0-5）都通过验收后，方可生成此任务列表。

---

## Task Type Mapping（任务类型映射） (Task Type Mapping)

| TaskType（任务类型） | RequiredPlanArtifacts（依赖Plan核心产物） | TaskGoal（任务目标） |
| :--- | :--- | :--- |
| **[Setup] 项目初始化/公共准备** | Phase 0-1: `architecture.md` + `contracts/api.contract-table.md` | 初始化项目基础结构、依赖与通用配置，确保后续接口任务可执行。 |
| **[RESEARCH] 预研验证任务** | Phase 3: `research.md` | 执行预研结论中的验证项，确认高风险方案可行并形成可执行基线。 |
| **[AutoTest] 自动化测试实现** | Phase 4: `test-matrix.md` + Phase 5: `contracts/I-XXX-*.md §4` | 先实现接口对应 ST-XXX / E2E-XXX / Mock 测试，形成可执行验证门禁。 |
| **[Impl] 接口逻辑开发** | Phase 5: `contracts/I-XXX-*.md` + Phase 4: `data-model.md` | **核心阶段**。严格按接口详设与数据模型完成业务实现，并以 `[AutoTest]` 通过作为完成标准。 |
| **[Refactor] 收敛与优化（可选）** | Phase 5 实现结果 + 测试结果 | 在不改变外部行为的前提下优化可维护性，并保持全量测试通过。 |

---

## Task Inventory

> **Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `test-matrix.md`, `contracts/I-XXX-*.md`, `contracts/api.contract-table.md`（若存在 `contracts/` 则需要；可选：`contracts/smoke-tests.md`）

| Task ID | Interface ID | Type | Priority | Dependencies | Est. Time | Required Inputs (SSoT) |
|---------|--------------|------|----------|--------------|-----------|------------------------|
| T-S01   | ALL          | [Setup]    | P0 | None          | 1h | `architecture.md`、`contracts/api.contract-table.md` |
| T-RES01 | ALL          | [RESEARCH] | P0 | T-S01         | 1h | `research.md` |
| T-001   | I-001        | [AutoTest] | P0 | T-RES01       | 2h | `contracts/I-001-*.md §4`、`test-matrix.md` |
| T-002   | I-001        | [Impl]     | P0 | T-001         | 3h | `contracts/I-001-*.md`、`data-model.md` |
| T-003   | I-002        | [AutoTest] | P0 | T-RES01       | 2h | `contracts/I-002-*.md §4`、`test-matrix.md` |
| T-004   | I-002        | [Impl]     | P0 | T-003         | 3h | `contracts/I-002-*.md`、`data-model.md` |

---

## Task Execution Guidelines (for Implementation Agents)

对于 **[AutoTest] / [Impl] 接口任务**，实施代理必须严格遵守以下原则：
1. **单一输入源主路径**: 实现前必须先加载 `ai-view-context.xml`（由 `/speckit.tasks` 生成）作为唯一业务上下文主输入；接口级上下文应从该文件裁剪得到。
2. **条件回查**: 禁止回读 Markdown 源文档补语义；若 `ai-view-context.xml` 缺失关键细节，必须回到上游阶段补齐并重新生成冻结上下文。
3. **先测后实**: 必须先完成 `[AutoTest]` 再进入 `[Impl]`；`[Impl]` 完成标准是对应自动化测试全绿。
4. **按图施工**: 不得擅自创造新的类结构或变更数据模型设计，核心类/实体必须与 `data-model.md` 一致。
5. **镜像翻译**: 将详设中的伪代码、类级时序准确翻译为目标语言的源代码。
