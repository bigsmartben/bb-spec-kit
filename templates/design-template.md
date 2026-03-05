---
description: "Design handoff template pack for speckit.design outputs (UX artifacts, UI spec, and static prototype)."
---

# Design Handoff Template: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Input**: `spec.md` (required), `plan.md` (optional constraints)

**Purpose**: Single navigation entry point for design outputs produced by `/speckit.design`.

Use this template as the structure baseline for the design handoff index. Detailed content templates live in:

- `design-ux-template.md`
- `design-ui-template.md`
- `design-prototype-template.md`

## Artifacts Overview & Navigation *(mandatory)*

Status MUST be one of: `Planned`, `Generated`, `N/A`.

| Artifact | Path | Purpose | Status |
| --- | --- | --- | --- |
| JTBD | `ux/jtbd.md` | Capture primary user job, persona, alternatives, and measurable outcomes | `Planned` |
| Journey Map | `ux/journey.md` | Capture stage-by-stage user actions, feelings, pain points, and opportunities | `Planned` |
| User Flow | `ux/flow.md` | Capture happy path + edge/error flows and accessibility expectations | `Planned` |
| UI Specification | `ui/ui-spec.md` | Capture screens, IA, components, copy, state model, accessibility, and traceability | `Planned` |
| Prototype Hub | `prototype/index.html` | Entry page linking all key prototype screens | `Planned` |
| Prototype Pages | `prototype/pages/*.html` | One page per key screen with representative states | `Planned` |
| Prototype Styles | `prototype/assets/styles.css` | Shared tokens, component styles, responsive and accessibility styling | `Planned` |
| Prototype Script | `prototype/assets/app.js` | Mock data, state toggles, and minimal interactions | `Planned` |
| Prototype Readme | `prototype/README.md` | Local viewing and optional static server instructions | `Planned` |

---

## Design Artifacts & Dependency Order *(mandatory)*

The design workflow produces multiple artifacts. Generate them in strict dependency order.

| Order | Artifact | Path | Depends on |
| ---: | --- | --- | --- |
| 1 | UX artifacts | `ux/` | `spec.md` (+ any UI constraints from `plan.md` if present) |
| 2 | UI specification | `ui/ui-spec.md` | `spec.md` + `ux/` |
| 3 | Static prototype | `prototype/` | `ui/ui-spec.md` + `ux/` |

---

## Project Structure *(mandatory)*

```text
specs/[###-feature]/
├── ux/
│   ├── jtbd.md
│   ├── journey.md
│   └── flow.md
├── ui/
│   └── ui-spec.md
└── prototype/
    ├── index.html
    ├── pages/
    │   └── *.html
    ├── assets/
    │   ├── styles.css
    │   └── app.js
    └── README.md
```

---

## Completion Checklist *(mandatory)*

- [ ] All required design files are created under `ux/`, `ui/`, and `prototype/`.
- [ ] `ui/ui-spec.md` contains requirement traceability (`FR-###` or scenario mapping).
- [ ] Accessibility expectations are explicit in UX flow and UI spec.
- [ ] Prototype supports desktop + mobile breakpoints.
- [ ] No backend/runtime dependency is introduced in prototype assets.
