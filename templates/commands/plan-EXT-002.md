---
description: EXT-002 计划生成（承接 spec 业务锚点并补齐实现映射）
---

## 输入

- `spec.md`（必需）
- `spec-template-EXT-002.md`（结构参考）

## 执行规则

1. 读取 spec 中以下内容：
   - `§ 1.3 Key Entities`
   - 每个 UC 的 `3.5 组件-数据依赖总览`
2. 生成 `plan.md` 时：
   - 保留业务锚点引用（不重定义 Entity 语义）
   - 在 `Interface & Implementation Mapping` 中补齐接口/事件/存储细节
3. 若发现以下冲突则报错：
   - 组件依赖项无法映射到任一 `Entity.field`
   - 实现映射与 spec 更新触发事件语义冲突

## 输出

- `plan.md`
- `data-model.md`
- `contracts/`（如适用）

## 验收检查

- 追溯链完整：`FR -> 组件 -> Entity.field -> 实现映射`
- 所有 MUST 级 FR 在 plan 中均有落地条目
