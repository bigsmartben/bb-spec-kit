---
description: "Convert PRD documents into a structured Spec (spec.md) with element mapping, conflict detection, and source traceability."
scripts:
  sh: "echo 'Run /sdd.prd2spec inside your AI chat; this command is AI-driven'"
  ps: "Write-Host 'Run /sdd.prd2spec inside your AI chat; this command is AI-driven'"
---

# /sdd.prd2spec — PRD → Spec conversion

**Goal**: Convert one or more PRD documents into a Spec Kit `spec.md` that:

- Is structured and ready for `/sdd.plan`
- Preserves business intent (no premature implementation decisions)
- Provides traceability from each Spec item back to the PRD source
- Detects multi-file conflicts and forces explicit resolution

## Usage

```bash
# Single file (path)
/sdd.prd2spec docs/prd/feature.md

# Single file (@ reference)
/sdd.prd2spec @prd-document.md

# Multi-file merge (mixed formats)
/sdd.prd2spec prd-product.md prd-tech.docx test-cases.txt

# Specify output filename
/sdd.prd2spec prd.md --output spec.md

# Incremental update (base Spec)
/sdd.prd2spec --base spec-v1.0.md prd-v1.1.md --output spec-v1.1.md

# Strict mode (fail if coverage below threshold)
/sdd.prd2spec prd.md --strict

# Output language (optional)
/sdd.prd2spec prd.md --lang en
```

## Inputs

- One or more PRD inputs:
  - Markdown/text file paths (`.md`, `.txt`)
  - Word documents (`.docx`) if the environment supports extraction
  - Editor references (`@file.md`)
  - Or pasted PRD content (when no files are provided)
- Optional:
  - `--output <file>`: target spec filename (filename override only; directory resolution stays aligned with `/sdd.specify`)
  - `--base <spec.md>`: use existing Spec as baseline for incremental updates
  - `--strict`: enforce coverage threshold (see Coverage & Strict Mode)
  - `--lang <en|zh>`: output language preference

## Outputs

- A Spec Kit-compliant `spec.md`
- A conversion report section appended to the Spec:
  - Coverage summary
  - Unmapped items list
  - Conflicts (if any) and their resolutions

## Constitution Evidence Source Policy (MANDATORY)

- Load constitution policy from:
  - Preferred: `.specify/memory/constitution.md`
  - Fallback: `memory/constitution.md`
- Treat `## Evidence Source Policy (ISS-MCP)` as policy SSOT for repository-fact assertions in this command.
- If both constitution files are missing, use the bootstrap policy in `templates/constitution-template.md` and explicitly label conclusions as degraded governance context.
- For repository fact retrieval, call-chain analysis, architecture-boundary verification, dependency mapping, and impact-scope tracing, follow that policy exactly.

## Core workflow

### Step 0: Output path resolution (must align with `/sdd.specify`)

Before content conversion, resolve the final output path using the same directory semantics and numbering rule as `/sdd.specify`:

1. Generate a concise `short-name` (2–4 words, kebab-case) from PRD title/theme.
2. Fetch all remote branches first:
   - `git fetch --all --prune`
3. Find the highest feature number across all sources for the **exact same** `short-name`:
   - Remote branches: `git ls-remote --heads origin | grep -E 'refs/heads/[0-9]+-<short-name>$'`
   - Local branches: `git branch | grep -E '^[* ]*[0-9]+-<short-name>$'`
   - Specs directories: directories matching `specs/[0-9]+-<short-name>`
4. Determine the next available number:
   - Extract numeric prefixes from all three sources
   - Let highest be `N`
   - Use `N+1` as the new feature number
   - If no match exists for this `short-name`, start from `1`
5. Run feature bootstrap script exactly once with both `--number` and `--short-name` to obtain canonical output context:
   - Bash: `scripts/bash/create-new-feature.sh --json --number <N+1> --short-name "<short-name>" "<feature description from PRD>"`
   - PowerShell: `scripts/powershell/create-new-feature.ps1 -Json -Number <N+1> -ShortName "<short-name>" "<feature description from PRD>"`
6. Parse script JSON output and treat `SPEC_FILE` as canonical default target.
7. Handle `--output` strictly as filename override:
   - If `--output` is omitted: write to `SPEC_FILE`.
   - If `--output` is a filename (e.g. `spec-v1.1.md`): write to `<dirname(SPEC_FILE)>/<output filename>`.
   - If `--output` includes a directory component: ignore directory parts and keep only basename under `<dirname(SPEC_FILE)>`.
8. Never write final output to current working directory by default.

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
- UI data dictionary / user-visible data objects (if present)
- Edge cases / failure modes
- Success criteria / acceptance criteria
- Glossary / terminology

If the PRD is unstructured, infer the buckets via section headers and keyword cues, but preserve original text and cite sources.

### Step 3: Mapping rules (PRD → Spec)

Generate `spec.md` using the spec template as the structure baseline:
  - Preferred: `.specify/templates/spec-template.md`
  - Fallback: `templates/spec-template.md`

Mapping guidelines:

- PRD goals/background → Spec `Background`
- PRD user journeys / stories → Spec `User Scenarios & Testing`
- PRD functional requirements → Spec `Functional Requirements` (FR-XXX)
- PRD non-functional requirements → Spec `Non-Functional Requirements` (NFR-XXX) if the template supports it; otherwise place them under `Constraints` or `Success Criteria` in a measurable form
- PRD acceptance/success criteria → Spec `Success Criteria` (SC-XXX)
- PRD user-visible data objects → Spec `UI Data Dictionary (UDD)` (define `Entity.field` items: meaning, calculation/criteria, boundaries, display rules)
- PRD constraints/assumptions → Spec `Assumptions` and `Out of Scope`

**UDD classification rules (required)**:

- Every UDD item MUST include a `Source Type` classification:
  - `System-backed`: the system/interface must provide or confirm the value (should be mappable to at least one contract/VO field downstream)
  - `UI-local`: purely UI-local/derived/display-only (must specify derivation rules; no VO source required)
- Prefer explicit `Key Path` marking:
  - If the PRD indicates priority/critical flows, map them to P1/P2/P3 and mark relevant UDD items accordingly
  - If priority is not provided, leave `Key Path` as `N/A` and avoid inventing priorities

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
