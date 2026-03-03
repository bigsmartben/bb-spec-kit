---
name: bbspec-skill
description: 精准修改 spec-kit 的 specify/plan/spec 指令与模板，确保每次变更严格限定在最小必要文件集内，不发生范围扩散。适用于：修改命令逻辑、调整模板结构、优化工作流步骤、新增章节字段等场景。
---

# Spec-Kit 指令与模板精准修改技能

## 目的

对 `specify`、`plan`、`spec` 等指令及其关联模板进行**范围受控的变更**，杜绝无关文件被意外触及。

---

## 文件所有权地图（Change Ownership Map）

每项需求必须先对号入座，只动对应列的文件。

| 修改目标 | 主要文件 | 禁止触及 |
|---|---|---|
| `speckit.specify` 指令逻辑 | `templates/commands/specify.md` | 其他 `commands/*.md` |
| `speckit.specify` 输出结构 | `templates/spec-template.md` | `plan-template.md`、其他模板 |
| `speckit.plan` 指令逻辑 | `templates/commands/plan.md` | 其他 `commands/*.md` |
| `speckit.plan` 输出结构 | `templates/plan-template.md` | `spec-template.md`、其他模板 |
| `speckit.constitution` 指令逻辑 | `templates/commands/constitution.md` | 其他 `commands/*.md` |
| `speckit.constitution` 输出结构 | `templates/constitution-template.md` | plan/spec/tasks 模板 |
| `speckit.tasks` 指令逻辑 | `templates/commands/tasks.md` | 其他 `commands/*.md` |
| `speckit.tasks` 输出结构 | `templates/tasks-template.md` | plan/spec/constitution 模板 |
| `speckit.implement` 指令逻辑 | `templates/commands/implement.md` | 其他 `commands/*.md`，无对应产物模板 |
| 功能分支/目录创建逻辑 | `scripts/bash/create-new-feature.sh`<br>`scripts/powershell/create-new-feature.ps1` | CLI 源码 |
| Plan 产物初始化逻辑 | `scripts/bash/setup-plan.sh`<br>`scripts/powershell/setup-plan.ps1` | CLI 源码 |
| 新增 Agent 支持 | `src/specify_cli/__init__.py` | 模板文件（除非该 Agent 格式特殊） |
| `speckit.checklist` 指令 | `templates/commands/checklist.md`、`templates/checklist-template.md` | 其他命令/模板 |

---

## 变更分类（必须在动手前判断）
所有修改都必须使用英文专业术语(中文示例除外)，避免歧义
### 类型 A：指令提示词变更
影响 AI 的行为逻辑，**只改 `templates/commands/<name>.md`**。

常见场景：
- 调整步骤顺序或描述
- 修改 NEEDS CLARIFICATION 规则
- 更改 handoff 目标或 prompt
- 调整错误处理逻辑
- **constitution**：修改占位符替换规则、版本号递增策略、一致性传播步骤清单
- **tasks**：修改任务格式要求、并行标记规则、阶段划分逻辑、任务 ID 命名规则
- **implement**：修改检查项检测逻辑、ignore 文件生成规则、阶段执行顺序或终止条件

### 类型 B：模板结构变更
影响生成产物的格式，**只改对应 `templates/<name>-template.md`**。

常见场景：
- 增删章节（如在 spec-template 中加新小节）
- 修改字段标签或注释
- 调整必填/可选标注
- **constitution-template**：增删原则节（`[PRINCIPLE_N_NAME]`）、调整 Governance 章节结构
- **tasks-template**：修改格式说明头部、阶段组织方式、任务 ID 规范说明
- **注意**：implement 无对应产物模板，不存在类型 B 变更

### 类型 C：脚本行为变更
影响文件创建/复制/JSON 输出，**只改 bash + PowerShell 对应脚本**，且两者必须同步。

常见场景：
- 修改 JSON 输出字段
- 更改目录布局
- 调整参数解析

### 类型 D：复合变更
类型 A + B 组合（指令逻辑 + 模板结构同步调整），**逐文件分步操作，每步完成再进行下一步**。

**constitution 的特殊 D 类**：constitution 指令步骤 4（一致性传播）触发其他模板需要更新时，属于类型 D。必须标注：哪条原则变化 → 影响哪个模板的哪个节 → 对应修改内容。

---

## 精准修改工作流

### Step 1 — 需求定界（必做）

在动任何文件之前，用一句话回答：

> **"本次修改的根本目的是：___，受影响的文件集合是：___"**

若文件集合超过 3 个，重新审视是否混入了不相关需求。

### Step 2 — 定位目标节点

对于 `templates/commands/*.md`：
- 找到要修改的具体步骤编号（如 `3. Load context:`）
- 找到对应的 Markdown 段落范围（行号）

对于 `templates/*-template.md`：
- 找到要修改的章节标题（如 `### 1.2  系统边界`）
- 确认是修改内容还是注释

### Step 3 — 执行最小变更

- 只替换**必须改变**的字符串范围
- 保持相邻段落、缩进、注释风格不变
- Bash 脚本有变更时，PowerShell 脚本**同步跟进**（且只改对称部分）

### Step 4 — 自我核查（完成后必做）

完成变更后，逐项确认：

```
□ 改动的文件是否完全在 Step 1 划定的集合内？
□ 未改动文件的内容是否一字未变？
□ 如有脚本改动，bash/PowerShell 是否已同步？
□ templates/commands/*.md 的 frontmatter（description/handoffs/scripts）是否按需更新？
□ 本次变更是否新增了任何命令注册或 agent 配置（如无需求，答案应为"否"）？
```

---

## 关键约束（硬规则）

1. **`src/specify_cli/__init__.py` 不在 specify/plan/spec/constitution/tasks/implement 模板修改的范围内**，除非明确新增 agent。
2. **`templates/commands/` 中的文件是所有 agent 的共同源**，打包脚本会自动为各 agent 生成命令文件，**无需手动同步到 `.claude/commands/` 等目录**。
3. 六个模板（spec/plan/constitution/tasks/checklist/agent-file）**互相独立**，修改一个不会也不应触及其他模板。
4. **`speckit.constitution` 的特殊性**：constitution 指令在步骤 4（一致性传播）中会**读取**其他模板来核查对齐情况——这是读操作，不是写操作。仅当 constitution 原则确实与其他模板产生实质冲突时，才允许同步修改对应模板（属于类型 D，必须明确标注）。
5. **`speckit.implement` 无对应产物模板**：implement 只读取已有产物（tasks.md、plan.md 等），不生成新模板文件。修改 implement 指令逻辑时，确认改动不会误导 AI 去修改其他命令的产物格式。
6. **`speckit.tasks` 与 tasks-template.md 的关系**：tasks-template.md 中的示例任务是**占位说明**，真实任务由命令运行时动态生成。修改模板时只改结构/格式定义，不改示例任务的业务内容。
7. 新增章节时，必须明确是 `mandatory`（必填）还是 `optional`（可选），与现有注释风格保持一致。
8. frontmatter 中的 `scripts.sh` / `scripts.ps` 路径**不得改变**，除非脚本文件本身也在变更范围内。

---

## 常见反模式（禁止行为）

| 反模式 | 原因 |
|---|---|
| "顺手"修改 clarify.md 里类似的措辞 | 超出范围，会引入非预期行为 |
| 修改 spec-template 后同时更新 plan-template "保持一致" | 两者独立，保持一致不是修改 plan 的理由 |
| 在命令 frontmatter 中增加新 handoff 但需求未提及 | 扩散行为，需额外需求支撑 |
| 因 bash 脚本改动而重构 PowerShell 脚本结构 | 只做对称的最小同步，不重构 |
| 读取所有命令文件再决定改哪个 | 先定界再读——只读目标文件 |
| constitution 步骤 4 读取其他模板后"顺手"更新它们 | 读取≠修改；只有存在实质冲突时才允许写入，且必须标注为类型 D |
| 修改 tasks 命令逻辑后"顺便检查" implement 命令是否需要同步 | 不在范围内，implement 逻辑独立，无需联动检查 |
| 为 implement 命令新建对应产物模板文件 | implement 不产生模板；禁止创建 `implement-template.md` |
| 修改 tasks-template 中示例任务的业务内容 | 示例仅为占位说明，业务内容由命令运行时动态生成，模板层不应硬编码 |

---

## 示例

### 示例 1：修改 specify 指令中 NEEDS CLARIFICATION 的数量上限

**定界**：类型 A，文件集 = `templates/commands/specify.md`

**定位节点**：找到 `LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total` 所在行

**执行**：只替换数字 `3` 为新值，不动其他行

**核查**：确认只有该文件有 diff

---

### 示例 2：在 spec-template 中新增"非功能需求"小节

**定界**：类型 B，文件集 = `templates/spec-template.md`

**定位节点**：确定新节插入位置（如在 § 1 系统边界之后）

**执行**：仅在目标位置插入新节，保持相邻节内容不变

**核查**：`templates/commands/specify.md` 中的 `Load templates/spec-template.md` 步骤无需修改，因为命令只引用路径，不描述章节细节

---

### 示例 3：修改 plan 脚本的 JSON 输出字段名

**定界**：类型 C，文件集 = `scripts/bash/setup-plan.sh` + `scripts/powershell/setup-plan.ps1`

**执行**：先改 bash，再找 PowerShell 中对称位置同步修改

**核查**：`templates/commands/plan.md` 中是否引用了该字段名（如 `IMPL_PLAN`）——若有，需标注为类型 D 并补充修改该文件，否则不动

---

### 示例 4：在 constitution 指令中修改版本号递增规则

**定界**：类型 A，文件集 = `templates/commands/constitution.md`

**定位节点**：找到步骤 2 中 `CONSTITUTION_VERSION` 相关段落（MAJOR/MINOR/PATCH 规则说明）

**执行**：只替换规则描述文字，不动其他步骤

**核查**：constitution-template.md、plan-template.md、其他命令文件均一字未变

---

### 示例 5：在 tasks-template 中新增"验收测试阶段"占位

**定界**：类型 B，文件集 = `templates/tasks-template.md`

**定位节点**：找到现有 Phase 结构末尾

**执行**：插入新 Phase 节（含格式说明注释），业务示例任务只写占位符

**核查**：`templates/commands/tasks.md` 中"生成 tasks.md"步骤无需修改，它引用的是模板路径而非章节名

---

### 示例 6：修改 implement 中 checklist 未完成时的阻断逻辑

**定界**：类型 A，文件集 = `templates/commands/implement.md`

**定位节点**：找到步骤 2 "If any checklist is incomplete" 分支

**执行**：只修改该分支的行为描述（如改为直接终止而非询问）

**核查**：tasks.md、tasks-template.md、脚本文件均未触及；implement 无模板文件，无类型 B 变更