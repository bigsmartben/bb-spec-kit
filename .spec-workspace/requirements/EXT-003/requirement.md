# EXT-003: Contract SSoT 粒度与 Interface ID 绑定 UX Flow

> 📋 **需求ID**: EXT-003  
> 📅 **创建时间**: 2026-03-03  
> 👤 **创建者**: Spec Kit 开发团队  
> 🎯 **优先级**: P1  
> 📊 **状态**: 待评审

---

## 📝 需求概述

### 问题陈述
当前规范中“接口契约”与“UX Flow”之间的映射粒度不统一，常出现 Flow 节点描述与接口定义脱节的问题。进一步地，smoke-tests 与 contracts/ux-flow 的 ID 引用不稳定，导致评审时无法快速证明链路一致性。

### 目标
建立以 `I-XXX` 为最小粒度的 Contract SSoT 规则，并强制 UX Flow 节点与 Interface ID 绑定，确保 `contracts`、`ux-flow`、`smoke-tests` 三类产物之间可追溯、可校验。

### 范围
**包含**：
- Contract SSoT 的命名与粒度规则（`I-XXX`）
- UX Flow 的 Node-to-Interface Mapping 规则
- smoke-tests 与 Interface ID 的追溯规则

**不包含**：
- 新增 CLI 功能
- 修改主仓库模板内容
- 修改运行时代码实现

---

## 👥 用户场景

### 场景 1: Plan 文档编制
**角色**: 方案设计者  
**目标**: 让接口契约与交互流程在文档层可闭环追溯  
**步骤**:
1. 在 `contracts/` 下按 `I-XXX` 建立接口契约定义
2. 在 UX Flow 中为每个系统节点标注 `I-XXX`
3. 在 smoke-tests 中引用对应 `I-XXX` 并形成追溯矩阵

**期望结果**: 任意 Flow 节点都可定位到唯一接口契约，且能映射到 smoke-test 用例。

### 场景 2: 设计评审
**角色**: 评审人（产品/开发/测试）  
**目标**: 快速验证 ID 自洽  
**步骤**:
1. 抽查任一 `I-XXX`
2. 反查对应 Flow Node 和 Test Case
3. 检查是否存在断链或一对多歧义

**期望结果**: ID 引用一致，无孤立节点或孤立测试。

---

## 🎨 功能需求

### FR-1: Contract SSoT 的 `I-XXX` 粒度规则
**描述**: 接口契约必须以 `I-XXX` 为最小管理单元，字段级定义为 SSoT；若存在 OpenAPI，仅作为视图层表达，不替代 SSoT。  
**优先级**: Must Have  
**输入**: Plan 阶段接口定义信息  
**输出**: `I-XXX` 级接口契约清单及字段约束

### FR-2: UX Flow 节点绑定 Interface ID
**描述**: UX Flow 中所有系统处理节点必须映射到唯一 `I-XXX`，并通过 Node-to-Interface Mapping 记录。  
**优先级**: Must Have  
**输入**: UX Flow 节点列表  
**输出**: Flow Node → Interface ID 映射表

### FR-3: smoke-tests 追溯一致性
**描述**: smoke-tests 必须引用 `I-XXX`，并可回溯到对应 Flow Node，形成最小追溯链。  
**优先级**: Must Have  
**输入**: smoke-test 用例清单  
**输出**: Node / Interface / Test Case 三元追溯关系

---

## 🎯 非功能需求

### NFR-1: 可审计性
- 任意 `I-XXX` 可在文档中双向追溯到 Flow Node 与测试用例。

### NFR-2: 一致性
- 同一接口 ID 语义在 contracts、ux-flow、smoke-tests 三处保持一致。

### NFR-3: 可维护性
- 允许增量新增 `I-XXX`，且不破坏既有编号语义。

---

## ✅ 验收标准

### AC-1: Contract SSoT 粒度明确
**Given**: 已定义接口契约  
**When**: 审查 contracts 目录规则  
**Then**: 仅接受 `I-XXX` 粒度，且字段级定义为 SSoT。

### AC-2: UX Flow 节点可映射
**Given**: 已产出 UX Flow  
**When**: 抽查任一系统节点  
**Then**: 可定位唯一 `I-XXX`。

### AC-3: smoke-tests 可追溯
**Given**: 已产出 smoke-tests  
**When**: 抽查任一测试用例  
**Then**: 可回溯对应 Flow Node 与 `I-XXX`。

### AC-4: 文档校验通过
**Given**: EXT-003 需求目录文件完整  
**When**: 运行 `validate-requirement.sh EXT-003`  
**Then**: 校验通过（允许 warning）。

---

## 📊 变更历史

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2026-03-03 | 1.0 | 初始创建 | Spec Kit 开发团队 |

---

**最后更新**: 2026-03-03  
**状态**: 待评审
