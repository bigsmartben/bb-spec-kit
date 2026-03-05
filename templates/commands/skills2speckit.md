---
description: "Convert any agent skill (local path or GitHub URL) into standard Spec-Kit format and register it as a distributable speckit command."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

### Step 1 — Parse Input

Parse `$ARGUMENTS` to determine the skill source.

**Supported formats:**

| Format | Example |
|--------|---------|
| Local relative path | `./my-skill` or `my-skills/some-skill` |
| Local absolute path | `/home/user/skills/my-skill` |
| GitHub tree URL | `https://github.com/owner/repo/tree/branch/path/to/skill` |
| GitHub raw SKILL.md URL | `https://raw.githubusercontent.com/owner/repo/branch/path/SKILL.md` |

If no input: **ERROR** — "Usage: /speckit.skills2speckit <local-path or GitHub URL>"

Extract from input:
- `SOURCE_TYPE`: `local` or `github`
- `SKILL_NAME`: last path segment, normalized to `kebab-case`
- `COMMAND_NAME`: `speckit.<SKILL_NAME>`
- `OUTPUT_DIR`: `.agents/skills/<SKILL_NAME>/` (relative to current project root)

---

### Step 2 — Ingest Skill Files

#### Local path mode

Read all files from the given directory:

```python
from pathlib import Path
source = Path("<resolved-local-path>")
files = {f.name: f.read_text(encoding="utf-8") for f in source.rglob("*") if f.is_file()}
```

#### GitHub URL mode

Convert the GitHub URL to a raw-content API call using `httpx` (already available — no new install needed):

```python
import httpx, os, re, urllib.parse

headers = {}
token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
if token:
    headers["Authorization"] = f"Bearer {token}"

files = {}  # {filename: content}

# Case 1: raw.githubusercontent.com single-file URL
if "raw.githubusercontent.com" in input_url:
    # Example: https://raw.githubusercontent.com/owner/repo/branch/path/SKILL.md
    filename = input_url.split("/")[-1]
    resp = httpx.get(input_url, headers=headers, timeout=15)
    if resp.status_code == 401:
        raise SystemExit("Private repo: set GH_TOKEN or GITHUB_TOKEN env var and retry.")
    if resp.status_code == 403:
        raise SystemExit("Rate limited. Set GH_TOKEN to increase limits (5000 req/hr vs 60).")
    resp.raise_for_status()
    files[filename] = resp.text

# Case 2: github.com/owner/repo/tree/branch/path tree URL (directory)
else:
    # Parse: https://github.com/owner/repo/tree/branch/path/to/skill
    # Convert to: https://api.github.com/repos/owner/repo/contents/path/to/skill?ref=branch
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.*)", input_url)
    if not match:
        raise SystemExit(f"Invalid GitHub URL format: {input_url}")
    owner, repo, branch, path = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    
    # Recursive fetch: use a queue to process all levels
    queue = [api_url]
    while queue:
        current_url = queue.pop(0)
        resp = httpx.get(current_url, headers=headers, timeout=15)
        if resp.status_code == 401:
            raise SystemExit("Private repo: set GH_TOKEN or GITHUB_TOKEN env var and retry.")
        if resp.status_code == 403:
            raise SystemExit("Rate limited. Set GH_TOKEN to increase limits (5000 req/hr vs 60).")
        resp.raise_for_status()
        
        for item in resp.json():
            if item["type"] == "file":
                raw = httpx.get(item["download_url"], headers=headers, timeout=15)
                raw.raise_for_status()
                files[item["name"]] = raw.text
            elif item["type"] == "dir":
                # Queue subdirectory for processing
                queue.append(item["url"])
```

---

### Step 3 — Analyze Existing Skill

Inspect collected files:

1. **SKILL.md present?**
   - Yes → parse existing frontmatter with `yaml.safe_load()`
   - No → infer `name` and `description` from README.md or directory name
2. **Detect script languages** — look for files ending in `.sh`, `.ps1`, `.js`, `.ts`, `.rb`, `.go`, `.rs`
3. **Detect Python dependencies** — scan all `.py` files for top-level `import <pkg>` (skip stdlib modules: `os`, `sys`, `re`, `pathlib`, `subprocess`, `json`, `shutil`, `typing`, `datetime`, `tempfile`, `zipfile`, `ssl`)
4. **Check structure conformance** — does the skill already have `references/` and `sample_codes/` subdirectories?

---

### Step 4 — Generate Standardized SKILL.md

Build the new `SKILL.md` content:

**Required frontmatter (always include all three fields):**

```yaml
---
name: <kebab-case SKILL_NAME>
description: <one-sentence trigger description — what user tasks activate this skill>
compatibility: requires-python >=3.11
---
```

**Required body sections (in this order):**

```markdown
# <Skill Display Name>

<One-paragraph purpose statement>

## Key Concepts

- **<Concept 1>**: <explanation>
- **<Concept 2>**: <explanation>
- **<Concept 3>**: <explanation>

## Workflow Steps

1. <step>
2. <step>
...

## Learn More

| Topic | How to Find |
|-------|-------------|
| ... | ... |
```

Rules for filling content:
- Extract key concepts from existing skill documentation
- Preserve all original workflow logic — do not simplify or omit steps
- If original has code samples, include the most representative one inline
- Keep `description` to ≤ 120 characters (it determines when the skill activates)
- Write in the same language as the original skill; add Chinese (zh-CN) glosses only if the original is in English

---

### Step 5 — Convert Non-Python Scripts

For each non-Python script file detected in Step 3:

1. **Copy** it to `OUTPUT_DIR/references/<filename>` (never delete the original)
2. **Generate** `OUTPUT_DIR/sample_codes/getting-started/wrapper.py` using this template:

```python
"""Python wrapper for <original-filename>.
Compatible with Python >=3.11
Original: ../references/<original-filename>
(Relative path from sample_codes/getting-started/wrapper.py → .agents/skills/<SKILL_NAME>/references/)

Usage:
    python wrapper.py [args...]
"""
import subprocess
import sys
from pathlib import Path

# Navigate: ./wrapper.py → ../ (getting-started) → ../ (sample_codes) → ../ (SKILL_NAME) → references/
SCRIPT = Path(__file__).parent.parent.parent / "references" / "<original-filename>"


def run(*args: str) -> int:
    """Run the original script with optional arguments."""
    interpreter_map = {
        ".sh": ["bash"],
        ".ps1": ["powershell", "-File"],
        ".js": ["node"],
        ".ts": ["npx", "ts-node"],
        ".rb": ["ruby"],
        # Note: .go and .rs files must be compiled first; copy to references only
    }
    ext = SCRIPT.suffix.lower()
    if ext not in interpreter_map:
        raise SystemExit(f"Unsupported script type: {ext}. Ensure {SCRIPT} is executable or compiles in target environment.")
    cmd = interpreter_map[ext] + [str(SCRIPT), *args]
    result = subprocess.run(cmd, check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(run(*sys.argv[1:]))
```

If the skill is **already pure Python**, skip this step (no wrapper needed).

---

### Step 6 — Manage Python Dependencies

1. Read `pyproject.toml` from the **current project root**
2. Parse the `[project.dependencies]` list with `tomllib` (Python >=3.11 stdlib — no install needed):

```python
import tomllib
from pathlib import Path

pyproject = Path("pyproject.toml")
with pyproject.open("rb") as f:
    data = tomllib.load(f)

existing_deps = set(data.get("project", {}).get("dependencies", []))
```

3. For each new Python package not already present (exact name match, case-insensitive):
   - Append `"<package>>=<current-stable-version>"` to the list
   - Use conservative lower bounds — prefer `>=X.Y` over `==X.Y` to avoid lock-in
   - Verify the version constraint is Python `>=3.11` safe (e.g., no package requiring `>=3.12`)
4. **Never reorder or remove** existing entries
5. Write back only if anything was added
6. After writing, append this note to the command output:

   > Dependencies updated in `pyproject.toml`. Run `uv sync` to install them.

---

### Step 7 — Write Output Files

Create the following files (create directories as needed):

```
.agents/skills/<SKILL_NAME>/
├── SKILL.md                          ← generated in Step 4
├── references/
│   └── <original-non-python-files>   ← copied in Step 5 (if any)
└── sample_codes/
    └── getting-started/
        └── wrapper.py                ← generated in Step 5 (if any)

templates/commands/<SKILL_NAME>.md    ← generated in Step 8
```

**Do NOT overwrite** an existing `SKILL.md` without warning. If `.agents/skills/<SKILL_NAME>/SKILL.md` already exists:
- Warn: "Skill `<SKILL_NAME>` already exists. Overwrite? (Proceeding — use git to revert if unintended.)"
- Proceed anyway (non-interactive — do not ask the user for confirmation)

---

### Step 8 — Generate speckit Command Template

Create `templates/commands/<SKILL_NAME>.md`:

```markdown
---
description: "<copy of SKILL.md description field — must match exactly>"
---

## User Input

\`\`\`text
$ARGUMENTS
\`\`\`

You **MUST** consider the user input before proceeding (if not empty).

## Outline

<Extract and adapt the workflow steps from the standardized SKILL.md>
<Rewrite each step as an imperative instruction for the AI agent>
<Keep all technical details, file paths, and commands intact>
```

Rules:
- The `description` field **must** exactly match the `description` in the new `SKILL.md`
- Include `$ARGUMENTS` as the first content block (required placeholder)  
- Convert Skill workflow steps (informational) → command steps (imperative)
- Reference `{SCRIPT}` if the skill involves running scripts: `scripts:` block in frontmatter

---

### Step 9 — Detect Workspace Agents and Sync Command Entrypoints

Goal: make `/speckit.<SKILL_NAME>` usable in the **current workspace immediately**, without requiring a full re-init.

Use this agent registry (aligned with spec-kit conventions):

| Agent Key | Command Entrypoint Directory | Output Format |
|-----------|------------------------------|---------------|
| `claude` | `.claude/commands/` | Markdown `.md` |
| `gemini` | `.gemini/commands/` | TOML `.toml` |
| `copilot` | `.github/agents/` | Markdown `.md` |
| `cursor-agent` | `.cursor/commands/` | Markdown `.md` |
| `qwen` | `.qwen/commands/` | TOML `.toml` |
| `opencode` | `.opencode/command/` | Markdown `.md` |
| `codex` | `.codex/commands/` | Markdown `.md` |
| `windsurf` | `.windsurf/workflows/` | Markdown `.md` |
| `kilocode` | `.kilocode/rules/` | Markdown `.md` |
| `auggie` | `.augment/rules/` | Markdown `.md` |
| `roo` | `.roo/rules/` | Markdown `.md` |
| `codebuddy` | `.codebuddy/commands/` | Markdown `.md` |
| `qodercli` | `.qoder/commands/` | Markdown `.md` |
| `q` | `.amazonq/prompts/` | Markdown `.md` |
| `amp` | `.agents/commands/` | Markdown `.md` |
| `shai` | `.shai/commands/` | Markdown `.md` |
| `bob` | `.bob/commands/` | Markdown `.md` |

Detection and sync rules:

1. Detect active agents by checking whether each agent root directory already exists in the workspace.
2. Read canonical source command from `templates/commands/<SKILL_NAME>.md`.
3. For each detected agent, generate `COMMAND_NAME` in agent-native format:
   - **Markdown agents** (claude, copilot, cursor-agent, opencode, codex, windsurf, kilocode, auggie, roo, codebuddy, qodercli, q, amp, shai, bob): write `<entrypoint>/speckit.<SKILL_NAME>.md` with `$ARGUMENTS` placeholder intact.
   - **TOML agents** (gemini, qwen): write `<entrypoint>/speckit.<SKILL_NAME>.toml`, convert `$ARGUMENTS` → `{{args}}`, render as:

```toml
description = "<same description>"

prompt = """
<command content>
"""
```

4. Create missing subdirectories under detected agent roots as needed.
5. If target command file already exists, warn and overwrite (non-interactive).
6. If no agent roots are detected, warn clearly and keep generated canonical files (`SKILL.md` + `templates/commands/<SKILL_NAME>.md`) as the source of truth.

---

### Step 10 — Output Summary

Print a structured summary:

```
✓ Skill standardized:  .agents/skills/<SKILL_NAME>/SKILL.md
✓ Command registered:  templates/commands/<SKILL_NAME>.md
✓ Command name:        speckit.<SKILL_NAME>
✓ Detected agents:     <list> [or "none"]
✓ Entrypoints synced:  <per-agent output paths> [or "none"]
✓ References:          .agents/skills/<SKILL_NAME>/references/<n> file(s)
✓ Python wrappers:     .agents/skills/<SKILL_NAME>/sample_codes/getting-started/wrapper.py  [or "none needed"]
✓ Dependencies added:  <list> [or "none"]

Next steps:
  1. Review .agents/skills/<SKILL_NAME>/SKILL.md and templates/commands/<SKILL_NAME>.md
  2. Run `/speckit.<SKILL_NAME> ...` in a detected agent workspace
  3. If no agent was detected, initialize one agent workspace (for example `specify init --ai codex --here`) and rerun `/speckit.skills2speckit`
  4. Run `uv sync` only if dependencies were added
```
