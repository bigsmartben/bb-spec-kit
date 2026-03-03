# Implementation Plan (EXT-002): [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]  
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

> 本模板用于承接 `spec-template-EXT-002.md` 的下游实现设计。  
> 原则：**Spec 保留业务语义与依赖锚点；Plan 承接接口/存储/事件等实现映射。**

## Summary

[从 spec 提取：核心目标、主用例、关键业务约束]

## Technical Context

**Language/Version**: [e.g., Python 3.11]  
**Primary Dependencies**: [e.g., FastAPI, React]  
**Storage**: [e.g., PostgreSQL / N/A]  
**Testing**: [e.g., pytest, Playwright]  
**Target Platform**: [e.g., Linux + Web]  
**Constraints**: [e.g., p95 < 200ms / 并发 / 一致性要求]

## Upstream Anchors (from Spec)

### A. Key Entities 语义锚点

> 仅引用，不重定义口径。

- [Entity.field] → [语义摘要]
- [Entity.field] → [语义摘要]

### B. 组件-数据依赖锚点

> 来源：spec 的“组件-数据依赖总览”。

| 组件 ID | 依赖数据项 | 数据依赖来源（业务） | 更新触发事件 | Entity 字段引用 |
|---|---|---|---|---|
| [component-id] | [item] | [业务来源] | [trigger] | ref: [Entity].[field] |

## Interface & Implementation Mapping（Plan 专属）

> 在此补齐实现细节：API、消息事件、存储、缓存、错误处理、重试策略。

| 组件 ID | 实现通道 | 请求/输入映射 | 响应/输出映射 | 失败处理 | 幂等/并发策略 |
|---|---|---|---|---|---|
| [component-id] | [REST/GraphQL/Event/Local] | [ui/input -> dto] | [dto -> view-model] | [fallback/retry] | [idempotency key/lock] |

## Data Model Realization

> 将 Key Entities 落地为实现级模型（字段类型、约束、索引、关系）。

- **Model [Name]**
  - Fields: [name:type:constraints]
  - Relations: [one-to-many ...]
  - Validation: [rule list]

## Delivery Slices (by User Story)

- **US1 / P1**: [MVP]
- **US2 / P2**: [增量]
- **US3 / P3**: [增强]

## Verification Plan

- [ ] 追溯检查：FR → 组件 → Entity.field → 实现映射
- [ ] 合同检查：接口定义与映射矩阵一致
- [ ] 错误路径检查：异常场景覆盖 spec 的 EC
- [ ] 性能与并发检查：满足约束
