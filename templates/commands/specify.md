---
description: Create or update the feature specification from a natural language feature description.
handoffs: 
  - label: Build Technical Plan
    agent: sdd.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: sdd.clarify
    prompt: Clarify specification requirements
    send: true
scripts:
  sh: scripts/bash/create-new-feature.sh --json "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 -Json "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Constitution Evidence Source Policy (MANDATORY)

- Load constitution policy from:
  - Preferred: `.specify/memory/constitution.md`
  - Fallback: `memory/constitution.md`
- Treat `## Evidence Source Policy (ISS-MCP)` as policy SSOT for repository-fact assertions in this command.
- If both constitution files are missing, use the bootstrap policy in `templates/constitution-template.md` and explicitly label conclusions as degraded governance context.
- For repository fact retrieval, call-chain analysis, architecture-boundary verification, dependency mapping, and impact-scope tracing, follow that policy exactly.

## Script Contract (SSOT)

- Contract file: `scripts/contracts/create-new-feature.json`
- Treat this contract as the authoritative source for script inputs, output keys, and side effects.

## Outline

The text the user typed after `/sdd.specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. **Generate a concise short name** (2-4 words) for context (optional scaffold hint in non-git mode):
   - Analyze the feature description and extract the most meaningful keywords
   - Create a 2-4 word short name that captures the essence of the feature
   - Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug")
   - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)
   - Keep it concise but descriptive enough to understand the feature at a glance
   - Examples:
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **Create spec scaffold via script contract (SSOT)**:

   - Run `{SCRIPT}` exactly once, passing user feature description (and short-name if available).
   - For git repositories, the script MUST use the **currently checked-out local branch name** as `BRANCH_NAME`.
   - For git repositories, the script MUST NOT create branches and MUST NOT switch branches in this phase.
   - For non-git repositories only, the script may use local directory-based fallback naming.

   Examples:

   - Bash: `{SCRIPT} --json --short-name "user-auth" "Add user authentication"`
   - PowerShell: `{SCRIPT} -Json -ShortName "user-auth" "Add user authentication"`

   **IMPORTANT**:
   - In non-git repositories, numbering follows the script-owned **global highest feature number** policy across local `specs/` directories.
   - Do not re-implement numbering logic in this command; trust script-owned numbering policy and script output.
   - Do not re-implement branch/directory resolution logic in this command; trust script output.
   - You must only ever run this script once per feature.
   - The JSON output is authoritative and includes `BRANCH_NAME` and `SPEC_FILE`.
   - For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

3. Load the spec template to understand required sections:
   - Preferred: `.specify/templates/spec-template.md`
   - Fallback: `templates/spec-template.md`

4. Load the project constitution (terminology authority):
   - Preferred: `.specify/memory/constitution.md`
   - Fallback: `memory/constitution.md`
   - If neither exists: WARN and proceed using the default terminology defined in `templates/spec-template.md`,
     but recommend running `/sdd.constitution` first for consistent downstream behavior.

## Output Language & Stability Contract *(MANDATORY)*

Your job is to produce a Spec that is easy to read for Chinese stakeholders **without** introducing semantic drift.

- **Default output language**: Write all *narrative content* in **Simplified Chinese (zh-CN)**.
- **Do NOT translate / do NOT rewrite** any of the following (keep exact tokens/casing/punctuation):
  - Any **Terminology / Terms** definitions from the constitution or the template (keep as the authority; you may add a Chinese gloss after it, but do not change the English term)
  - Requirement identifiers and traceability IDs: `UC-###`, `FR-###`, scenario IDs like `S1`, and any stable IDs you create
  - UDD references: `Entity.field` (treat as stable IDs)
  - Normative keywords: `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`
  - Markers that downstream workflows depend on: `[NEEDS CLARIFICATION: ...]` (keep the marker text in English exactly)
  - File paths, code identifiers, CLI commands, and anything in code fences/backticks
- **Structure stability**: Preserve section order and headings from `templates/spec-template.md` (do not rename headings; only fill content).
- **No leftover placeholders**: Replace all bracket placeholders like `[Actor Name]`, `[Description]`, etc. If something is unknown, make a reasonable assumption or use `[NEEDS CLARIFICATION: ...]` (max 3).

5. Follow this execution flow:

    1. Parse user description from Input
       If empty: ERROR "No feature description provided"
    2. Extract key concepts from description
       Identify: actors, actions, data, constraints
    3. For unclear aspects:
       - Make informed guesses based on context and industry standards
       - Only mark with [NEEDS CLARIFICATION: specific question] if:
         - The choice significantly impacts feature scope or user experience
         - Multiple reasonable interpretations exist with different implications
         - No reasonable default exists
       - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
       - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
    4. Fill User Scenarios & Testing / Acceptance Scenarios section
       If no clear user flow: ERROR "Cannot determine user scenarios"
    5. Generate Functional Requirements
       Each requirement must be testable and concrete (no vague wording)
       Use reasonable defaults for unspecified details (document assumptions in Assumptions section)
       For each `FR-###` entry in **3.3 Functional Requirements**, include at minimum:
       - `Capability`: one sentence starting with `System MUST/SHOULD/MAY ...`
       - `Given/When/Then (minimum)`: a minimal, testable behavioral assertion
       - `UDD (user-visible data) refs`: list relevant `Entity.field` items
         - `Reads/Displays`: what the user sees/relies on in this FR
         - `Writes/Updates`: what becomes user-visible or changes (ensure § 1.3 UDD is updated accordingly)
       - `Failure / edge behavior`: at least one failure condition and expected outcome (ref `EC-###` if defined globally)
    6. Define Success Criteria
       Create measurable, technology-agnostic outcomes
       Include both quantitative metrics (time, performance, volume) and qualitative measures (user satisfaction, task completion)
       Each criterion must be verifiable without implementation details
    7. Identify the **UI Data Dictionary (UDD)** (if user-visible information is involved):
       - Use the Spec template's UDD section structure
       - Define UDD items at the `Entity.field` level (meaning, calculation/criteria, boundaries, display rules)
       - Classify every UDD item:
         - `Source Type`: `System-backed` vs `UI-local`
         - `Key Path`: `P1/P2/P3/N/A` (prefer explicit marking; do not invent priorities if none are provided)
    8. Return: SUCCESS (spec ready for planning)

5. Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the feature description (arguments) while preserving section order and headings.

   - Ensure `## Artifacts Overview & Navigation` is present near the top and uses working relative links (no anchor links).
   - Do NOT add any status tracking here and do NOT claim downstream artifacts are already generated.

6. **Specification Quality Validation**: After writing the initial spec, validate it against quality criteria:

   a. **Create Spec Quality Checklist**: Create/overwrite `FEATURE_DIR/checklists/requirements.md` by loading and applying `templates/checklist-template.md`.

      - Set checklist metadata fields to:
        - `CHECKLIST TYPE`: `Specification Quality`
        - `FEATURE NAME`: feature name derived from `SPEC_FILE`
        - `Purpose`: `Validate specification completeness and quality before proceeding to planning`
        - `Created`: current date
        - `Feature`: relative link to `SPEC_FILE`
      - Preserve the checklist section/item structure from the template exactly; do not inline or redefine checklist item text in this command.

   b. **Run Validation Check**: Review the spec against each checklist item:
      - For each item, determine if it passes or fails
      - Document specific issues found (quote relevant spec sections)

   c. **Handle Validation Results**:

      - **If all items pass**: Mark every checklist item as `[x]` and proceed to step 8

      - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List the failing items and specific issues
        2. Update the spec to address each issue
        3. Re-run validation until all items pass (max 3 iterations)
        4. If still failing after 3 iterations, document remaining issues in checklist notes and warn user

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. **LIMIT CHECK**: If more than 3 markers exist, keep only the 3 most critical (by scope/security/UX impact) and make informed guesses for the rest
        3. For each clarification needed (max 3), present options to user in this format:

           ```markdown
           ## Question [N]: [Topic]
           
           **Context**: [Quote relevant spec section]
           
           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]
           
           **Suggested Answers**:
           
           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |
           
           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - Table Formatting**: Ensure markdown tables are properly formatted:
           - Use consistent spacing with pipes aligned
           - Each cell should have spaces around content: `| Content |` not `|Content|`
           - Header separator must have at least 3 dashes: `|--------|`
           - Test that the table renders correctly in markdown preview
        5. Number questions sequentially (Q1, Q2, Q3 - max 3 total)
        6. Present all questions together before waiting for responses
        7. Wait for user to respond with their choices for all questions (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
        8. Update the spec by replacing each [NEEDS CLARIFICATION] marker with the user's selected or provided answer
        9. Re-run validation after all clarifications are resolved

   d. **Update Checklist**: After each validation iteration, write status back to `FEATURE_DIR/checklists/requirements.md`:
      - Mark each passing item as `- [x]`
      - Mark each failing item as `- [ ]`
      - Preserve the original item order and IDs (do not duplicate or renumber items)
      - Add concise notes for unresolved failures

8. Report completion with branch name, spec file path, checklist results, and readiness for the next phase (`/sdd.clarify` or `/sdd.plan`).
   - Also suggest reviewer workflow command: `/sdd.preview` (generates reviewer-facing `preview.html` after artifacts are available).

**NOTE:** In git repositories, this script does **not** create/switch branches. It initializes the spec scaffold under `specs/<current-branch>/`.

## General Guidelines

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.
- DO NOT embed checklists inside `spec.md`; keep them as standalone files under `FEATURE_DIR/checklists/`.

### Section Requirements

- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation

When creating this spec from a user prompt:

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
2. **Document assumptions**: Record reasonable defaults in the Assumptions section
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers - use only for critical decisions that:
   - Significantly impact feature scope or user experience
   - Have multiple reasonable interpretations with different implications
   - Lack any reasonable default
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
5. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
6. **Common areas needing clarification** (only if no reasonable default exists):
   - Feature scope and boundaries (include/exclude specific use cases)
   - User types and permissions (if multiple conflicting interpretations possible)
   - Security/compliance requirements (when legally/financially significant)

**Examples of reasonable defaults** (don't ask about these):

- Data retention: Industry-standard practices for the domain
- Performance targets: Standard web/mobile app expectations unless specified
- Error handling: User-friendly messages with appropriate fallbacks
- Authentication method: Standard session-based or OAuth2 for web apps
- Integration patterns: Use project-appropriate patterns (REST/GraphQL for web services, function calls for libraries, CLI args for tools, etc.)

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective, not system internals
4. **Verifiable**: Can be tested/validated without knowing implementation details

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"

**Bad examples** (implementation-focused):

- "API response time is under 200ms" (too technical, use "Users see results instantly")
- "Database can handle 1000 TPS" (implementation detail, use user-facing metric)
- "React components render efficiently" (framework-specific)
- "Redis cache hit rate above 80%" (technology-specific)
