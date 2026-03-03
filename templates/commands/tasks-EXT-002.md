---
description: EXT-002 任务生成（双来源拆解：spec 锚点 + plan 映射）
---

## 输入

- `spec.md`（必需）
- `plan.md`（必需）
- `data-model.md` / `contracts/`（可选增强）

## 执行规则

1. 先从 spec 提取业务任务线索：
   - UC、FR、组件-数据依赖锚点、更新触发事件
2. 再从 plan 提取实现任务线索：
   - Interface & Implementation Mapping
   - 数据模型落地、错误处理、并发策略
3. 合并生成任务时，必须为每个实现任务标注其上游锚点：
   - `ref: UC/FR`
   - `ref: Entity.field`

## 任务组织建议

- Phase 1: Setup
- Phase 2: Foundation
- Phase 3+: 按用户故事拆解
- Final: 追溯与一致性复核

## 失败条件（阻断生成）

- 出现无法追溯到 `Entity.field` 的实现任务
- MUST 级 FR 未被任何任务覆盖
- Spec 与 Plan 对同一组件触发事件定义冲突
