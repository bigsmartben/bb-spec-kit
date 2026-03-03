# Terminology Guide（术语指南）

> Purpose（目的）: Standardize terminology and control semantics across Spec Kit templates.
> Scope（范围）: All files under `templates/`, `templates/commands/`, and generated artifacts.
> Normative References（参考标准）: ISO/IEC/IEEE 24765, DDD, BDD, RFC 2119.

---

## §1 Language Policy（语言策略）

### 1.1 Control Semantics Policy（控制语义策略）

- MUST: All control semantics be expressed in English.
- MUST: Use unique canonical terms for phases, artifacts, IDs, gates, and constraints.
- MUST NOT: Use Chinese as the only carrier of executable/decision semantics.
- MAY: Add Chinese as annotation for human readability.

### 1.2 Human Annotation Policy（中文注释策略）

- SHOULD: Use `English（中文）` for section titles in human-facing templates.
- SHOULD: Use `EnglishKey（中文说明）` for table headers.
- MAY: Add Chinese explanation after an em dash (`—`) when clarifying strict rules.

### 1.3 Commands and Constitution Policy（命令与宪章策略）

- MUST: Files in `templates/commands/` remain ONLY English for control semantics and workflow logic.
- MUST: `templates/constitution-template.md` remain ONLY English for baseline memory semantics.
- MAY: Keep minimal Chinese in non-control comments/examples only if strictly necessary.

---

## §2 RFC 2119 Rule Keywords（规则关键字）

Use these keywords for all gates and normative rules:

- MUST
- MUST NOT
- SHOULD
- MAY

Example（示例）:

- `MUST NOT: Define HTTP method/path in Spec — Spec 阶段禁止接口签名。`

---

## §3 Canonical Terms（规范术语字典）

The following terms are locked for spelling and capitalization across all templates.

| Canonical Term（标准术语） | Chinese Annotation（中文注释） | Notes（说明） |
|---|---|---|
| Guardrails | 阶段管控检查 | Stage gate checklist semantics |
| Constitution Check | 宪章一致性检查 | Plan-time governance gate |
| Contract SSoT | 契约唯一真相源 | Primary contract source |
| Context Compression | 上下文压缩 | CTX/REF/DELTA format |
| Interface Design | 接口设计 | Phase 5 artifact |
| Field Specification | 字段规格 | Visibility/output data semantics |
| Traceability Matrix | 追溯矩阵 | Requirement–design–task–test linkage |
| Data Model | 数据模型 | Class and logical schema artifact |
| Test Matrix | 测试矩阵 | Full testing coverage artifact |
| UX Flow | 交互流程 | Main flow artifact |
| Smoke Tests | 冒烟测试 | Minimum executable validation |
| Single Source of Truth (SSoT) | 唯一真相源 | Authoritative information source |
| Definition of Done (DoD) | 完成定义 | Delivery acceptance baseline |

---

## §4 English Retention Rules（英文保留规则）

### 4.1 Domain Terms（领域术语）

Keep original English for standard domain vocabulary. On first occurrence in human-facing templates, use `English（中文）`.

| Domain Term（领域术语） | First Occurrence Format（首次格式） |
|---|---|
| Bounded Context | `Bounded Context（限界上下文）` |
| Ubiquitous Language | `Ubiquitous Language（统一语言）` |
| Anti-Corruption Layer | `Anti-Corruption Layer（防腐层）` |
| Context Map | `Context Map（上下文映射）` |
| Aggregate Root | `Aggregate Root（聚合根）` |

### 4.2 BDD/Gherkin Terms（BDD 术语）

MUST keep original keywords unchanged:

- Feature
- Scenario
- Given
- When
- Then
- Scenario Outline

### 4.3 Technical Standards and Abbreviations（技术标准与缩写）

MUST keep original forms:

- RBAC, OAuth 2.0, GDPR
- RESTful API, OpenAPI
- DTO, VO, BO, PO
- SRP, ISP, DIP, OCP, LSP
- CI/CD, TLS, AES

---

## §5 Prohibited Variants（禁用变体）

Do not use non-canonical variants that break searchability or uniqueness.

| Prohibited Variant（禁用写法） | Canonical Replacement（标准替代） |
|---|---|
| 字段表契约主源 | Contract SSoT |
| 唯一真理来源 | Single Source of Truth (SSoT) |
| 接口详细设计 | Interface Design |
| 模型设计与全量测试 | Data Model + Test Matrix |
| 交互主链路 | UX Flow |
| 表单呈现要素内容 | Field Specification |
| UI元素（作为字段语义） | Field Specification |

---

## §6 Template Formatting Rules（模板格式规则）

### 6.1 Section Titles（章节标题）

Human-facing templates MUST use:

- `English（中文）`

Examples:

- `## Overview（概述）`
- `## Functional Requirements（功能需求）`
- `## Phase 1: Contract SSoT（接口契约主源）`

### 6.2 Table Headers（表头）

Human-facing templates MUST use:

- `EnglishKey（中文说明）`

Example:

```markdown
| Interface ID（接口ID） | Method（方法） | Purpose（用途） | Status（状态） |
|---|---|---|---|
```

### 6.3 Rules and Gates（规则与门禁）

Normative sentences MUST begin with RFC 2119 keywords.

Example:

- `MUST: Keep section numbering unchanged.`
- `MUST NOT: Remove required template sections.`

---

## §7 Governance Process（治理流程）

1. New Term Admission（新增术语）: Add to `memory/constitution.md` glossary and this guide in the same change set.
2. Term Update（术语变更）: Update all affected templates and references.
3. Consistency Review（一致性审查）: Run terminology checks before each release.
4. Conflict Resolution（冲突裁决）: Priority = ISO/IEC/IEEE 24765 > DDD/BDD standards > team conventions.

---

## §8 Compliance Checklist（合规Checklist（检查清单））

- [ ] Control semantics are English-only in `templates/commands/`.
- [ ] `templates/constitution-template.md` is English-only.
- [ ] Human-facing template titles follow `English（中文）`.
- [ ] Human-facing table headers follow `EnglishKey（中文说明）`.
- [ ] Canonical terms are used with exact spelling/capitalization.
- [ ] Rules use RFC 2119 keywords.

---

Version（版本）: 2.0
Maintainer（维护者）: Spec Kit Team
