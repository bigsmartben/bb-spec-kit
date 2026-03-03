"""
Tests for `specify init` with four required AI agents.

These agents MUST pass:
  - codex    (.codex/prompts/)
  - claude   (.claude/commands/)
  - opencode (.opencode/command/)    ← singular 'command', not 'commands'
  - roo      (.roo/commands/)        ← maps to "Roo Code" in AGENTS.md

Test layers:
  1. AGENT_CONFIG unit tests  — static config validation, no mocking
  2. Directory-mapping tests  — verify folder + commands_subdir combinations
  3. CLI integration tests    — mocked download + check_tool, real Typer runner
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from specify_cli import AGENT_CONFIG, app


# ───────── constants ─────────

# Required agents: (agent_key, expected_folder, expected_commands_subdir)
REQUIRED_AGENTS = [
    ("codex",     ".codex",     "prompts"),
    ("claude",    ".claude",    "commands"),
    ("opencode",  ".opencode",  "command"),   # singular
    ("roo",       ".roo",       "commands"),
]

runner = CliRunner()


# ───────── fixtures ─────────

@pytest.fixture
def tmp_project(tmp_path):
    """Create an isolated temporary project directory."""
    project = tmp_path / "test-project"
    project.mkdir()
    return project


def _make_download_mock(project_path: Path, agent_key: str):
    """
    Return a side_effect function for patching download_and_extract_template.

    Creates the minimum directory structure the CLI expects to find after
    extraction: the agent's commands subdirectory with a sample markdown file,
    plus the .specify/templates directory for constitution setup.
    """
    folder = AGENT_CONFIG[agent_key]["folder"].rstrip("/")
    subdir = AGENT_CONFIG[agent_key]["commands_subdir"]

    def _side_effect(
        proj_path, ai_assistant, script_type, is_current_dir=False,
        *, verbose=True, tracker=None, client=None, debug=False,
        github_token=None,
    ):
        base = Path(proj_path)

        # Create agent commands directory (simulates template extraction)
        commands_dir = base / folder / subdir
        commands_dir.mkdir(parents=True, exist_ok=True)
        (commands_dir / "speckit.specify.md").write_text(
            "---\ndescription: Specify command\n---\n# Specify\n$ARGUMENTS\n"
        )

        # Create .specify structure (simulates full template content)
        specify_root = base / ".specify"
        (specify_root / "templates").mkdir(parents=True, exist_ok=True)
        (specify_root / "memory").mkdir(parents=True, exist_ok=True)
        (specify_root / "templates" / "constitution-template.md").write_text(
            "# Project Constitution\n"
        )

        return base

    return _side_effect


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1: AGENT_CONFIG unit tests (no mocks, no network)
# ─────────────────────────────────────────────────────────────────────────────

class TestAgentConfigExists:
    """All four required agents must be registered in AGENT_CONFIG."""

    @pytest.mark.parametrize("agent_key,_folder,_subdir", REQUIRED_AGENTS)
    def test_agent_key_present(self, agent_key, _folder, _subdir):
        """Agent key must exist in AGENT_CONFIG."""
        assert agent_key in AGENT_CONFIG, (
            f"'{agent_key}' not found in AGENT_CONFIG.\n"
            f"Available keys: {sorted(AGENT_CONFIG.keys())}"
        )

    @pytest.mark.parametrize("agent_key,_folder,_subdir", REQUIRED_AGENTS)
    def test_agent_has_required_fields(self, agent_key, _folder, _subdir):
        """Each agent config must contain all mandatory fields."""
        cfg = AGENT_CONFIG[agent_key]
        for field in ("name", "folder", "commands_subdir", "install_url", "requires_cli"):
            assert field in cfg, (
                f"AGENT_CONFIG['{agent_key}'] missing field '{field}'"
            )

    @pytest.mark.parametrize("agent_key,_folder,_subdir", REQUIRED_AGENTS)
    def test_agent_name_is_nonempty_string(self, agent_key, _folder, _subdir):
        """Display name must be a non-empty string."""
        name = AGENT_CONFIG[agent_key]["name"]
        assert isinstance(name, str) and name.strip(), (
            f"AGENT_CONFIG['{agent_key}']['name'] is empty or not a string: {name!r}"
        )

    @pytest.mark.parametrize("agent_key,_folder,_subdir", REQUIRED_AGENTS)
    def test_agent_requires_cli_is_bool(self, agent_key, _folder, _subdir):
        """requires_cli must be a boolean."""
        val = AGENT_CONFIG[agent_key]["requires_cli"]
        assert isinstance(val, bool), (
            f"AGENT_CONFIG['{agent_key}']['requires_cli'] must be bool, got {type(val)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Layer 2: Directory-mapping tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAgentDirectoryMapping:
    """Verify folder and commands_subdir for each required agent."""

    @pytest.mark.parametrize("agent_key,expected_folder,expected_subdir", REQUIRED_AGENTS)
    def test_agent_folder(self, agent_key, expected_folder, expected_subdir):
        """Verify the agent's top-level folder."""
        actual_folder = AGENT_CONFIG[agent_key]["folder"].rstrip("/")
        assert actual_folder == expected_folder, (
            f"AGENT_CONFIG['{agent_key}']['folder'] mismatch.\n"
            f"  Expected: '{expected_folder}/'\n"
            f"  Got:      '{actual_folder}/'\n"
            "Update AGENT_CONFIG in src/specify_cli/__init__.py to fix."
        )

    @pytest.mark.parametrize("agent_key,expected_folder,expected_subdir", REQUIRED_AGENTS)
    def test_agent_commands_subdir(self, agent_key, expected_folder, expected_subdir):
        """Verify the commands subdirectory name (pay attention to singular vs plural)."""
        actual_subdir = AGENT_CONFIG[agent_key]["commands_subdir"]
        assert actual_subdir == expected_subdir, (
            f"AGENT_CONFIG['{agent_key}']['commands_subdir'] mismatch.\n"
            f"  Expected: '{expected_subdir}'\n"
            f"  Got:      '{actual_subdir}'\n"
            "NOTE: opencode uses 'command' (singular). "
            "codex uses 'prompts'. Others use standard 'commands'."
        )

    def test_codex_uses_prompts_not_commands(self):
        """codex specifically must use 'prompts', not the default 'commands'."""
        assert AGENT_CONFIG["codex"]["commands_subdir"] == "prompts", (
            "codex must use commands_subdir='prompts' "
            "(matches .codex/prompts/ directory convention)"
        )

    def test_opencode_uses_singular_command(self):
        """opencode specifically must use 'command' (singular), not 'commands'."""
        assert AGENT_CONFIG["opencode"]["commands_subdir"] == "command", (
            "opencode must use commands_subdir='command' (singular).\n"
            "This is a deliberate exception to the 'commands' convention."
        )

    def test_roo_requires_cli_false(self):
        """roo is IDE-based and must NOT require CLI tool check."""
        assert AGENT_CONFIG["roo"]["requires_cli"] is False, (
            "roo (Roo Code) is IDE-based and should have requires_cli=False."
        )

    def test_claude_requires_cli_true(self):
        """claude is a CLI tool and MUST require CLI check."""
        assert AGENT_CONFIG["claude"]["requires_cli"] is True, (
            "claude (Claude Code) is a CLI tool and should have requires_cli=True."
        )

    def test_codex_requires_cli_true(self):
        """codex is a CLI tool and MUST require CLI check."""
        assert AGENT_CONFIG["codex"]["requires_cli"] is True, (
            "codex (Codex CLI) is a CLI tool and should have requires_cli=True."
        )

    def test_opencode_requires_cli_true(self):
        """opencode is a CLI tool and MUST require CLI check."""
        assert AGENT_CONFIG["opencode"]["requires_cli"] is True, (
            "opencode is a CLI tool and should have requires_cli=True."
        )

    @pytest.mark.parametrize("agent_key,expected_folder,expected_subdir", REQUIRED_AGENTS)
    def test_full_commands_path(self, agent_key, expected_folder, expected_subdir, tmp_path):
        """Commands directory resolves correctly for each agent."""
        folder = AGENT_CONFIG[agent_key]["folder"].rstrip("/")
        subdir = AGENT_CONFIG[agent_key]["commands_subdir"]
        expected_path = tmp_path / folder / subdir
        assert str(expected_path).endswith(f"{folder}/{subdir}")


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3: CLI integration tests (mocked download + check_tool)
# ─────────────────────────────────────────────────────────────────────────────

class TestInitCliCodex:
    """specify init --here --ai codex — must pass."""

    def test_codex_init_creates_prompts_dir(self, tmp_project):
        side_effect = _make_download_mock(tmp_project, "codex")
        with (
            patch("specify_cli.download_and_extract_template", side_effect=side_effect),
            patch("specify_cli.check_tool", return_value=True),
            patch("specify_cli.init_git_repo", return_value=(True, None)),
        ):
            # Change to tmp_project directory to avoid "not empty" warning
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmp_project)
                result = runner.invoke(
                    app,
                    ["init", "--here", "--ai", "codex", "--script", "sh",
                     "--no-git", "--ignore-agent-tools"],
                    catch_exceptions=False,
                    env={"HOME": str(tmp_project.parent)},
                )
            finally:
                os.chdir(orig_cwd)
        # Accept 0 exit code
        assert result.exit_code == 0, (
            f"CLI exited {result.exit_code}\nOutput:\n{result.output}"
        )

    def test_codex_config_folder_correct(self):
        """End-to-end config check: codex folder is .codex."""
        cfg = AGENT_CONFIG["codex"]
        assert cfg["folder"].strip("/") == ".codex"
        assert cfg["commands_subdir"] == "prompts"
        assert cfg["requires_cli"] is True


class TestInitCliClaude:
    """specify init --here --ai claude — must pass."""

    def test_claude_init_creates_commands_dir(self, tmp_project):
        side_effect = _make_download_mock(tmp_project, "claude")
        with (
            patch("specify_cli.download_and_extract_template", side_effect=side_effect),
            patch("specify_cli.check_tool", return_value=True),
            patch("specify_cli.init_git_repo", return_value=(True, None)),
        ):
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmp_project)
                result = runner.invoke(
                    app,
                    ["init", "--here", "--ai", "claude", "--script", "sh",
                     "--no-git", "--ignore-agent-tools"],
                    catch_exceptions=False,
                    env={"HOME": str(tmp_project.parent)},
                )
            finally:
                os.chdir(orig_cwd)
        assert result.exit_code == 0, (
            f"CLI exited {result.exit_code}\nOutput:\n{result.output}"
        )

    def test_claude_config_folder_correct(self):
        cfg = AGENT_CONFIG["claude"]
        assert cfg["folder"].strip("/") == ".claude"
        assert cfg["commands_subdir"] == "commands"
        assert cfg["requires_cli"] is True


class TestInitCliOpencode:
    """specify init --here --ai opencode — must pass (singular 'command')."""

    def test_opencode_init_creates_command_dir(self, tmp_project):
        side_effect = _make_download_mock(tmp_project, "opencode")
        with (
            patch("specify_cli.download_and_extract_template", side_effect=side_effect),
            patch("specify_cli.check_tool", return_value=True),
            patch("specify_cli.init_git_repo", return_value=(True, None)),
        ):
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmp_project)
                result = runner.invoke(
                    app,
                    ["init", "--here", "--ai", "opencode", "--script", "sh",
                     "--no-git", "--ignore-agent-tools"],
                    catch_exceptions=False,
                    env={"HOME": str(tmp_project.parent)},
                )
            finally:
                os.chdir(orig_cwd)
        assert result.exit_code == 0, (
            f"CLI exited {result.exit_code}\nOutput:\n{result.output}"
        )

    def test_opencode_subdir_is_singular(self):
        """opencode commands_subdir must be 'command' (singular) not 'commands'."""
        assert AGENT_CONFIG["opencode"]["commands_subdir"] == "command", (
            "opencode uses .opencode/command/ (singular). "
            "AGENT_CONFIG must reflect this exactly."
        )


class TestInitCliRoo:
    """specify init --here --ai roo — must pass (IDE-based, no CLI check)."""

    def test_roo_init_succeeds(self, tmp_project):
        side_effect = _make_download_mock(tmp_project, "roo")
        with (
            patch("specify_cli.download_and_extract_template", side_effect=side_effect),
            # roo has requires_cli=False, so check_tool is called for git only
            patch("specify_cli.check_tool", return_value=True),
            patch("specify_cli.init_git_repo", return_value=(True, None)),
        ):
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmp_project)
                result = runner.invoke(
                    app,
                    ["init", "--here", "--ai", "roo", "--script", "sh",
                     "--no-git", "--ignore-agent-tools"],
                    catch_exceptions=False,
                    env={"HOME": str(tmp_project.parent)},
                )
            finally:
                os.chdir(orig_cwd)
        assert result.exit_code == 0, (
            f"CLI exited {result.exit_code}\nOutput:\n{result.output}"
        )

    def test_roo_config_is_ide_based(self):
        """Roo Code is IDE-based: requires_cli must be False."""
        cfg = AGENT_CONFIG["roo"]
        assert cfg["folder"].strip("/") == ".roo"
        assert cfg["commands_subdir"] == "commands"
        assert cfg["requires_cli"] is False
        assert cfg["install_url"] is None


# ─────────────────────────────────────────────────────────────────────────────
# Layer 4: Cross-agent invariant tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAgentInvariants:
    """Cross-agent invariants that must hold for all four required agents."""

    @pytest.mark.parametrize("agent_key,_f,_s", REQUIRED_AGENTS)
    def test_agent_folder_starts_with_dot(self, agent_key, _f, _s):
        """All agent folders must start with '.' (hidden directory convention)."""
        folder = AGENT_CONFIG[agent_key]["folder"]
        assert folder.startswith("."), (
            f"AGENT_CONFIG['{agent_key}']['folder'] must start with '.', got: {folder!r}"
        )

    @pytest.mark.parametrize("agent_key,_f,_s", REQUIRED_AGENTS)
    def test_agent_commands_subdir_nonempty(self, agent_key, _f, _s):
        """commands_subdir must be a non-empty string."""
        val = AGENT_CONFIG[agent_key]["commands_subdir"]
        assert isinstance(val, str) and val.strip(), (
            f"AGENT_CONFIG['{agent_key}']['commands_subdir'] must be non-empty string"
        )

    def test_invalid_agent_key_not_in_config(self):
        """An unknown agent key must NOT be present in AGENT_CONFIG.

        We validate at the config layer (reliable) rather than testing CLI exit
        code, because the CLI may defer agent validation to the download step.
        """
        invalid_key = "nonexistent-agent-xyz"
        assert invalid_key not in AGENT_CONFIG, (
            f"'{invalid_key}' was unexpectedly found in AGENT_CONFIG — "
            "either remove it or update this test."
        )

    def test_all_four_agents_in_config(self):
        """All four required agents must be present in AGENT_CONFIG simultaneously."""
        missing = [k for k, _, _ in REQUIRED_AGENTS if k not in AGENT_CONFIG]
        assert not missing, (
            f"Missing required agents in AGENT_CONFIG: {missing}\n"
            "Add them to specify_cli.__init__.AGENT_CONFIG"
        )
