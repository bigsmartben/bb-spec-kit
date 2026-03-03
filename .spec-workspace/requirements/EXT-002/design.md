# EXT-002 技术设计文档

## 设计目标

在不破坏 `spec-template.md` 现有三个必填区块的前提下，以**总览 + UC 明细**的方式叠加产品设计规范层：

- `§ 2.2` 统一维护跨 UC 的全局状态机；
- UC 明细保留用户故事、交互流程、功能需求、UI 语义契约；
- Spec 阶段不包含接口端点/请求响应/存储映射等实现细节。

---

## 模板分层架构

```text
spec-template-EXT-002 目标结构

§ 1 全局上下文（mandatory）
  1.1 Actors
  1.2 System Boundary
  1.3 Key Entities

§ 2 UC 总览（mandatory）
  2.1 FR Index
  2.2 全局状态机总览（optional, 推荐）

§ UC-xxx 明细
  3.1 用户故事 & 验收场景（mandatory）
  3.2 用户交互流程（optional）
  3.3 功能需求 FR（mandatory）
  3.4 UI 元素定义（前端功能 required）

§ N 全局验收标准（mandatory）
  N.1 Success Criteria
  N.2 环境类 Edge Cases
```

### 使用视角分层

| 受众 | 重点层 | 说明 |
|-----|--------|------|
| 产品评审 | §1 / §2 / 各UC 3.1~3.4 | 理解"谁做什么"、"流程如何"、"界面长什么样" |
| 开发实现 | §2.2 / 各UC 3.3 / 3.4 | 功能要求 + 状态逻辑 + UI 契约 |
| 测试验收 | 各UC 3.1 / §N | 验收场景 + 成功指标 |

---

## 冗余处理决策

### 决策 1：Edge Cases 内容裁剪

**现状**：`Edge Cases` 混合了两类内容：
- 状态类：`"如果任务已关闭，不允许再次关闭"`
- 环境类：`"如果网络超时，显示重试提示"`

**决策**：
- 状态类条目 → 迁移至 `§ 2.2 全局状态机总览` 的「禁止转换清单」
- 环境类条目 → 保留在 `Edge Cases`

**模板内的落地方式**：在 `§ N.2 Edge Cases` 注释中增加说明：
> 仅填写环境类异常（网络、权限、服务不可用、并发超时）；
> 状态转换类约束请移至 `§ 2.2 全局状态机总览 → 禁止转换清单`

---

### 决策 2：Key Entities 与 UI 元素定义的口径归属

**现状**：`Key Entities` 定义实体属性，`UI Component Specification` 也涉及字段口径，潜在重复。

**决策**：
- `Key Entities` = **数据层单一真相**（定义字段名、类型、约束）
- `UI Component Specification` 口径通过 `→ ref: [EntityName].[fieldName]` 引用
- 只有**展示层特有的格式差异**（时区转换、数字精度格式、空态文案）才在 UI 层单独补充

**模板内的落地方式**：在 Key Entities 注释和 UI 口径字段均加入引用说明提示。

---

### 决策 3：FR-xxx 与 Acceptance Scenarios 的分工

**现状**：轻微重叠（FR 说"系统能做 X"，Scenario 验证"给定条件验证 X"）。

**决策**：保留两者，在模板注释中明确分工。不删减内容。
- `FR-xxx` = **能力声明**（What the system does）
- `Acceptance Scenarios` = **验证规格**（How to verify it）

---

### 决策 4：User Interaction Flow 与 Acceptance Scenarios 的关系

**决策**：
- `Acceptance Scenarios` → 验证**单个路径的输入输出**
- `User Interaction Flows` → 描述**多条路径的结构和连接关系**

两者互补，不互相替代。Flow 中每个分支节点建议标注对应的 Acceptance Scenario 编号。

---

### 决策 5：Spec 去实现化边界（新增）

**决策**：Spec 阶段禁止强制要求实现细节，包含但不限于：

- endpoint / HTTP status code
- request/response 字段映射
- 数据库表结构与事务实现
- 锁实现细节（如 version/row-level）

**允许保留**：业务可验收语义（原子性、一致性、并发冲突恢复预期、用户可感知反馈）。

**落地方式**：

- 在模板注释中明确“实现细节后移到 plan/design”；
- 在测试用例中增加“去实现化”检查项，防止文档回退到实现描述。

---

## 模板内容设计细节

### Layer 0 设计要点

- Actor 表格：类型区分 Human / System / Timer，含权限与职责描述
- 系统边界分 In Scope / Out of Scope 两个列表
- Use Case 清单表格，含 UC ID、关系类型（Primary / `<<include>>` / `<<extend>>`）、关联 UC
- Traceability 注释：每条 UC 追溯到对应 User Story

### Layer 2 设计要点

参考 `.spec-workspace/user_template/交互流程图.md` 的图例约定：
- `[]` 页面/界面状态
- `()` 用户操作
- `{}` 系统决策/条件判断

每条 Flow 组成：
1. 前置条件表格（用户状态 / 系统状态 / 数据状态）
2. 主流程（Mermaid `graph TD` + 文字描述双模式，解决不支持 Mermaid 渲染的场景）
3. 异常路径表格（异常ID / 触发步骤 / 触发条件 / 系统响应 / 用户感知 / EC ref）
4. 后置条件表格（分主流成功、各异常情况）

### § 2.2 全局状态机总览 设计要点

- 状态枚举表格：State / 业务语义 / 是否初始 / 是否终止（✅ / ❌）
- 转换矩阵表格：From State / Event / Guard / To State / 操作 Actor
- 禁止转换清单：bullet list，精确到转换方向（`A → *` 或 `A → C`）
- 并发规则：文字说明，不强制格式

### § UC-xxx 3.4 UI 元素定义 设计要点

- 页面视图信息表：页面标题 / 路由路径 / 入口方式 / 权限要求
- 每个组件独立分块（用 `---` 分隔），字段：
  - 类型：枚举常用类型
  - 显示文案：按状态分行（默认 / 加载 / 空 / 错误）
  - 内涵（必填，有正反示例）
  - 口径（必填，有 ref 引用规则说明）
  - 状态规则表：状态 / 触发条件 / 视觉表现 / 交互行为
  - 触发行为（关联 FR-xxx）

> 注意：UI 元素定义不包含接口/请求字段映射；实现细节下沉到 plan。

---

## 文件输出规划

| 文件 | 路径 | 说明 |
|------|------|------|
| 实验性模板 | `.spec-workspace/templates/spec-template-EXT-002.md` | Step 1 产物，供评审和 sandbox 测试 |
| 主仓库模板（同步后） | `templates/spec-template.md` | Step 4 同步后的最终修改目标 |

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| 模板过长，使用者跳过新增小节 | 所有新增小节标注 `*(optional)*`，降低心理负担；使用层次说明注释引导 |
| 内涵口径描述仍不够规范 | 模板内提供正例和反例，强制"内涵"和"口径"分项填写 |
| 与交互流程图模板格式不一致 | 以 `user_template/交互流程图.md` 为参考基准，图例约定保持一致 |
| Mermaid 在部分环境无法渲染 | Flow 主流程提供"mermaid + 文字双模式" |
