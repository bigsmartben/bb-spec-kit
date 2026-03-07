#!/usr/bin/env python3
"""Validate release script agent metadata against the Python SSOT registry."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def _extract_sh_all_agents(content: str) -> list[str]:
    m = re.search(r"ALL_AGENTS=\(([^)]*)\)", content)
    if not m:
        raise ValueError("Could not find ALL_AGENTS in create-release-packages.sh")
    return [token for token in m.group(1).split() if token]


def _extract_ps_all_agents(content: str) -> list[str]:
    m = re.search(r"\$AllAgents\s*=\s*@\(([^)]*)\)", content)
    if not m:
        raise ValueError("Could not find $AllAgents in create-release-packages.ps1")
    return [token.strip().strip("'\"") for token in m.group(1).split(",") if token.strip()]


def _extract_sh_case_labels(content: str) -> set[str]:
    m = re.search(r"case \$agent in(.*?)\n\s*esac", content, re.S)
    if not m:
        raise ValueError("Could not find 'case $agent in ... esac' block in create-release-packages.sh")
    block = m.group(1)
    return set(re.findall(r"^\s*([a-z0-9-]+)\)\s*$", block, re.M))


def _extract_ps_switch_labels(content: str) -> set[str]:
    # Match all switch labels across file; we only assert expected labels exist.
    labels = set(re.findall(r"^\s*'([a-z0-9-]+)'\s*\{", content, re.M))
    if not labels:
        raise ValueError("Could not find switch labels in create-release-packages.ps1")
    return labels


def _extract_release_asset_agents(content: str) -> set[str]:
    return set(
        re.findall(
            r"spec-kit-template-([a-z0-9-]+)-(?:sh|ps)-\"\$VERSION\"\.zip",
            content,
        )
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root / "src"))

    from specify_cli.agent_registry import release_agent_keys

    expected_order = release_agent_keys()
    expected_set = set(expected_order)

    sh_path = repo_root / ".github" / "workflows" / "scripts" / "create-release-packages.sh"
    ps_path = repo_root / ".github" / "workflows" / "scripts" / "create-release-packages.ps1"
    gh_path = repo_root / ".github" / "workflows" / "scripts" / "create-github-release.sh"

    sh_content = sh_path.read_text(encoding="utf-8")
    ps_content = ps_path.read_text(encoding="utf-8")
    gh_content = gh_path.read_text(encoding="utf-8")

    sh_agents = _extract_sh_all_agents(sh_content)
    ps_agents = _extract_ps_all_agents(ps_content)
    sh_case_labels = _extract_sh_case_labels(sh_content)
    ps_switch_labels = _extract_ps_switch_labels(ps_content)
    release_asset_agents = _extract_release_asset_agents(gh_content)

    errors: list[str] = []

    if set(sh_agents) != expected_set:
        errors.append(
            "create-release-packages.sh ALL_AGENTS set mismatch:\n"
            f"  expected: {sorted(expected_set)}\n"
            f"  actual:   {sorted(set(sh_agents))}"
        )
    if len(sh_agents) != len(set(sh_agents)):
        errors.append("create-release-packages.sh ALL_AGENTS contains duplicates")

    if set(ps_agents) != expected_set:
        errors.append(
            "create-release-packages.ps1 $AllAgents set mismatch:\n"
            f"  expected: {sorted(expected_set)}\n"
            f"  actual:   {sorted(set(ps_agents))}"
        )
    if len(ps_agents) != len(set(ps_agents)):
        errors.append("create-release-packages.ps1 $AllAgents contains duplicates")

    if release_asset_agents != expected_set:
        errors.append(
            "create-github-release.sh asset agent set mismatch:\n"
            f"  expected: {sorted(expected_set)}\n"
            f"  actual:   {sorted(release_asset_agents)}"
        )

    missing_sh_case = expected_set - sh_case_labels
    if missing_sh_case:
        errors.append(f"Missing shell case labels in create-release-packages.sh: {sorted(missing_sh_case)}")

    missing_ps_case = expected_set - ps_switch_labels
    if missing_ps_case:
        errors.append(f"Missing PowerShell switch labels in create-release-packages.ps1: {sorted(missing_ps_case)}")

    if errors:
        print("Agent metadata consistency check failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Agent metadata consistency check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
