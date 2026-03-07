"""Cross-source consistency checks for agent metadata."""

from __future__ import annotations

import re
from pathlib import Path

import specify_cli
from specify_cli.agent_registry import (
    build_cli_agent_config,
    build_extension_agent_configs,
    documented_agent_keys,
    release_agent_keys,
)
from specify_cli.extensions import CommandRegistrar

REPO_ROOT = Path(__file__).resolve().parent.parent
SH_RELEASE = REPO_ROOT / ".github" / "workflows" / "scripts" / "create-release-packages.sh"
PS_RELEASE = REPO_ROOT / ".github" / "workflows" / "scripts" / "create-release-packages.ps1"
GH_RELEASE = REPO_ROOT / ".github" / "workflows" / "scripts" / "create-github-release.sh"
README = REPO_ROOT / "README.md"
AGENTS_DOC = REPO_ROOT / "AGENTS.md"


def _extract_sh_all_agents(content: str) -> list[str]:
    m = re.search(r"ALL_AGENTS=\(([^)]*)\)", content)
    assert m, "ALL_AGENTS not found in create-release-packages.sh"
    return [x for x in m.group(1).split() if x]


def _extract_ps_all_agents(content: str) -> list[str]:
    m = re.search(r"\$AllAgents\s*=\s*@\(([^)]*)\)", content)
    assert m, "$AllAgents not found in create-release-packages.ps1"
    return [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()]


def _extract_sh_case_labels(content: str) -> set[str]:
    m = re.search(r"case \$agent in(.*?)\n\s*esac", content, re.S)
    assert m, "Could not find case $agent block in create-release-packages.sh"
    return set(re.findall(r"^\s*([a-z0-9-]+)\)\s*$", m.group(1), re.M))


def _extract_ps_switch_labels(content: str) -> set[str]:
    labels = set(re.findall(r"^\s*'([a-z0-9-]+)'\s*\{", content, re.M))
    assert labels, "Could not find switch labels in create-release-packages.ps1"
    return labels


def _extract_release_asset_agents(content: str) -> set[str]:
    return set(
        re.findall(
            r"spec-kit-template-([a-z0-9-]+)-(?:sh|ps)-\"\$VERSION\"\.zip",
            content,
        )
    )


def _extract_doc_keys(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    m = re.search(
        r"<!-- supported-agent-keys:start -->\s*```text\s*(.*?)\s*```\s*<!-- supported-agent-keys:end -->",
        content,
        re.S,
    )
    assert m, f"supported-agent-keys block not found in {path.name}"
    return [line.strip() for line in m.group(1).splitlines() if line.strip()]


def test_registry_cli_projection_matches_exported_agent_config():
    assert specify_cli.AGENT_CONFIG == build_cli_agent_config()


def test_registry_extension_projection_matches_command_registrar():
    assert CommandRegistrar.AGENT_CONFIGS == build_extension_agent_configs()


def test_release_agent_lists_match_registry():
    sh_agents = _extract_sh_all_agents(SH_RELEASE.read_text(encoding="utf-8"))
    ps_agents = _extract_ps_all_agents(PS_RELEASE.read_text(encoding="utf-8"))
    expected = set(release_agent_keys())
    assert set(sh_agents) == expected
    assert set(ps_agents) == expected
    assert len(sh_agents) == len(set(sh_agents))
    assert len(ps_agents) == len(set(ps_agents))


def test_release_asset_list_matches_registry():
    release_assets = _extract_release_asset_agents(GH_RELEASE.read_text(encoding="utf-8"))
    assert release_assets == set(release_agent_keys())


def test_release_scripts_have_case_for_every_agent():
    expected = set(release_agent_keys())
    sh_cases = _extract_sh_case_labels(SH_RELEASE.read_text(encoding="utf-8"))
    ps_cases = _extract_ps_switch_labels(PS_RELEASE.read_text(encoding="utf-8"))
    assert expected <= sh_cases
    assert expected <= ps_cases


def test_documented_agent_keys_match_registry():
    expected = documented_agent_keys()
    assert _extract_doc_keys(README) == expected
    assert _extract_doc_keys(AGENTS_DOC) == expected
