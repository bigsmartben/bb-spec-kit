---
description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`  
**Outputs**: tasks.md (this document), interface detail docs, `checklists/udd-vo-coverage.md`  
**Execution Contract**: See `/speckit.tasks` command for format, types, rules (SSOT)

## Task Format

`- [ ] T### [P?] [Type:Research|Interface|Test|Infra|Docs] [IFxx?] Description with file path`

[Refer to `/speckit.tasks` Execution Contract for detailed rules]

## Interface Inventory

| InterfaceID | Interface | Served User Stories |
| --- | --- | --- |
| IF01 | [operationId or contract doc] | [US###, ...] |

## Phases (Template Structure)

- **Phase 0**: Research (if unknowns exist)
- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundations (shared blocking prerequisites)
- **Phase 3+**: Interfaces (IFxx delivery units; each: Test -> Implementation)
- **Final**: Polish & Cross-Cutting

## DAG (Required Output)

### Task DAG (Adjacency List) — PRIMARY SSOT

```text
T001 -> T010    # Phase order
T010 -> T020    # Setup before Foundations
T020 -> T030    # Foundations before interfaces
T030 -> T032    # Test setup before implementation
```

**Notes**: 
- Every edge MUST cite valid TaskID present in this file
- Refer to `/speckit.tasks` Execution Contract for DAG & diagram rules
