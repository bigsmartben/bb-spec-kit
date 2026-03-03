# Tasks (EXT-002): [FEATURE NAME]

**Input**: `/specs/[###-feature-name]/` 下的设计文档  
**Prerequisites**: `plan.md`（必需）, `spec.md`（必需）, `data-model.md`（建议）, `contracts/`（如有）

> 任务拆解原则（闭环）：
> 1) 业务任务来源于 **spec 的组件-数据依赖锚点**；
> 2) 实现任务来源于 **plan 的 Interface & Implementation Mapping**；
> 3) 二者必须可追溯到同一个 `Entity.field`。

## 任务格式

- [ ] `Txxx [P?] [USx] 描述（含文件路径）`

## Phase 1: Setup

- [ ] T001 初始化目录结构与基础依赖
- [ ] T002 建立 lint / format / test 基础配置

## Phase 2: Foundation（阻塞）

- [ ] T003 建立通用错误处理与日志框架
- [ ] T004 建立配置与环境管理
- [ ] T005 建立基础数据模型骨架

## Phase 3+: User Story Slices

### User Story 1 (P1)

**Goal**: [目标]

- [ ] T010 [US1] 从 spec 抽取组件-数据依赖锚点并生成追溯表（`specs/.../traceability.md`）
- [ ] T011 [US1] 按 plan 映射实现接口/事件适配层（`src/...`）
- [ ] T012 [US1] 实现实体字段读写与校验（`src/models/...`）
- [ ] T013 [US1] 实现组件状态更新触发链路（`src/ui/...`）
- [ ] T014 [US1] 覆盖异常路径与重试策略（`tests/integration/...`）

### User Story 2 (P2)

- [ ] T020 [US2] 复用同一追溯链扩展功能点

## Final Phase: Cross-Cutting

- [ ] T900 全链路追溯复核：FR → 组件 → Entity.field → 实现代码
- [ ] T901 文档同步：更新 quickstart / 设计说明

## 质量门禁（必须通过）

- [ ] 每个 US 至少有 1 条独立验证路径
- [ ] 不允许存在“仅在 plan 定义、spec 无锚点”的实现任务
- [ ] 不允许存在“spec 有锚点、plan 无实现映射”的悬空项
