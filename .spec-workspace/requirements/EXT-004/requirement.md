# EXT-004: Smoke Tests + Interface Design 门禁与最小设计包

> 📋 **需求ID**: EXT-004  
> 📅 **创建时间**: 2026-03-03  
> 👤 **创建者**: Spec Kit 开发团队  
> 🎯 **优先级**: P1  
> 📊 **状态**: 待评审

---

## 📝 需求概述

### 问题陈述
当前 smoke tests 与 UX Flow、Contract SSoT 的推导链路缺乏硬性门禁，导致“测试覆盖看似存在但追溯关系不完整”的问题。同时接口设计材料粒度不统一，缺少 `I-XXX` 级别的最小设计包标准。

### 目标
建立两项门禁：
1. smoke tests 必须从 UX Flow + Contract SSoT 推导，并提供 Traceability Matrix；
2. 每个 `I-XXX` 接口必须具备最小设计包（时序图、伪代码、自动化测试策略、源码变更清单）。

### 范围
**包含**：
- smoke tests 推导规则与追溯矩阵要求
- `I-XXX` 最小接口设计包必备项
- 文档边界声明（不与 data-model 类图重复）

**不包含**：
- 新增 CLI 功能
- data-model 文档结构改造

---

## 👥 用户场景

### 场景 1: 方案设计者输出最小设计包
**角色**: 方案设计者  
**目标**: 为每个接口提供统一最小设计信息  
**步骤**:
1. 为 `I-XXX` 编写类方法级时序图
2. 补充伪代码逻辑
3. 给出自动化测试策略
4. 列出源码变更清单

**期望结果**: 接口实现前已具备可评审的最小设计闭环。

### 场景 2: 测试人员审查可追溯性
**角色**: 测试工程师  
**目标**: 验证 smoke tests 来源与覆盖正确  
**步骤**:
1. 查看 Traceability Matrix
2. 抽查 Flow Node / Interface / Test Case 关联
3. 识别未覆盖节点

**期望结果**: smoke tests 来源明确，缺口可快速定位。

---

## 🎨 功能需求

### FR-1: Smoke Tests 推导门禁
**描述**: smoke tests 必须由 UX Flow + Contract SSoT 推导，不允许脱离两者独立编写。  
**优先级**: Must Have  
**输入**: UX Flow、Contract SSoT  
**输出**: 可追溯 smoke tests 集合

### FR-2: Traceability Matrix 强制要求
**描述**: smoke tests 文档必须包含追溯矩阵，最少列：`Flow Node`、`Interface ID`、`Test Case ID`。  
**优先级**: Must Have  
**输入**: 测试用例清单  
**输出**: 完整追溯矩阵

### FR-3: `I-XXX` 最小设计包门禁
**描述**: 每个接口必须至少包含四项：类方法级时序图、伪代码逻辑、自动化测试策略、源码变更清单。  
**优先级**: Must Have  
**输入**: 接口设计资料  
**输出**: 接口最小设计包

### FR-4: 文档边界约束
**描述**: 接口设计包不得重复 data-model 的类图内容；类图归属仍在 data-model 文档。  
**优先级**: Must Have  
**输入**: 设计文档内容  
**输出**: 无重复、边界清晰的文档结构

---

## 🎯 非功能需求

### NFR-1: 可验证性
- 评审人员可通过矩阵快速发现缺失覆盖。

### NFR-2: 一致性
- 所有接口按统一四项结构产出最小设计包。

### NFR-3: 可维护性
- 接口变更可定位到对应设计包与测试策略。

---

## ✅ 验收标准

### AC-1: 推导链完整
**Given**: 已有 UX Flow 与 Contract SSoT  
**When**: 审查 smoke tests 来源  
**Then**: 每条 smoke test 可追溯到 Flow Node 与 `I-XXX`。

### AC-2: 追溯矩阵完整
**Given**: 已编写 smoke tests  
**When**: 检查矩阵列  
**Then**: 至少包含 `Flow Node`/`Interface ID`/`Test Case ID`。

### AC-3: 接口最小设计包完整
**Given**: 任一 `I-XXX` 接口  
**When**: 审查设计文档  
**Then**: 必含时序图、伪代码、自动化测试策略、源码变更清单。

### AC-4: 边界约束生效
**Given**: 设计文档存在类图内容  
**When**: 审查内容归属  
**Then**: data-model 类图不在本 EXT 的接口设计包内重复定义。

### AC-5: 文档校验通过
**Given**: EXT-004 目录文件完整  
**When**: 运行 `validate-requirement.sh EXT-004`  
**Then**: 校验通过（允许 warning）。

---

## 📊 变更历史

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2026-03-03 | 1.0 | 初始创建 | Spec Kit 开发团队 |

---

**最后更新**: 2026-03-03  
**状态**: 待评审
