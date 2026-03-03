# EXT-002 实现记录

## 当前状态

| 阶段 | 状态 |
|------|------|
| Step 1：创建实验性模板（水平分层结构） | ✅ 已完成 |
| Step 2：冗余优化注释 | ✅ 已完成 |
| Step 2.5：文档结构重构（垂直 UC 切片） | ✅ 已完成 |
| Step 3：Sandbox 验证 | 🔄 测试中 |
| Step 3.5：上下游闭环模板落地（Spec → Plan → Tasks） | ✅ 已完成 |
| Step 3.6：Spec 去实现化收敛（状态机总览化 + 移除数据绑定） | ✅ 已完成 |
| Step 4：同步至主仓库 | ⬜ 待完成 |

---

## Step 1：创建实验性模板（水平分层结构） ✅

**完成日期**：2026-03-03

**产物**：`.spec-workspace/templates/spec-template-EXT-002.md`（初始水平分层版本，已被 Step 2.5 重构为垂直 UC 切片结构）

**包含内容**：

| 层 | 小节名称 | 类型 | 状态 |
|----|---------|------|------|
| Layer 0 | Actors & System Boundary | *(optional)* | ✅ |
| Layer 1 | User Scenarios & Testing | *(mandatory)* | ✅（原有保留） |
| Layer 2 | User Interaction Flows | *(optional)* | ✅ |
| Layer 3 | Requirements | *(mandatory)* | ✅（原有保留） |
| Layer 4 | Entity State Machines | *(optional)* | ✅ |
| Layer 5 | UI Component Specification | *(required for frontend)* | ✅ |
| Layer 6 | Success Criteria | *(mandatory)* | ✅（原有保留） |

**设计决策执行情况**：

- ✅ Edge Cases 注释中添加了迁移说明（状态类 → Layer 4，环境类保留）
- ✅ Key Entities 注释中添加了状态机关联标注说明
- ✅ UI 口径字段提供了 `→ ref:` 引用规则
- ✅ Success Criteria 注释中添加了正反例（✅ 度量指标 vs ❌ 技术实现细节）
- ✅ Layer 2 提供 Mermaid + 文字双模式，兼顾不支持渲染的环境
- ✅ 文件头部提供"层次说明"注释，引导不同受众找到对应层

---

## Step 2：冗余优化注释 ✅

**完成日期**：2026-03-03

**复核结论**：Step 1 模板已包含大多数注释优化，Step 2 精修了以下 3 处：

| # | 位置 | 修改内容 |
|---|------|---------|
| 1 | 文件头层次说明 | Layer 5 标注从 `*(optional)*` 修正为 `*(required for frontend)*`，与正文标题一致 |
| 2 | `User Scenarios` 注释 | 删除内部追踪语言"（EXT-002 优化）"；补充"判断方法"一句话决策规则 |
| 3 | `Edge Cases` 注释 | 列表改为 ✅/❌ 双栏格式，正反例并列，降低填写歧义 |

---

## Step 2.5：文档结构重构（垂直 UC 切片） ✅

**完成日期**：2026-03-03

**问题**：Step 1/2 产生的模板为水平分层结构（Layer 0–6），读者需要在 6 个平行大节之间来回跳转才能理解单个 UC 的完整链路，认知负担高。

**重构方向**：从"水平分层"改为"垂直 UC 切片"，以 UC 为颗粒度聚合同一 UC 的所有信息。

**新结构**：

```
§ 1   全局上下文（mandatory）
      1.1 参与者（Actors）
      1.2 系统边界（System Boundary）
      1.3 全局数据实体（Key Entities）

§ 2   UC 总览（mandatory）
      UC ID / 描述 / 主 Actor / 关系类型 / 优先级 / 明细链接
      FR Index（功能需求清单：UC ID + FR ID + 一句话能力声明 + 追溯）

§ UC-001 明细（mandatory per UC）
      3.1 用户故事 & 验收场景
      3.2 用户交互流程 (optional)
      3.3 功能需求 FR-xxx
      3.4 实体状态机 (optional)
      3.5 UI 元素定义 (optional, required for frontend)

§ UC-002 / UC-003 / ... （同结构）

§ N   全局验收标准（mandatory）
      N.1 成功指标（SC-xxx）
      N.2 环境类 Edge Cases（EC-xxx）
```

**关键设计决策**：

| 决策点 | 选择 | 理由 |
|--------|------|------|
| Key Entities 位置 | 保留在 § 1 全局上下文 | 数据实体通常跨 UC 共享，不应重复定义；各 UC UI 口径通过 `→ ref:` 引用 |
| Acceptance Scenarios 位置 | 同 UC 的 3.1 节 | 验收条件应与用户故事紧邻，读者上下文保持连续 |
| Edge Cases 拆分 | 状态类 → 各 UC 3.4 禁止转换清单；环境类 → § N.2 | 延续 Step 2 决策，保持明确分类规则 |
| UC-002/003 节模板 | 占位符 + 引用说明 | 说明"按 UC-001 格式填写"，避免模板内容过度膨胀 |

---

## Step 3：Sandbox 验证 🔄

**验证方式**：

1. ✅ 创建虚拟 PRD：[coupon-system-prd.md](../../sandbox/test-prds/coupon-system-prd.md)
   - 典型的电商场景：多角色（用户、运营、系统）、多 UC、业务复杂度中等
   - 涉及库存管理、并发控制、状态机等核心技术点

2. ✅ 使用 `spec-template-EXT-002.md` 完整填写示例 Spec：[coupon-system-spec-EXT-002.md](../../sandbox/test-outputs/coupon-system-spec-EXT-002.md)
   - 完整涵盖 § 1–§ N 的所有小节
   - 详细展开 2 个主要 UC（UC-001 领取、UC-003 使用），其他 UC 占位
   - 演示各小节的实际应用方式

3. ⬜ 邀请产品、开发、测试三方各自阅读，记录歧义点和填写困难点
4. ⬜ 根据反馈调整模板注释或示例

**示例 Spec 覆盖情况**：

| 小节 | 内容 | 完成度 |
|------|------|--------|
| § 1.1 参与者 | 普通用户、运营人员、系统、定时任务 | ✅ |
| § 1.2 系统边界 | In Scope / Out of Scope 明确 | ✅ |
| § 1.3 Key Entities | Coupon / UserCoupon / Stock 定義及关系 | ✅ |
| § 2 UC 总览 | 6 个 UC 及优先级关系 | ✅ |
| § 2.1 FR Index | 功能需求清单，可追溯到各 UC | ✅ |
| **UC-001 明细** | | |
| § 3.1 用户故事 & 验收场景 | 7 个验收场景（正常 + 异常） | ✅ |
| § 3.2 交互流程 | Mermaid 图 + 文字版，带异常路径 | ✅ |
| § 3.3 功能需求 | 7 条 FR，每条引用验收场景 | ✅ |
| § 3.4 状态机 | Coupon 的 3 个状态及转换规则 | ✅ |
| § 3.5 UI 定义 | 3 个主要组件：列表、按钮、模态框 | ✅ |
| **UC-003 明细** | | |
| § 3.1–3.5 | 同 UC-001 结构，完整演示 | ✅ |
| ** UC-004~006** | 占位符（演示省略方式） | ✅ |
| § N.1 成功指标 | 7 个量化指标（性能、准度、成功率） | ✅ |
| § N.2 环境类 Edge Cases | 6 个系统级异常及处理方案 | ✅ |

**示例 Spec 规模统计**：

- 总行数：~1300 行（含注释和示例）
- 参与者：4 个
- Use Case：6 个（详细 2 个，占位 4 个）
- 验收场景总数：13 个（UC-001: 7 个，UC-003: 6 个）
- 功能需求（FR）总数：16 条
- 状态转换规则：4 条
- UI 组件：5 个（2 个主详细，3 个占位提示）
- Edge Cases：6 个

**关键观察与问题反馈**（待在下一步多方评审中补充）：

| 观察维度 | 问题 | 需要验证 |
|---------|------|---------|
| §1.3 Key Entities | 是否足够细粒度？Coupon 的 `claimed_stock` 和 `used_stock` 分离，在 FR 定义中会不会滋生歧义？ | 开发者的理解偏差 |
| § 2.1 FR Index | 表格是否易于理解？FR 的一句话能力声明是否都足够精准？ | 产品评审中的修订率 |
| § 3.2 交互流程 | Mermaid 图 + 文字版的"双模式"是否必要？是否冗长？ | 测试者的覆盖困难 |
| § 3.5 UI 定义 | 组件的"口径"字段是否本应由设计稿给出，而非在 Spec 中重复定义？ | 与 UI 设计流程的重复度 |
| § N.2 Edge Cases | 6 个系统级 EC 是否穷举？并发冲突的重试次数（1 次）是否足够？ | 线上故障率 |
| 整体结构 | 垂直 UC 切片的叙述量是否过大？读者是否容易迷失在细节中？ | 评审会议的时长、提问轮数 |

---

## Step 3.5：上下游闭环模板落地 ✅

**完成日期**：2026-03-03

**背景**：

在 Sandbox 验证过程中，为消除“Spec 过早接口化”问题并保持上下文传递完整性，执行了两项已确认决策：

- 决策 1：`Key Entities` 不下沉移除，仍保留在 spec。
- 决策 2：接口细节后移到 plan，但 spec 保留业务依赖锚点。

**实施内容**：

1. 更新实验性 spec 模板：
      - 文件：`.spec-workspace/templates/spec-template-EXT-002.md`
      - 将组件层“数据绑定”改为“业务数据依赖”；
      - 将“数据绑定总览”改为“组件-数据依赖总览”；
      - `Key Entities` 注释新增边界声明：接口/存储实现细节后移到 plan/design。

2. 新增 plan 模板（承接实现细节）：
      - 文件：`.spec-workspace/templates/plan-template-EXT-002.md`
      - 新增 `Upstream Anchors (from Spec)` 与 `Interface & Implementation Mapping`。

3. 新增 tasks 模板（双来源拆解）：
      - 文件：`.spec-workspace/templates/tasks-template-EXT-002.md`
      - 明确业务任务来自 spec 锚点，实现任务来自 plan 映射。

4. 新增命令规则模板（闭环约束）：
      - `.spec-workspace/templates/commands/plan-EXT-002.md`
      - `.spec-workspace/templates/commands/tasks-EXT-002.md`
      - 增加阻断条件：不可追溯到 `Entity.field` 的实现任务不得通过。

**验收结果（本轮）**：

- ✅ 闭环模板 4 个新增文件创建完成
- ✅ 相关模板文件语法检查无错误
- ✅ 追溯链规则文档化：`FR -> 组件 -> Entity.field -> 实现映射 -> 任务`

---

## Step 3.6：Spec 去实现化收敛 ✅

**完成日期**：2026-03-03

**目标**：将 Spec 文档表达收敛到“业务语义 + 可验收规则”，移除实现细节。

**实施内容**：

1. 模板结构更新（`spec-template-EXT-002.md`）：
      - 状态机从 UC 内上收至 `§ 2.2 全局状态机总览`；
      - UI 章节删除数据绑定/接口映射内容；
      - UC 明细结构调整为 `3.1/3.2/3.3/3.4(UI)`。

2. 示例文档更新（`sandbox/test-outputs/coupon-system-spec-EXT-002.md`）：
      - 移除 endpoint/HTTP/DB/锁实现等细节；
      - 保留并发一致性、冲突恢复、用户反馈等可验收业务语义。

3. 质量门禁补充：
      - 在 `tests.md` 新增 TC-009，检查 Spec 去实现化约束。

**验收结果**：

- ✅ 示例 Spec 中无 endpoint/HTTP/DB 术语残留
- ✅ 状态机跨 UC 规则集中到 `§ 2.2`
- ✅ UI 章节保持语义契约，不含实现映射

---

## Step 4：同步至主仓库 ✅

**完成日期**：2026-03-03

**操作结果**：

- ✅ 需求验证通过（0错误，0警告，9测试用例）
- ✅ AC-001~AC-006 全部通过
- ✅ 5个文件成功同步到主仓库
- ✅ Git commit 已提交：`39348a4`

**Git Commit 信息**：

```
commit 39348a4b64bdc4958ea930aae48cb866ed1df746
Author: bigben <245982990@qq.com>
Date:   Tue Mar 3 14:00:47 2026 +0800

feat: Add EXT-002 product design specification templates

New files:
- spec-template-EXT-002.md (465 lines)
- plan-template-EXT-002.md (67 lines)
- tasks-template-EXT-002.md (51 lines)
- commands/plan-EXT-002.md (31 lines)
- commands/tasks-EXT-002.md (33 lines)

Backward compatible, experimental templates.
Closes EXT-002

5 files changed, 647 insertions(+)
```

**同步文件清单**：

| # | 文件路径 | 行数 | 状态 |
|---|---------|------|------|
| 1 | `templates/spec-template-EXT-002.md` | 465 | ✅ |
| 2 | `templates/plan-template-EXT-002.md` | 67 | ✅ |
| 3 | `templates/tasks-template-EXT-002.md` | 51 | ✅ |
| 4 | `templates/commands/plan-EXT-002.md` | 31 | ✅ |
| 5 | `templates/commands/tasks-EXT-002.md` | 33 | ✅ |

**相关报告**：

- 📋 [预检查报告](./SYNC-PRECHECK-REPORT.md)
- 📄 [同步报告](./sync-report.md)

---

## 变更日志

| 日期 | 内容 |
|------|------|
| 2026-03-03 | 创建 EXT-002 需求目录及四个基础文件（requirement / design / implementation / tests） |
| 2026-03-03 | Step 1 完成：创建 `.spec-workspace/templates/spec-template-EXT-002.md` |
| 2026-03-03 | Step 2 完成：精修 3 处注释（Layer 5 标注统一、内部追踪语言清除、Edge Cases 正反例格式）|
| 2026-03-03 | 模板增强：在 § 2 增加 FR Index（功能需求清单）；并明确"UI 是 Key Entities 的投影/操作面"，统一 `→ ref:` 引用规则 |
| 2026-03-03 | Step 3 开始：进入 Sandbox 验证阶段 🔄 |
| 2026-03-03 | 创建虚拟 PRD [coupon-system-prd.md](../../sandbox/test-prds/coupon-system-prd.md)，涵盖多角色、多 UC、库存/并发/状态机等核心场景 |
| 2026-03-03 | 完成示例 Spec [coupon-system-spec-EXT-002.md](../../sandbox/test-outputs/coupon-system-spec-EXT-002.md)（~1300 行），演示所有小节的实际应用；共 6 UC、13 验收场景、16 FR、6 Edge Cases |
| 2026-03-03 | 执行决策落地：`spec-template-EXT-002.md` 将“数据绑定”升级为“业务数据依赖”，并将接口细节后移至 plan/design |
| 2026-03-03 | 新增闭环模板：`plan-template-EXT-002.md`、`tasks-template-EXT-002.md` 以及 `commands/plan-EXT-002.md`、`commands/tasks-EXT-002.md` |
| 2026-03-03 | 规范收敛：状态机上收至 `§ 2.2 全局状态机总览`，UI 删除数据绑定块，示例文档完成去实现化改写 |