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
import httpx, os

# Convert github.com tree URL → api.github.com/repos/.../contents/... 
# Example: https://github.com/owner/repo/tree/main/path/to/skill
#       → https://api.github.com/repos/owner/repo/contents/path/to/skill?ref=main

headers = {}
token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
if token:
    headers["Authorization"] = f"Bearer {token}"

resp = httpx.get(api_url, headers=headers, timeout=15)
if resp.status_code == 401:
    # Do NOT prompt interactively — just fail with a clear message
    raise SystemExit("Private repo: set GH_TOKEN or GITHUB_TOKEN env var and retry.")
if resp.status_code == 403:
    raise SystemExit("Rate limited. Set GH_TOKEN to increase limits (5000 req/hr vs 60).")
resp.raise_for_status()

# Download each file listed in the API response
files = {}  # {filename: content}
for item in resp.json():
    if item["type"] == "file":
        raw = httpx.get(item["download_url"], headers=headers, timeout=15)
        raw.raise_for_status()
        files[item["name"]] = raw.text
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
Original: references/<original-filename>

Usage:
    python wrapper.py [args...]
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "references" / "<original-filename>"


def run(*args: str) -> int:
    """Run the original script with optional arguments."""
    interpreter_map = {
        ".sh": ["bash"],
        ".ps1": ["powershell", "-File"],
        ".js": ["node"],
        ".ts": ["npx", "ts-node"],
        ".rb": ["ruby"],
    }
    ext = SCRIPT.suffix.lower()
    cmd = interpreter_map.get(ext, []) + [str(SCRIPT), *args]
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

### Step 9 — Output Summary

Print a structured summary:

```
✓ Skill standardized:  .agents/skills/<SKILL_NAME>/SKILL.md
✓ Command registered:  templates/commands/<SKILL_NAME>.md
✓ References:          .agents/skills/<SKILL_NAME>/references/<n> file(s)
✓ Python wrappers:     .agents/skills/<SKILL_NAME>/sample_codes/getting-started/wrapper.py  [or "none needed"]
✓ Dependencies added:  <list> [or "none"]

Next steps:
  1. Review .agents/skills/<SKILL_NAME>/SKILL.md — adjust description if needed
  2. Run `uv sync` to install any new dependencies
  3. Run `specify init --ai <agent> --ai-skills` to distribute the new command
```
