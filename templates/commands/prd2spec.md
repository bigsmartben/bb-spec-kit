---
description: "Convert PRD documents into a structured Spec (spec.md) with element mapping, conflict detection, and source traceability."
scripts:
  sh: "echo 'Run /speckit.prd2spec inside your AI chat; this command is AI-driven'"
  ps: "Write-Host 'Run /speckit.prd2spec inside your AI chat; this command is AI-driven'"
---

# /speckit.prd2spec — PRD → Spec conversion

**Goal**: Convert one or more PRD documents into a Spec Kit `spec.md` that:

- Is structured and ready for `/speckit.plan`
- Preserves business intent (no premature implementation decisions)
- Provides traceability from each Spec item back to the PRD source
- Detects multi-file conflicts and forces explicit resolution

## Usage

```bash
# Single file (path)
/speckit.prd2spec docs/prd/feature.md

# Single file (@ reference)
/speckit.prd2spec @prd-document.md

# Multi-file merge (mixed formats)
/speckit.prd2spec prd-product.md prd-tech.docx test-cases.txt

# Specify output filename
/speckit.prd2spec prd.md --output spec.md

# Incremental update (base Spec)
/speckit.prd2spec --base spec-v1.0.md prd-v1.1.md --output spec-v1.1.md

# Strict mode (fail if coverage below threshold)
/speckit.prd2spec prd.md --strict

# Output language (optional)
/speckit.prd2spec prd.md --lang en
```

## Inputs

- One or more PRD inputs:
  - Markdown/text file paths (`.md`, `.txt`)
  - Word documents (`.docx`) if the environment supports extraction
  - Editor references (`@file.md`)
  - Or pasted PRD content (when no files are provided)
- Optional:
  - `--output <file>`: target spec filename
  - `--base <spec.md>`: use existing Spec as baseline for incremental updates
  - `--strict`: enforce coverage threshold (see Coverage & Strict Mode)
  - `--lang <en|zh>`: output language preference

## Outputs

- A Spec Kit-compliant `spec.md`
- A conversion report section appended to the Spec:
  - Coverage summary
  - Unmapped items list
  - Conflicts (if any) and their resolutions

## Core workflow

### Step 1: Input detection and loading

1. Detect input mode:
   - Multi-file mode if multiple inputs are provided
   - File mode if a file path is provided
   - Reference mode if `@...` is provided
   - Paste mode if the user pasted PRD content
2. Load content:
   - `.md` / `.txt`: read as plain text and preserve line numbers
   - `.docx`: extract headings, paragraphs, and tables
     - If `.docx` extraction is not possible, request the user to provide a Markdown export of the PRD

### Step 2: PRD structure normalization

Normalize PRD content into canonical buckets (best-effort):

- Background / Goals
- In Scope / Out of Scope
- Users / Roles / Permissions
- User journeys / user stories
- Functional requirements
- Non-functional requirements
- Constraints / assumptions
- Data and key entities (if present)
- Edge cases / failure modes
- Success criteria / acceptance criteria
- Glossary / terminology

If the PRD is unstructured, infer the buckets via section headers and keyword cues, but preserve original text and cite sources.

### Step 3: Mapping rules (PRD → Spec)

Generate `spec.md` using `templates/spec-template.md` as the structure baseline.

Mapping guidelines:

- PRD goals/background → Spec `Background`
- PRD user journeys / stories → Spec `User Scenarios & Testing`
- PRD functional requirements → Spec `Functional Requirements` (FR-XXX)
- PRD non-functional requirements → Spec `Non-Functional Requirements` (NFR-XXX) if the template supports it; otherwise place them under `Constraints` or `Success Criteria` in a measurable form
- PRD acceptance/success criteria → Spec `Success Criteria` (SC-XXX)
- PRD data objects → Spec `Key Entities` (define names, fields, constraints at a business level)
- PRD constraints/assumptions → Spec `Assumptions` and `Out of Scope`

**Do not prematurely implement**:

- MUST NOT: introduce endpoints, HTTP methods, database schemas, locks, or specific frameworks unless the PRD explicitly mandates them as a hard constraint.
- SHOULD: capture mandated vendor/service constraints as governance constraints (still cite the PRD).

### Step 4: Traceability (source links)

Every generated item that comes from the PRD MUST include a source pointer.

Use this format:

- `origin: <file>:L<start>-L<end>` for text files
- `origin: <file>:P<page>` (or `origin: <file>:Section "<heading>"`) for `.docx` when exact lines are unavailable

Examples:

- `origin: prd.md:L120-L138`
- `origin: prd-tech.docx:P12`

### Step 5: Coverage & strict mode

Compute coverage as: mapped items / total recognized PRD items (per bucket and overall).

- If `--strict` is enabled:
  - If overall coverage < 95%: **FAIL** and do not output a final Spec
  - Instead, output a review report with:
    - Unmapped items list
    - Suggested missing Spec sections
    - Top 5 clarification questions

### Step 6: Multi-file merge and conflict handling

When multiple PRDs are provided:

- De-duplicate equivalent requirements (same intent)
- Detect conflicts:
  - Same requirement with different constraints (e.g., different limits)
  - Same entity field with different meaning/rules
  - Different success criteria for the same user journey
- For each conflict:
  - List conflicting sources (with origin pointers)
  - Propose a resolution and ask for confirmation if the choice impacts scope or user experience
  - If unresolved: mark as `[NEEDS CLARIFICATION: ...]` (limit to 3 critical clarifications total)

### Step 7: Incremental update (`--base`)

If `--base` is provided:

- Preserve existing IDs (FR/NFR/SC) where the semantics match
- Only add new IDs for truly new requirements
- If an existing item changes meaning, treat it as a modification and record it in a `Change Log` section

## Failure conditions (block output)

- Conflicts remain unresolved in strict mode
- Coverage below threshold in strict mode
- Spec contains significant implementation details that were not mandated by the PRD

## Final checklist (before responding)

- Spec is complete and uses the Spec template structure
- Each generated requirement is testable and unambiguous
- Each generated item has an `origin:` pointer
- No more than 3 `[NEEDS CLARIFICATION]` markers remain
- No unintended implementation details were introduced

