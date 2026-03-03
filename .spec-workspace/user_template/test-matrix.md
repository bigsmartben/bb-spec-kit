# Test Case Matrix（测试用例矩阵）: [FEATURE]

**Plan**: [plan.md](./plan.md) | **Date**: [DATE] | **Phase**: Phase 4 - 测试设计

---

## Overview（概述）

本文档基于 Spec 的状态机定义（§3）与功能需求（§4），以及 Phase 1/3/4 产物（`contracts/api.contract-table.md`、`research.md`、`data-model.md`），系统化推导测试用例，建立需求 ↔ 用例的双向追溯矩阵。

### Test Design Principles（测试Design Principles（设计原则））

- **测试先行**: 本文档在实现前完成，作为 `[AutoTest]` 任务的直接输入
- **接口锚定**: 每个测试用例必须关联到至少一个 Interface ID 或 Spec 需求 ID
- **分层测试**: 契约测试 → 参数测试 → 状态依赖测试 → 集成测试，层层递进
- **可执行**: 每个用例需明确前置条件、操作步骤、期望结果，供 AutoTest 直接实现

---

## 1. State Machine Test Cases（状态机测试用例） (State Machine Tests)

> **消费来源**: `spec.md §3` 状态机图 / 状态转换表

### 1.1 State Transition Coverage Matrix（状态转换覆盖矩阵）

> **设计方法**: 覆盖所有正向路径、异常路径、边界转换

| TC-ID | From State | Event/Trigger | Guard Condition | To State | Test Type | Interface ID | Priority |
|-------|-----------|--------------|----------------|---------|----------|-------------|---------|
| SM-001 | [INIT] | [submit] | [amount > 0] | [PENDING] | 正向路径 | I-001 | P0 |
| SM-002 | [INIT] | [submit] | [amount <= 0] | [INIT] (rejected) | 边界值 | I-001 | P1 |
| SM-003 | [PENDING] | [approve] | [reviewer != submitter] | [APPROVED] | 正向路径 | I-002 | P0 |
| SM-004 | [PENDING] | [approve] | [reviewer == submitter] | [PENDING] (rejected) | 异常路径 | I-002 | P1 |
| SM-005 | [PENDING] | [reject] | [—] | [REJECTED] | 正向路径 | I-002 | P0 |
| SM-ERR-001 | [APPROVED] | [submit] | [—] | 错误响应(非法状态) | 异常路径 | I-001 | P1 |

### 1.2 State Machine Boundary Scenarios（状态机边界场景）

| ScenarioID（场景ID） | ScenarioDescription（场景描述） | PreState（前置状态） | ActionSequence（操作序列） | ExpectedResult（期望结果） | Interface ID |
|--------|---------|---------|---------|---------|-------------|
| SM-BOUND-001 | [并发审批竞态] | [PENDING] | [两个审批员同时 approve] | [只有一个成功，另一个返回 409] | I-002 |
| SM-BOUND-002 | [幂等性验证] | [APPROVED] | [重复发送 approve 请求] | [返回 200，状态不重复转换] | I-002 |

---

## 2. Functional Requirement Test Cases（功能需求测试用例） (Functional Requirement Tests)

> **消费来源**: `spec.md §4` 功能需求列表

### 2.1 Equivalence Class Partitioning（等价类划分）

> **方法**: 对每个功能需求进行等价类划分

| FT-ID | Func-ID | EquivalenceClassDescription（等价类描述） | InputConditions（输入条件） | ExpectedOutput（期望输出） | Interface ID | Priority |
|-------|--------|-----------|---------|---------|-------------|---------|
| FT-001 | F-001 | 有效金额 | amount = 100 (正整数) | 创建成功，返回 orderId | I-001 | P0 |
| FT-002 | F-001 | 零值金额 | amount = 0 | 400, code=2001 | I-001 | P1 |
| FT-003 | F-001 | 负数金额 | amount = -1 | 400, code=2001 | I-001 | P1 |
| FT-004 | F-001 | 超大金额 | amount = MAX_LONG + 1 | 400, code=2001 (overflow) | I-001 | P2 |

### 2.2 Boundary Value Analysis（边界值分析）

| BV-ID | Func-ID | BoundaryDescription（边界描述） | TestValue（测试值） | ExpectedResult（期望结果） | Interface ID | Priority |
|-------|--------|---------|-------|---------|-------------|---------|
| BV-001 | F-001 | 最小有效金额 | amount = 1 | 创建成功 | I-001 | P1 |
| BV-002 | F-001 | 最大有效金额 | amount = [MAX_AMOUNT] | 创建成功 | I-001 | P1 |
| BV-003 | F-001 | 超出最大金额 | amount = [MAX_AMOUNT + 1] | 400, code=2001 | I-001 | P1 |

### 2.3 Decision Table（判定表；功能组合场景）

| DT-ID | Function（功能） | Condition1（条件1） | Condition2（条件2） | Condition3（条件3） | Result（结果） | Interface ID |
|-------|-----|------|------|------|-----|-------------|
| DT-001 | [功能名] | [条件1=T] | [条件2=T] | [条件3=F] | [结果描述] | I-001 |
| DT-002 | [功能名] | [条件1=T] | [条件2=F] | [条件3=T] | [结果描述] | I-001 |

### 2.4 Exception Path Coverage（异常路径覆盖）

| EP-ID | ExceptionType（异常类型） | TriggerCondition（触发条件） | ExpectedErrorCode（期望错误码） | ExpectedHTTPStatus（期望HTTP状态） | Interface ID | Priority |
|-------|--------|---------|----------|----------------|-------------|---------|
| EP-001 | 未认证访问 | 无 Authorization header | 401 | 401 | 全部 | P0 |
| EP-002 | 权限不足 | 角色不匹配 | 403 | 403 | I-002 | P0 |
| EP-003 | 资源不存在 | 无效 ID | 2003 | 404 | I-002 | P1 |
| EP-004 | 参数非法 | 必填字段缺失 | 400 | 400 | 全部 | P1 |

---

## 3. Interface Automation Test Cases（接口自动化测试用例） (Interface Automation Tests)

> **消费来源**: `contracts/api.contract-table.md`（SSoT） + `data-model.md` + `research.md` + `contracts/api.openapi.yaml`（可选一致性参考）

### 3.1 Interface Test Case Index（各接口测试用例索引）

| Interface ID | InterfaceName（接口名称） | ContractTests（契约测试） | ParameterTests（参数测试） | StateDependentTests（状态依赖测试） | IntegrationTests（集成测试） | TotalCases（总用例数） |
|-------------|---------|---------|---------|-----------|---------|---------|
| I-001 | [接口名1] | 见 3.2.1 | 见 3.2.2 | 见 3.2.3 | 见 3.2.4 | [N] |
| I-002 | [接口名2] | 见 3.3.1 | 见 3.3.2 | 见 3.3.3 | 见 3.3.4 | [N] |

### 3.2 I-001: [InterfaceName（接口名称）] Detailed Cases（详细用例）

> **引用**: `contracts/api.contract-table.md`（I-001 字段契约） + `data-model.md`（相关类/状态）

#### Layer 1: Contract Tests（契约测试） (Contract Tests)

| CT-ID | TestDescription（测试描述） | Preconditions（前置条件） | Action（操作） | ExpectedResult（期望结果） | Priority |
|-------|---------|---------|-----|---------|---------|
| CT-I001-001 | Happy Path - 成功响应包含必需字段 | [用户已认证] | POST /api/xxx {valid payload} | 200, body 含 {id, status, createdAt} | P0 |
| CT-I001-002 | 后置条件 - 数据持久化验证 | [CT-I001-001 通过] | GET /api/xxx/{id} | 200, 数据与创建时一致 | P0 |
| CT-I001-003 | 不变量 - 幂等性 | [资源已存在] | POST /api/xxx {same idempotency-key} | 200, 返回已有数据，无重复创建 | P1 |

#### Layer 2: Parameter Tests（参数测试） (Parameter Tests)

| PT-ID | ParameterName（参数名） | TestType（测试类型） | TestValue（测试值） | ExpectedResult（期望结果） | Priority |
|-------|-------|---------|-------|---------|---------|
| PT-I001-001 | [param1] | 必填缺失 | null | 400, code=2001, msg 包含 "param1 required" | P1 |
| PT-I001-002 | [param1] | 类型错误 | "abc" (期望整数) | 400, code=2001 | P1 |
| PT-I001-003 | [param1] | 下边界 | 0 | 400, code=2001 | P1 |
| PT-I001-004 | [param1] | 上边界 | [MAX+1] | 400, code=2001 | P2 |
| PT-I001-005 | [param2] | XSS 注入 | `<script>alert(1)</script>` | 400 或转义后存储 | P2 |
| PT-I001-006 | [param2] | SQL 注入 | `'; DROP TABLE users;--` | 400 或安全处理 | P1 |

#### Layer 3: State-Dependent Tests（状态依赖测试） (State-Dependent Tests)

| SD-ID | TestDescription（测试描述） | CallOrder（调用顺序） | ExpectedResult（期望结果） | Priority |
|-------|---------|---------|---------|---------|
| SD-I001-001 | 调用顺序依赖 - 先创建再操作 | [创建] → [操作] | 操作成功 | P0 |
| SD-I001-002 | 非法状态操作 | [直接操作未初始化资源] | 404/409 | P1 |

#### Layer 4: Integration Tests（集成测试） (Integration Tests)

| IT-ID | TestDescription（测试描述） | InvolvedMocks（涉及Mock） | OperationFlow（操作链路） | ExpectedResult（期望结果） | Priority |
|-------|---------|---------|---------|---------|---------|
| IT-I001-001 | 完整业务链路 E2E | 无 Mock | [step1] → [step2] → [step3] | 最终状态正确 | P0 |
| IT-I001-002 | 外部服务降级 | Mock [外部服务] 超时 | [操作] | 降级响应 / 错误封装正确 | P1 |

### 3.3 I-002: [InterfaceName（接口名称）] Detailed Cases（详细用例）

> **引用**: `contracts/api.contract-table.md`（I-002 字段契约） + `data-model.md`（相关类/状态）

#### Layer 1-4: Case Tables（用例表格）

> *(按 3.2 节格式填写)*

---

## 4. Traceability Matrix（追溯矩阵） (Traceability Matrix)

### 4.1 Requirement -> Test Case Traceability（需求到测试用例追溯）

| SpecRequirementID（Spec需求ID） | RequirementDescription（需求描述） | RelatedTestCases（关联测试用例） | CoverageTypes（覆盖测试类型） | CoverageStatus（覆盖状态） |
|------------|---------|------------|-----------|---------|
| F-001 | [需求1描述] | SM-001, FT-001, FT-002, CT-I001-001 | SM+FT+CT | ✅ 覆盖 |
| F-002 | [需求2描述] | SM-003, SM-004, CT-I002-001 | SM+CT | ✅ 覆盖 |
| F-003 | [需求3描述] | [无关联用例] | — | ❌ 未覆盖 |

### 4.2 Test Case -> Requirement Traceability（测试用例到需求追溯）

| TestCaseID（测试用例ID） | TestDescription（测试描述） | TracedRequirements（追溯需求） | Interface ID |
|----------|---------|---------|-------------|
| SM-001 | [描述] | F-001, State §3.1 | I-001 |
| CT-I001-001 | [描述] | F-001, F-002 | I-001 |

### 4.3 Coverage Statistics（覆盖率统计）

| Dimension（维度） | Total（总数） | Covered（已覆盖） | Uncovered（未覆盖） | CoverageRate（覆盖率） |
|-----|-----|-------|-------|------|
| Spec 功能需求 | [N] | [N] | [0] | [100%] |
| 状态转换 | [N] | [N] | [0] | [100%] |
| 接口契约 | [N] | [N] | [0] | [100%] |

---

## 5. Test Quality Review（测试质量审查） (Test Quality Review)

### 5.1 Quality Evaluation Dimensions（质量评估维度）

| EvaluationDimension（评估维度） | CheckResult（检查结果） | Notes（说明） |
|---------|---------|-----|
| 独立性 | ✅/❌ | 测试间无隐式依赖 |
| 可重复性 | ✅/❌ | 无时间/随机/顺序依赖 |
| 断言明确性 | ✅/❌ | 每个用例有明确的期望结果 |
| 边界覆盖 | ✅/❌ | 等价类和边界值已覆盖 |
| 状态覆盖 | ✅/❌ | 所有状态转换路径已覆盖 |
| 异常路径 | ✅/❌ | 关键异常场景已覆盖 |

### 5.2 Gap Analysis（缺口分析） (Gap Analysis)

> 下列需求/场景当前测试覆盖不足，建议补充：

| GapID（缺口ID） | GapDescription（缺口描述） | SuggestedAdditionalCases（建议补充用例） | RiskLevel（风险等级） |
|--------|---------|------------|---------|
| GAP-001 | [缺口描述] | [建议用例] | 🔴 High |
| GAP-002 | [缺口描述] | [建议用例] | 🟡 Medium |

### 5.3 Mock Strategy Summary（策略汇总）

> 汇总所有接口的 Mock 需求（来源: `I-XXX-*.md §4.3`）

| MockTarget（Mock目标） | Type（类型） | UsedByTests（使用的测试） | MockBehavior（Mock行为） |
|---------|-----|---------|---------|
| [外部服务1] | HTTP Stub | IT-I001-002 | 返回超时响应 |
| [外部服务2] | gRPC Mock | IT-I002-003 | 返回指定错误码 |

---

## Execution Plan（执行计划）

| TestLevel（测试层次） | MappedTask（对应任务） | Dependencies（依赖） | Priority（优先级） |
|---------|---------|-----|------|
| SM Tests (状态机) | T-RES01 [AutoTest] | Phase 4 设计完成 | P0 |
| FT Tests (功能需求) | T-001 [AutoTest] | Phase 4 设计完成 | P0 |
| CT Tests (契约) | T-001 [AutoTest] | `contracts/api.contract-table.md` 完成 | P0 |
| PT Tests (参数) | T-001 [AutoTest] | 契约测试通过 | P1 |
| IT Tests (集成) | T-002 [AutoTest] | Impl 完成 | P0 |

---

**Note**: 本文档由 `/speckit.plan` 命令 Phase 4 生成。详见 `.specify/templates/commands/plan.md §Phase 4`。
