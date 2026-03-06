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

## Design Summary *(mandatory)*

- Scope summary: [What in-scope user outcomes this handoff covers]
- Out of scope: [Explicitly excluded capabilities]
- Primary actor(s): [Who this design optimizes for]
- Implementation target: [Web/mobile platform and notable constraints from `plan.md`]

SSOT note: `spec.md` remains the requirements SSOT. This design handoff MUST only operationalize in-scope requirements into UX/UI/prototype artifacts.

---

## Reviewer Notes *(optional)*

- Key assumptions: [Assumption + rationale]
- Open questions: [Question + owner]
- Risk register: [Risk + impact + mitigation]

---

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

## Recommended Review Order *(mandatory)*

1. `ux/jtbd.md` and `ux/journey.md` — verify user/job framing and pain points.
2. `ux/flow.md` — verify happy path + edge/error logic and accessibility expectations.
3. `ui/ui-spec.md` — verify screen/state/component/data contracts and requirement traceability.
4. `prototype/index.html` then `prototype/pages/*.html` — verify implementation readiness and state demonstrations.
5. `prototype/README.md` — verify handoff notes, assumptions, and known deltas.

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
- [ ] `spec.md` SSOT is preserved (no new normative requirements introduced in design artifacts).
- [ ] `ui/ui-spec.md` contains requirement traceability (`FR-###` or scenario mapping) and screen-to-prototype mapping.
- [ ] Accessibility expectations are explicit in UX flow, UI spec, and prototype behavior.
- [ ] Prototype supports desktop + mobile breakpoints with visible non-happy-path states.
- [ ] No backend/runtime dependency is introduced in prototype assets.
