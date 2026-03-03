# Main-Flow Smoke Tests（主链路冒烟测试）: [FEATURE]

**Plan**: [plan.md](./plan.md) | **Date**: [DATE] | **Phase**: Phase 2 - Smoke Tests

---

## Overview（概述）

本文档用于定义 Phase 2 的最小可跑通冒烟测试（Smoke），聚焦核心业务链路与关键失败路径。

- **输入来源**: `contracts/ux.flow.md` + `contracts/api.contract-table.md`
- **可选一致性参考**: `contracts/api.openapi.yaml`
- **目标**: 在实现前确认“主链路可跑通 + 关键失败可识别”

### Success Criteria Check（门禁）

- [ ] 每条主链路至少 1 条 Happy Path 用例 + 1 条关键失败用例。
- [ ] 每条 Smoke 用例可追溯到至少 1 个 Flow 节点 ID 与 1 个 Interface ID。
- [ ] 每条 Smoke 用例包含最小数据前置、操作步骤、期望响应语义。
- [ ] 覆盖外部依赖可用性/降级场景（如存在三方调用）。

---

## 1. Smoke Case Overview（Smoke用例总览）

| SmokeID（SmokeID） | Type（类型） | Interface ID | Flow Path/Node | Priority（优先级） | Goal（目标） |
|---------|------|-------------|----------------|-------|------|
| ST-001 | Happy Path | I-001/I-002 | P-HAPPY-001 | P0 | 验证主链路端到端可跑通 |
| ST-002 | Failure Path | I-001 | P-FAIL-001 | P0 | 验证关键入参失败可识别 |
| ST-003 | Failure Path | I-002 | P-FAIL-002 | P1 | 验证外部依赖失败可降级 |

---

## 2. Detailed Case Definitions（用例详细定义）

### 2.1 ST-001 — Main-Flow Success Smoke（主链路成功冒烟）

| Item（项目） | Content（内容） |
|------|------|
| Interface ID | I-001, I-002 |
| Flow 引用 | `P-HAPPY-001`（`N-001 → N-002 → N-003 → N-004`） |
| 前置条件 | 测试账号可用；外部依赖健康；最小合法参数准备完成 |
| 输入数据 | `userId=U1001`, `amount=100`, `channel=APP` |
| 操作步骤 | 1) 调用 I-001 创建请求 2) 触发 I-002 外部交互 3) 接收响应 |
| 期望结果 | 返回 2xx；响应含 `code/message/data`；关键 Field Specification 与契约表一致 |
| 验收检查点 | 无阻断错误；链路耗时在可接受范围；traceId 可追踪 |

### 2.2 ST-002 — Invalid-Input Failure Smoke（入参非法失败冒烟）

| Item（项目） | Content（内容） |
|------|------|
| Interface ID | I-001 |
| Flow 引用 | `P-FAIL-001`（`N-001 → N-ERR-001`） |
| 前置条件 | 无 |
| 输入数据 | `amount=0` 或缺失必填字段 |
| 操作步骤 | 调用 I-001 并提交非法参数 |
| 期望结果 | 返回 4xx；错误码/错误信息语义明确；不进入后续业务步骤 |
| 验收检查点 | 错误响应结构符合契约；日志中可定位失败原因 |

### 2.3 ST-003 — External-Dependency Failure Smoke（外部依赖失败冒烟）

| Item（项目） | Content（内容） |
|------|------|
| Interface ID | I-002 |
| Flow 引用 | `P-FAIL-002`（`N-003 → N-ERR-002`） |
| 前置条件 | 外部服务设置为超时或返回错误（Mock/Stubs） |
| 输入数据 | 合法业务参数 |
| 操作步骤 | 调用主链路并触发外部依赖失败 |
| 期望结果 | 返回降级响应或可预期失败码；系统状态不出现脏写 |
| 验收检查点 | 失败路径可恢复；告警/日志字段完整 |

---

## 3. Traceability Matrix（追溯矩阵）（Smoke ↔ Flow ↔ Contract）

| SmokeID（SmokeID） | FlowNodeOrPath（Flow节点/路径） | Interface ID | ContractKeyFieldSpecification（契约关键字段规格） | Notes（备注） |
|---------|----------------|-------------|------------------------------|------|
| ST-001 | P-HAPPY-001 | I-001/I-002 | `userId`, `amount`, `channel`, `traceId` | 主链路成功 |
| ST-002 | P-FAIL-001 | I-001 | `amount`, `code`, `message` | 参数失败 |
| ST-003 | P-FAIL-002 | I-002 | `channel`, `traceId`, `code` | 外部失败 |

---

## 4. Execution Guidance（执行建议）

- 执行顺序：`ST-001` → `ST-002` → `ST-003`
- 失败处理：任一 P0 用例失败即阻断进入后续 Plan 阶段
- 输出约束：仅保留最终结论与证据链接，不额外创建分析草稿文件

---

**后续步骤**:
本文件为 Phase 2 最小验证集合；Phase 4 在 `test-matrix.md` 中补全全量测试矩阵。
