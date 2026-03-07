# Workflow SSOT Boundaries

本文档定义 Spec-Kit 在 SDD 主链中的职责边界与单一来源（SSOT）约束，避免规则在 `scripts / commands / templates` 三层重复定义与漂移。

## 1) Script 层（Deterministic Side Effects）

**定位**：本地确定性动作执行器。

**允许**：

- Git/分支/目录/文件等本地副作用
- 环境探测、前置条件检测
- 输出 machine-readable JSON（供 command 消费）

**禁止**：

- 定义阶段编排顺序（例如应先 `/sdd.plan` 还是 `/sdd.tasks`）
- 定义产物章节结构（`spec.md/plan.md/tasks.md` 的 heading/table contract）
- 在脚本内隐式引入与 command 不一致的业务策略

---

## 2) Command 层（Workflow Orchestration）

**定位**：阶段流程编排与 gate 执行。

**允许**：

- 定义输入/输出依赖关系
- 调用 script 并消费其 JSON 输出
- 定义阶段 gate、handoff、失败处理

**禁止**：

- 重新定义 artifact 的固定结构（结构 SSOT 在 template/schema）
- 复制 script 内部算法（例如编号分配细节）

**约束**：

- command 必须信任 script 输出作为确定性来源（deterministic source）
- command 只声明“做什么/按什么顺序做”，而非“文档长什么样”

---

## 3) Template / Schema 层（Artifact Structure SSOT）

**定位**：产物结构与稳定字段的唯一来源。

**允许**：

- 定义 mandatory/optional sections
- 定义稳定标题、表头、固定标签
- 定义 artifact 的导航与结构骨架

**禁止**：

- 定义本地副作用（建分支、改 git、改环境）
- 定义阶段执行顺序与 gate 逻辑

---

## 4) 冲突解决优先级

当多层描述不一致时，按以下优先级处理：

1. **Script 实际输出**（仅针对脚本副作用与脚本结果）
2. **Template/Schema**（仅针对 artifact 结构）
3. **Command 文本说明**（应回收为编排语义，不应覆盖前两者）

---

## 5) 最小一致性检查（CI 推荐）

- command 引用的脚本必须存在，且输出 key 与预期一致
- command 不得与 template 的结构 contract 冲突
- 对关键策略（如 feature 编号策略）增加回归测试，防止文档-实现漂移

## 6) Pre-Implementation 上下文解析约束（新增）

在 `implement` 之前的阶段（如 `plan / design / tasks / preview / analyze`）必须遵循以下规则：

- **必须显式输入文件**：命令执行时第一个输入参数必须是明确文件路径（如 `spec.md` / `plan.md` / `tasks.md`）。
- **上下文来源唯一**：阶段上下文只能从该输入文件及其所属 `specs/<feature>/` 目录中的必要兄弟产物解析。
- **禁止隐式推断**：不得依赖当前 git 分支名、`SPECIFY_FEATURE` 或最近的 `specs/*` 目录推断 active feature。

分层职责补充：

- Script 层：负责 input-file-derived feature context 的确定性解析。
- Command 层：负责声明 allowed input basenames 与阶段 gate，不重写解析算法。
- Template/Schema 层：继续仅负责结构与稳定字段，不承载上下文解析策略。
