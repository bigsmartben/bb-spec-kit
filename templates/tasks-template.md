---
description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`  
**Outputs**: tasks.md (this document), interface detail docs, `checklists/udd-vo-coverage.md`  
**Execution Contract**: See `/sdd.tasks` command for format, types, rules (SSOT)

## Structure SSOT Notes

- This template is the structural source of truth for `tasks.md` section skeleton.
- `/sdd.tasks` command should orchestrate and populate this structure, not redefine it.

## Task Format

`- [ ] T### [P?] [Type:Research|Interface|Test|Infra|Docs] [IFxx?] Description with file path`

[Refer to `/sdd.tasks` Execution Contract for detailed generation rules]

## Task Types (Canonical)

- `Research`
- `Interface`
- `Test`
- `Infra`
- `Docs`

## Interface Inventory

| InterfaceID | Interface | Served User Stories |
| --- | --- | --- |
| IF01 | [operationId or contract doc] | [US###, ...] |

## Interface Section Template (repeat per IFxx)

```markdown
## Interface IFxx — [name]

- Goal: [one-line delivery goal]
- Contract: [operationId/path]
- Served User Stories: [US/UC refs]
- Definition of Done: [verifiable completion criteria]

- [ ] T### [Type:Test] [IFxx] ...
- [ ] T### [Type:Interface] [IFxx] ...
```

## Phases (Template Structure)

- **Phase 0**: Research (if unknowns exist)
- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundations (shared blocking prerequisites)
- **Phase 3+**: Interfaces (IFxx delivery units; each: Test -> Implementation)
- **Final**: Polish & Cross-Cutting

## Final Phase Template

- [ ] T### [Type:Docs] Update final reviewer/developer notes in specs/[###-feature-name]/quickstart.md
- [ ] T### [Type:Infra] Run final validation command set in [relevant path(s)]

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
- Refer to `/sdd.tasks` Execution Contract for DAG & diagram rules
