---
name: skills2speckit
description: Convert any agent skill (local path or GitHub URL) into standard Spec-Kit SKILL.md format and register it as a distributable speckit command. Use when you want to package a new skill into the speckit ecosystem, standardize an external skill, convert non-Python scripts to Python wrappers, or add new capabilities to the speckit command library.
compatibility: requires-python >=3.11
---

# skills2speckit

Converts any AI agent skill into the standard Spec-Kit format and registers it as a distributable speckit command under `templates/commands/<name>.md`.

## What This Skill Does

1. **Ingests** a skill from a local directory path or a GitHub URL
2. **Standardizes** it to the Spec-Kit `SKILL.md + references/ + sample_codes/` structure
3. **Converts** non-Python scripts to Python wrappers (retaining originals in `references/`)
4. **Manages dependencies** — new Python packages are appended to `pyproject.toml [project.dependencies]` with `>=3.11`-compatible constraints; `uv sync` handles installation silently
5. **Registers** the skill as a speckit command by generating `templates/commands/<name>.md`

Output is written to the **user's current project** under `.agents/skills/<name>/`.

---

## Input Formats

### Local path
```
/speckit.skills2speckit ./path/to/skill-dir
/speckit.skills2speckit /absolute/path/to/skill-dir
```

### GitHub URL (public or private repo)
```
/speckit.skills2speckit https://github.com/owner/repo/tree/branch/path/to/skill
/speckit.skills2speckit https://raw.githubusercontent.com/owner/repo/branch/path/to/SKILL.md
```
For private repos, set `GH_TOKEN` or `GITHUB_TOKEN` environment variable. No user prompts — the skill reads it silently.

---

## Standard Output Structure

```
.agents/skills/<name>/
├── SKILL.md               # Standardized frontmatter + knowledge content
├── references/            # Original scripts/docs preserved here
│   └── original-script.*  # Non-Python scripts kept as reference
└── sample_codes/
    └── getting-started/
        └── wrapper.py     # Python equivalent of any non-Python entry point

templates/commands/<name>.md   # Registered as distributable speckit command
```

---

## Standardization Rules

### SKILL.md Frontmatter (required fields)
```yaml
---
name: <kebab-case-name>
description: <one-line trigger description — what tasks activate this skill>
compatibility: requires-python >=3.11   # always include
---
```

### SKILL.md Body (required sections)
- **Purpose** — one paragraph, what the skill does
- **Key Concepts** — 3-5 bullet points
- **Workflow Steps** — numbered procedure
- **Learn More** — search queries or doc links for deeper topics

### Non-Python Script Conversion

| Original type | Action |
|---------------|--------|
| bash/shell `.sh` | Generate `sample_codes/getting-started/wrapper.py` using `subprocess` |
| PowerShell `.ps1` | Generate Python wrapper using `subprocess` with `powershell -File` |
| Node.js `.js/.ts` | Generate Python wrapper using `subprocess`; note npm dependency |
| Ruby/Go/etc. | Generate Python wrapper using `subprocess` |

Original scripts are **always copied** to `references/` — never deleted.

Python wrapper template:
```python
"""Python wrapper for <original-script>.
Compatible with Python >=3.11
Original: references/<original-script>
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "references" / "<original-script>"


def run(*args: str) -> int:
    result = subprocess.run(
        ["<interpreter>", str(SCRIPT), *args],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(run(*sys.argv[1:]))
```

### Dependency Management Rules

- Scan skill content for `import <pkg>` / `require('<pkg>')` patterns
- For each new Python package not already in `pyproject.toml`:
  - Append to `[project.dependencies]` with `>=<current-stable-version>`
  - Verify constraint is `>=3.11`-safe (no `match` statements, no `3.12+` syntax)
- **Never remove or reorder** existing dependencies
- After writing `pyproject.toml`, instruct user to run: `uv sync` (no confirmation needed)

---

## speckit Command Template Format

The generated `templates/commands/<name>.md` must follow this pattern:

```markdown
---
description: <one-line description matching SKILL.md description>
---

## User Input

\`\`\`text
$ARGUMENTS
\`\`\`

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. <step 1>
2. <step 2>
...
```

---

## Learn More

| Topic | How to Find |
|-------|-------------|
| httpx async usage | Search: `httpx async client python requests` |
| pyproject.toml dependency format | See: `pyproject.toml [project.dependencies]` in this repo |
| GitHub raw URL patterns | `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>` |
| uv sync documentation | `uv sync --help` or https://docs.astral.sh/uv/ |