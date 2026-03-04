---
description: Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent templates stay in sync.
handoffs: 
  - label: Build Specification
    agent: speckit.specify
    prompt: Implement the feature specification based on the updated constitution. I want to build...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

**Note**: If `.specify/memory/constitution.md` does not exist yet, it should have been initialized from `.specify/templates/constitution-template.md` during project setup. If it's missing, copy the template first.

Follow this execution flow:

1. Load the existing constitution at `.specify/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.
   - For `DEPENDENCY_MATRIX`:
     - Replace with **Markdown table rows** matching the template header.
     - Populate from repo evidence (dependency manifests/lockfiles, build configs, and runtime integrations referenced in code/docs).
     - Include third-party libraries AND intermediary services (SaaS/APIs/queues/caches/etc.).
     - Include transitive dependencies when they are risk-relevant (e.g., license/copyright constraints, security posture, critical intermediaries).
     - If any value is unknown (license/owner/upgrade path), use `TODO(<FIELD>): ...` and list it in the Sync Impact Report.
   - For `ARCHITECTURE_EVIDENCE_INDEX`:
     - Replace with **Markdown table rows** matching the template header.
     - Purpose: provide a repo-derived, evidence-based architectural index that downstream plan/tasks can reference as **single source of truth** (SSOT) for entrypoints and boundaries.
     - Populate from repo evidence (routing/handlers/CLI entrypoints/jobs/events, service boundaries, persistence adapters, external call sites).
     - Each row MUST include:
       - A stable `IndexID` (e.g., `AEI-001`) that downstream artifacts can reference (do not renumber unless meaning changes)
       - Concrete `Entry Point (file:symbol)` when `Status` is `Existing`
       - `Interfaces` (HTTP/CLI/Event/etc.) at the boundary level (high-level only; do not embed full contracts here)
       - `Persistence Touchpoints` (DB tables/collections/queues/caches/etc.) when applicable (may be `Planned/New code`)
       - `Status`: `Existing` or `Planned/New code`
     - You MUST NOT invent “Existing” code paths. If evidence does not exist yet, mark as `Planned/New code`.
     - If any field is unknown, use `TODO(<FIELD>): ...` and list it in the Sync Impact Report.
     - Avoid duplicating detailed call chains here; keep it an index. Detailed, feature-scoped call chains belong in plan/tasks artifacts, but MUST reference `IndexID`s from this index.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist (**read-only audit** — write only when a concrete conflict is confirmed; any writes constitute a Type D amendment and MUST be listed in the Sync Impact Report):
   - Read `.specify/templates/plan-template.md` to verify any "Constitution Check" references still align with updated principles (read-only; do not rewrite unless a direct conflict is confirmed).
   - Read `.specify/templates/spec-template.md` to verify scope/requirements alignment with updated principles (read-only; do not rewrite unless a direct conflict is confirmed).
   - Read `.specify/templates/tasks-template.md` to verify task categorization still reflects principle-driven task types (e.g., observability, versioning, testing discipline) (read-only; do not rewrite unless a direct conflict is confirmed).
   - Read each command file in `.specify/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required (read-only; do not rewrite unless a direct conflict is confirmed).
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present) and note any references to changed principles (read-only; flag in Sync Impact Report for manual follow-up rather than editing inline).
   - **IMPORTANT**: Steps above are read-only audits. Do NOT modify template or command files during this step unless a specific, direct conflict with the updated constitution principles is identified. Any writes to non-constitution files must be listed in the Sync Impact Report as intentional Type D amendments.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).
   - Dependency Matrix is a valid Markdown table (header + separator + 0..N rows).

7. Write the completed constitution back to `.specify/memory/constitution.md` (overwrite).

8. Output a final summary to the user with:
   - New version and bump rationale.
   - Any files flagged for manual follow-up.
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.specify/memory/constitution.md` file.
