"""
Tests for all speckit command templates in templates/commands/.

Covers:
- All expected command files exist
- Valid YAML frontmatter with 'description' field
- Body content is non-empty
- $ARGUMENTS placeholder present in templating commands
- prd2spec: PRD→Spec conversion keywords, usage section, output targets
- speckit phase commands: specify/plan/tasks/implement/constitution/analyze
- checklist, clarify, taskstoissues: basic structure
- No duplicate command IDs
- All commands have a unique, non-empty description
"""

from pathlib import Path

import pytest
import yaml

# ───────── constants ─────────

COMMANDS_DIR = Path(__file__).parent.parent / "templates" / "commands"

EXPECTED_COMMANDS = [
    "analyze",
    "checklist",
    "clarify",
    "constitution",
    "design",
    "implement",
    "plan",
    "prd2spec",
    "specify",
    "tasks",
    "taskstoissues",
]

# Commands that must have $ARGUMENTS placeholder.
# Note: prd2spec accepts file-path arguments (e.g. /speckit.prd2spec docs/prd.md)
# and uses $ARGUMENTS embedded in usage examples, NOT as a standalone template
# variable in the body. It is intentionally excluded from this list.
COMMANDS_WITH_ARGUMENTS = [
    "specify",
    "plan",
    "tasks",
    "implement",
    "constitution",
    "clarify",
    "checklist",
    "analyze",
    "design",
]

# Commands expected to reference a handoff or downstream command
COMMANDS_WITH_HANDOFFS = [
    "specify",
    "plan",
    "tasks",
]


# ───────── helpers ─────────


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content.

    Returns:
        (frontmatter_dict, body_text) — frontmatter is {} if not present.
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        fm = {}

    return fm, parts[2].strip()


def _load_command(name: str) -> tuple[str, dict, str]:
    """Load a command template.

    Returns:
        (raw_content, frontmatter_dict, body_text)
    """
    path = COMMANDS_DIR / f"{name}.md"
    content = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(content)
    return content, fm, body


# ───────── existence tests ─────────


class TestCommandFilesExist:
    """All expected command files must be present."""

    def test_commands_directory_exists(self):
        assert COMMANDS_DIR.exists(), (
            f"templates/commands/ directory not found at {COMMANDS_DIR}\nIs this running from the spec-kit repo root?"
        )

    @pytest.mark.parametrize("name", EXPECTED_COMMANDS)
    def test_command_file_exists(self, name):
        path = COMMANDS_DIR / f"{name}.md"
        assert path.exists(), (
            f"Missing command template: templates/commands/{name}.md\n"
            "Create the file or rename it to match the expected name."
        )

    def test_no_unexpected_extensions(self):
        """All files in commands/ must be .md (no stray .txt or .bak files)."""
        bad = [f for f in COMMANDS_DIR.iterdir() if f.suffix != ".md"]
        assert not bad, f"Non-markdown files found in templates/commands/: {[f.name for f in bad]}"


# ───────── frontmatter structure tests ─────────


class TestCommandFrontmatter:
    """Each command file must have valid YAML frontmatter with required fields."""

    @pytest.mark.parametrize("name", EXPECTED_COMMANDS)
    def test_has_frontmatter(self, name):
        """Command file must begin with '---' (YAML frontmatter delimiter)."""
        path = COMMANDS_DIR / f"{name}.md"
        if not path.exists():
            pytest.skip(f"{name}.md does not exist")
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---"), (
            f"templates/commands/{name}.md must start with '---' (YAML frontmatter).\n"
            'Add: ---\\ndescription: "..."\n---'
        )

    @pytest.mark.parametrize("name", EXPECTED_COMMANDS)
    def test_frontmatter_is_valid_yaml(self, name):
        """Frontmatter YAML must parse without error."""
        path = COMMANDS_DIR / f"{name}.md"
        if not path.exists():
            pytest.skip(f"{name}.md does not exist")
        content = path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            pytest.fail(f"{name}.md has opening '---' but no closing '---'")
        try:
            result = yaml.safe_load(parts[1])
        except yaml.YAMLError as exc:
            pytest.fail(f"{name}.md has invalid YAML frontmatter: {exc}")
        assert result is not None, (
            f'{name}.md frontmatter is empty (None after YAML parse).\nAt minimum, add: description: "..."'
        )

    @pytest.mark.parametrize("name", EXPECTED_COMMANDS)
    def test_has_description_field(self, name):
        """Every command must have 'description' in frontmatter."""
        path = COMMANDS_DIR / f"{name}.md"
        if not path.exists():
            pytest.skip(f"{name}.md does not exist")
        _, fm, _ = _load_command(name)
        assert "description" in fm, (
            f"templates/commands/{name}.md frontmatter missing 'description' field.\n"
            'Add: description: "Short description of what this command does"'
        )
        assert fm["description"] and str(fm["description"]).strip(), (
            f"templates/commands/{name}.md 'description' must not be empty."
        )


# ───────── body content tests ─────────


class TestCommandBody:
    """Command body must be non-trivial."""

    @pytest.mark.parametrize("name", EXPECTED_COMMANDS)
    def test_body_is_nonempty(self, name):
        """Command body (after frontmatter) must contain meaningful content."""
        path = COMMANDS_DIR / f"{name}.md"
        if not path.exists():
            pytest.skip(f"{name}.md does not exist")
        _, _, body = _load_command(name)
        assert len(body.strip()) >= 50, (
            f"templates/commands/{name}.md body seems too short ({len(body.strip())} chars).\n"
            "Command bodies should describe the workflow in detail."
        )

    @pytest.mark.parametrize("name", COMMANDS_WITH_ARGUMENTS)
    def test_has_arguments_placeholder(self, name):
        """Commands that accept user input must reference $ARGUMENTS."""
        path = COMMANDS_DIR / f"{name}.md"
        if not path.exists():
            pytest.skip(f"{name}.md does not exist")
        content = path.read_text(encoding="utf-8")
        assert "$ARGUMENTS" in content, (
            f"templates/commands/{name}.md must contain '$ARGUMENTS' placeholder.\n"
            "This is how agent commands receive user-provided text."
        )


# ───────── prd2spec specific tests ─────────


class TestPrd2Spec:
    """prd2spec command must fully describe PRD→Spec conversion workflow."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = COMMANDS_DIR / "prd2spec.md"
        if not path.exists():
            pytest.skip("prd2spec.md does not exist")
        self.content, self.fm, self.body = _load_command("prd2spec")

    def test_description_mentions_prd(self):
        """Description must mention PRD."""
        desc = str(self.fm.get("description", "")).lower()
        assert "prd" in desc, f"prd2spec description should mention 'PRD'. Got: {self.fm.get('description')!r}"

    def test_description_mentions_spec(self):
        """Description must mention Spec or spec.md."""
        desc = str(self.fm.get("description", "")).lower()
        assert "spec" in desc, f"prd2spec description should mention 'spec'. Got: {self.fm.get('description')!r}"

    def test_body_has_usage_section(self):
        """prd2spec must include a Usage section."""
        assert "## Usage" in self.content or "# Usage" in self.content or "usage" in self.content.lower(), (
            "prd2spec.md must have a Usage section showing how to invoke the command."
        )

    def test_body_references_spec_md_output(self):
        """prd2spec must reference spec.md as its output target."""
        assert "spec.md" in self.content, "prd2spec.md must reference 'spec.md' as the output of the conversion."

    def test_body_references_speckit_plan(self):
        """prd2spec output must be ready for speckit.plan (downstream handoff)."""
        assert "speckit.plan" in self.content or "/speckit.plan" in self.content or "plan" in self.body.lower(), (
            "prd2spec.md should reference speckit.plan as the next step after conversion."
        )

    def test_body_has_workflow_steps(self):
        """prd2spec must describe its workflow steps."""
        # Expect numbered steps or headers indicating workflow
        has_steps = "Step 1" in self.content or "### Step" in self.content or "1." in self.content
        assert has_steps, "prd2spec.md should contain numbered workflow steps (e.g., 'Step 1: ...')."

    def test_body_mentions_traceability(self):
        """prd2spec must mention traceability from PRD to Spec."""
        assert "traceab" in self.content.lower() or "source" in self.content.lower(), (
            "prd2spec.md should mention traceability from PRD items to Spec entries."
        )

    def test_body_describes_inputs(self):
        """prd2spec must describe its accepted inputs."""
        assert "## Inputs" in self.content or "## Input" in self.content or "input" in self.content.lower(), (
            "prd2spec.md must describe the inputs it accepts (file paths, @references, etc.)."
        )

    def test_body_describes_outputs(self):
        """prd2spec must describe what it produces."""
        assert "## Output" in self.content or "output" in self.content.lower(), (
            "prd2spec.md must describe the outputs it produces."
        )

    def test_has_scripts_in_frontmatter(self):
        """prd2spec must have scripts field in frontmatter."""
        assert "scripts" in self.fm, "prd2spec.md frontmatter must contain 'scripts' (sh and/or ps entries)."


# ───────── speckit phase command tests ─────────


class TestSpecifyCommand:
    """specify command: creates spec.md from natural language description."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = COMMANDS_DIR / "specify.md"
        if not path.exists():
            pytest.skip("specify.md does not exist")
        self.content, self.fm, self.body = _load_command("specify")

    def test_has_scripts(self):
        assert "scripts" in self.fm, "specify.md must have scripts in frontmatter"

    def test_has_handoffs(self):
        assert "handoffs" in self.fm, "specify.md must declare handoffs (downstream commands like speckit.plan)"

    def test_handoffs_includes_plan(self):
        handoffs = self.fm.get("handoffs", [])
        labels = [str(h.get("agent", "")).lower() for h in handoffs if isinstance(h, dict)]
        assert any("plan" in label for label in labels), (
            "specify.md handoffs must include speckit.plan as a downstream step."
        )

    def test_references_spec_template(self):
        assert "spec" in self.body.lower(), "specify.md body must mention spec creation."


class TestPlanCommand:
    """plan command: generates implementation plan from spec."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = COMMANDS_DIR / "plan.md"
        if not path.exists():
            pytest.skip("plan.md does not exist")
        self.content, self.fm, self.body = _load_command("plan")

    def test_description_mentions_plan(self):
        desc = str(self.fm.get("description", "")).lower()
        assert "plan" in desc or "implementation" in desc, (
            f"plan.md description must mention 'plan' or 'implementation'. Got: {desc!r}"
        )

    def test_body_references_spec(self):
        assert "spec" in self.body.lower(), "plan.md must reference the spec.md as its input."


class TestDesignCommand:
    """design command: generates UX/UI artifacts and static prototype from spec."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = COMMANDS_DIR / "design.md"
        if not path.exists():
            pytest.skip("design.md does not exist")
        self.content, self.fm, self.body = _load_command("design")

    def test_description_mentions_design_or_prototype(self):
        desc = str(self.fm.get("description", "")).lower()
        assert "design" in desc or "prototype" in desc or "ux" in desc, (
            f"design.md description must mention design/prototype/ux intent. Got: {desc!r}"
        )

    def test_body_references_spec_as_input(self):
        assert "spec" in self.body.lower(), "design.md must reference spec.md as its input context."

    def test_body_references_design_templates(self):
        assert "design-template.md" in self.content and "design-ui-template.md" in self.content and "design-prototype-template.md" in self.content, (
            "design.md must reference design template pack files for deterministic output structure."
        )

    def test_body_references_prototype_outputs(self):
        assert "prototype/index.html" in self.content and "prototype/pages" in self.content, (
            "design.md must explicitly define prototype output files/paths."
        )


class TestTasksCommand:
    """tasks command: breaks down plan into actionable task list."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = COMMANDS_DIR / "tasks.md"
        if not path.exists():
            pytest.skip("tasks.md does not exist")
        self.content, self.fm, self.body = _load_command("tasks")

    def test_description_mentions_tasks(self):
        desc = str(self.fm.get("description", "")).lower()
        assert "task" in desc or "breakdown" in desc, (
            f"tasks.md description must mention 'task' or similar. Got: {desc!r}"
        )

    def test_body_references_plan(self):
        assert "plan" in self.body.lower(), "tasks.md must reference the plan as its input."


class TestImplementCommand:
    """implement command: executes tasks to build the feature."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = COMMANDS_DIR / "implement.md"
        if not path.exists():
            pytest.skip("implement.md does not exist")
        self.content, self.fm, self.body = _load_command("implement")

    def test_description_mentions_implement(self):
        desc = str(self.fm.get("description", "")).lower()
        assert "implement" in desc or "execute" in desc or "build" in desc, (
            f"implement.md description must mention 'implement' or similar. Got: {desc!r}"
        )

    def test_body_references_tasks(self):
        assert "task" in self.body.lower(), "implement.md must reference tasks as its input."


class TestConstitutionCommand:
    """constitution command: creates project governing principles."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = COMMANDS_DIR / "constitution.md"
        if not path.exists():
            pytest.skip("constitution.md does not exist")
        self.content, self.fm, self.body = _load_command("constitution")

    def test_description_present(self):
        assert self.fm.get("description"), "constitution.md must have a non-empty description"

    def test_body_has_content(self):
        assert len(self.body) >= 100, "constitution.md body too short"


class TestAnalyzeCommand:
    """analyze command: cross-artifact consistency analysis."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = COMMANDS_DIR / "analyze.md"
        if not path.exists():
            pytest.skip("analyze.md does not exist")
        self.content, self.fm, self.body = _load_command("analyze")

    def test_description_present(self):
        assert self.fm.get("description"), "analyze.md must have a non-empty description"

    def test_body_mentions_analysis(self):
        assert "analyz" in self.body.lower() or "consistency" in self.body.lower() or "spec" in self.body.lower(), (
            "analyze.md must describe the analysis it performs."
        )


class TestClarifyCommand:
    """clarify command: structured requirements clarification."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = COMMANDS_DIR / "clarify.md"
        if not path.exists():
            pytest.skip("clarify.md does not exist")
        self.content, self.fm, self.body = _load_command("clarify")

    def test_description_present(self):
        assert self.fm.get("description"), "clarify.md must have a non-empty description"


class TestChecklistCommand:
    """checklist command: generates quality checklists."""

    @pytest.fixture(autouse=True)
    def load(self):
        path = COMMANDS_DIR / "checklist.md"
        if not path.exists():
            pytest.skip("checklist.md does not exist")
        self.content, self.fm, self.body = _load_command("checklist")

    def test_description_present(self):
        assert self.fm.get("description"), "checklist.md must have a non-empty description"

    def test_body_mentions_checklist(self):
        assert "check" in self.body.lower() or "quality" in self.body.lower(), (
            "checklist.md body must mention checking or quality."
        )


# ───────── uniqueness / integrity tests ─────────


class TestCommandIntegrity:
    """Ensure no duplicate descriptions and no broken file structures."""

    def test_all_descriptions_unique(self):
        """No two commands should have the exact same description."""
        descriptions = {}
        for name in EXPECTED_COMMANDS:
            path = COMMANDS_DIR / f"{name}.md"
            if not path.exists():
                continue
            _, fm, _ = _load_command(name)
            desc = fm.get("description", "")
            if desc:
                assert desc not in descriptions.values(), (
                    f"Duplicate description found in '{name}.md' and '{descriptions.get(desc)}':\n  {desc!r}"
                )
                descriptions[name] = desc

    def test_commands_dir_matches_expected_set(self):
        """templates/commands/ should contain at least all EXPECTED_COMMANDS."""
        actual = {f.stem for f in COMMANDS_DIR.glob("*.md")}
        missing = set(EXPECTED_COMMANDS) - actual
        assert not missing, f"Missing command files in templates/commands/: {sorted(missing)}"

    def test_no_empty_files(self):
        """No command file should be zero bytes."""
        for path in COMMANDS_DIR.glob("*.md"):
            size = path.stat().st_size
            assert size > 0, f"Empty file found: templates/commands/{path.name}"
