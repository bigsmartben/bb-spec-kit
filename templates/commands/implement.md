---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Scan all checklist files in the checklists/ directory
   - For each checklist, count:
     - Total items: All lines matching `- [ ]` or `- [X]` or `- [x]`
     - Completed items: Lines matching `- [X]` or `- [x]`
     - Incomplete items: Lines matching `- [ ]`
   - Create a status table:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - Calculate overall status:
     - **PASS**: All checklists have 0 incomplete items
     - **FAIL**: One or more checklists have incomplete items

   - **If any checklist is incomplete**:
     - Display the table with incomplete item counts
     - **STOP** and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
     - Wait for user response before continuing
     - If user says "no" or "wait" or "stop", halt execution
     - If user says "yes" or "proceed" or "continue", proceed to step 3

   - **If all checklists are complete**:
     - Display the table showing all checklists passed
     - Automatically proceed to step 3

3. Load and validate the implementation context (fail fast):
   - **REQUIRED**: Read `tasks.md` for the complete task list, Interface Inventory, and Task DAG
   - **REQUIRED**: Read `plan.md` for tech stack, architecture, and file structure
   - **REQUIRED**: Read `data-model.md` for entities, relationships, and state machines
     - If `data-model.md` is missing: **ERROR** and STOP (design is incomplete)
   - **REQUIRED**: Ensure `contracts/` exists and is non-empty
     - If `contracts/` is missing or empty: **ERROR** and STOP (design is incomplete)
   - **OPTIONAL**: `research.md`
     - If it exists, read it ONLY when needed for a specific task (e.g., a task references a decision/rationale)
     - Do NOT create new design artifacts during `speckit.implement` unless explicitly required by `tasks.md`
   - **OPTIONAL**: `quickstart.md`
     - Use it only for verification tasks (or when `tasks.md` explicitly references it)

4. **Project Setup Verification** (global / shared-worktree only):
   - **REQUIRED**: Create/verify ignore files based on actual project setup:

   **Detection & Creation Logic**:
   - Check if the following command succeeds to determine if the repository is a git repo (create/verify .gitignore if so):

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - Check if Dockerfile* exists or Docker in plan.md → create/verify .dockerignore
   - Check if .eslintrc* exists → create/verify .eslintignore
   - Check if eslint.config.* exists → ensure the config's `ignores` entries cover required patterns
   - Check if .prettierrc* exists → create/verify .prettierignore
   - Check if .npmrc or package.json exists → create/verify .npmignore (if publishing)
   - Check if terraform files (*.tf) exist → create/verify .terraformignore
   - Check if .helmignore needed (helm charts present) → create/verify .helmignore

   **If ignore file already exists**: Verify it contains essential patterns, append missing critical patterns only
   **If ignore file missing**: Create with full pattern set for detected technology

   **Common Patterns by Technology** (from plan.md tech stack):
   - **Node.js/JavaScript/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
   - **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
   - **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
   - **Ruby**: `.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
   - **PHP**: `vendor/`, `*.log`, `*.cache`, `*.env`
   - **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
   - **Kotlin**: `build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
   - **C++**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
   - **C**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `Makefile`, `config.log`, `.idea/`, `*.log`, `.env*`
   - **Swift**: `.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
   - **R**: `.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
   - **Universal**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

   **Tool-Specific Patterns**:
   - **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
   - **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
   - **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
   - **Kubernetes/k8s**: `*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

5. Parse `tasks.md` into an execution model (Interface-scoped + DAG-driven):
   - **REQUIRED**: Extract **Interface Inventory** and build a map: `IFxx -> {contracts, interface_details, verification_refs}`
     - Prefer explicit contract paths listed per interface section
     - For HTTP API features: map `operationId` to `contracts/interface-details/<operationId>.md` (load only those relevant to the current IF)
   - **REQUIRED**: Extract the full task list with fields:
     - Task ID (T###), `[P]` marker, `Type:*`, optional `[IFxx]`, and all file paths (or `N/A`)
   - **REQUIRED**: Extract **Task DAG (Adjacency List)** and build a dependency graph
     - If the adjacency list is missing/unparseable: **ERROR** and STOP (rerun `/speckit.tasks`)
   - Compute a **ready-queue**:
     - A task is `READY` iff all its dependency tasks are completed (`[X]`)

6. Worktree model and Interface-parallel execution (default):
   - **Parallel unit = Interface (`IFxx`)**
     - Each interface SHOULD be developed in its own worktree/branch (independent iteration)
     - Within a single interface, follow DAG ordering; only tasks marked `[P]` may run in parallel (subject to file conflicts)
   - **Worktree tasks are REQUIRED**
     - Each `IFxx` MUST have an explicit worktree/branch enablement task (typically `Type:Infra [IFxx]`)
     - If an interface has no worktree task: **ERROR** and STOP (rerun `/speckit.tasks`)
   - **Naming rule**
     - Follow `tasks.md` worktree naming exactly when specified
     - If `tasks.md` does not specify names, use: `<feature-spec-branch>-<ifxx>` (e.g., `123-my-feature-if03`)
       - `feature-spec-branch` = the feature branch name referenced by the spec/worktree workflow
       - `<ifxx>` is lowercase (`if01`, `if02`, ...)
   - **Global/shared tasks**
     - Tasks with no `[IFxx]` label, or tasks that modify shared repo-wide files, MUST run in the shared/base worktree before starting interface-parallel batches

7. Scheduling algorithm (strict ready-queue from Task DAG adjacency list):
   - Repeat until all tasks are completed:
     1) Recompute `READY` tasks from the DAG adjacency list (all deps completed)
     2) Form a **parallel batch** from `READY` tasks using these constraints:
        - Prefer maximizing parallelism across different `IFxx` (different worktrees)
        - Within the same `IFxx`, only include multiple tasks in the same batch if they are marked `[P]`
        - Never batch tasks that touch the same file paths (treat any overlap as a conflict)
        - Treat repo-wide/shared paths as conflicts across all interfaces (serialize), e.g.:
          - `.github/`, CI configs, top-level configs, shared libraries/modules, `tasks.md`, `plan.md`
        - If conflict detection is uncertain, serialize (correctness > speed)
     3) Print the planned batch BEFORE execution as a concise table:
        - columns: `Task`, `IF`, `Worktree`, `DependsOn`, `Paths`
     4) Execute the batch:
        - For each interface in the batch, ensure the worktree/branch is active
        - Apply **Interface-scoped context** (below) before executing that interface’s tasks
     5) After each task completes, immediately mark it `[X]` in `tasks.md`

8. Progress tracking and error handling:
   - Report progress after each completed task
   - Halt execution if any non-parallel task fails
   - For parallel tasks [P], continue with successful tasks, report failed ones
   - Provide clear error messages with context for debugging
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT** For completed tasks, make sure to mark the task off as [X] in the tasks file.

9. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

## Interface-scoped context (MANDATORY for `[IFxx]` tasks)

Before executing any task tagged with a specific interface `[IFxx]`, you MUST build and use an "Interface Context Packet" for that interface:

- Always include:
  - The `IFxx` section from `tasks.md` (goal, served stories, definition of done, interface-local task list)
  - The global `plan.md`
  - The global `data-model.md`
- Include ONLY the interface’s relevant contract material:
  - Contract doc(s) referenced by the `IFxx` section / Interface Inventory (do not load other interfaces’ contracts)
  - If `contracts/openapi.yaml` exists:
    - Load ONLY the `paths`/operations whose `operationId` belong to this `IFxx` (do not load unrelated endpoints)
  - If `contracts/interface-details/` exists:
    - Load ONLY `contracts/interface-details/<operationId>.md` files relevant to this `IFxx`
- For verification tasks (`Type:Test`):
  - Load ONLY the relevant portion(s) of `quickstart.md` referenced by the interface or task
  - If `contracts/test-case-matrix.md` exists:
    - Preferred: Load ONLY the rows for the concrete `CaseID`s referenced by the test task
    - Otherwise: Load ONLY the rows relevant to this interface’s `operationId` / contract
    - Treat the loaded rows as the acceptance criteria for implementing the test (inputs/expected outputs/mocks/fixtures)
    - If the task references `CaseID`s that cannot be found in the matrix: **ERROR** and STOP (regenerate via `/speckit.plan` or `/speckit.tasks`)

You MUST NOT load unrelated interface documents "just in case". Keep the context minimal and interface-scoped.

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/speckit.tasks` first to regenerate the task list.
