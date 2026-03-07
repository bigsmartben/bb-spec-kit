"""Consistency tests for script contracts under scripts/contracts/."""

from __future__ import annotations

import json
import re
from pathlib import Path

from specify_cli.agent_registry import build_cli_agent_config


ROOT = Path(__file__).parent.parent
CONTRACTS_DIR = ROOT / "scripts" / "contracts"
COMMANDS_DIR = ROOT / "templates" / "commands"
BASH_UPDATE_AGENT_CONTEXT = ROOT / "scripts" / "bash" / "update-agent-context.sh"
PS_UPDATE_AGENT_CONTEXT = ROOT / "scripts" / "powershell" / "update-agent-context.ps1"

EXPECTED_CONTRACTS = {
    "create-new-feature.json",
    "setup-plan.json",
    "check-prerequisites.json",
    "update-agent-context.json",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_bash_update_specific_agent_labels(content: str) -> set[str]:
    m = re.search(r"update_specific_agent\(\) \{(.*?)\n\}", content, re.S)
    assert m, "Could not find update_specific_agent() in bash script"
    return set(re.findall(r"^\s*([a-z0-9-]+)\)\s*$", m.group(1), re.M))


def _extract_ps_update_specific_agent_labels(content: str) -> set[str]:
    m = re.search(r"function Update-SpecificAgent \{(.*?)\n\}", content, re.S)
    assert m, "Could not find Update-SpecificAgent in powershell script"
    return set(re.findall(r"^\s*'([a-z0-9-]+)'\s*\{", m.group(1), re.M))


def test_expected_contract_files_exist():
    actual = {p.name for p in CONTRACTS_DIR.glob("*.json")}
    missing = EXPECTED_CONTRACTS - actual
    assert not missing, f"Missing contract files: {sorted(missing)}"


def test_all_contracts_reference_existing_scripts():
    for contract_path in CONTRACTS_DIR.glob("*.json"):
        data = _load_json(contract_path)
        scripts = data.get("scripts", {})
        for key in ("sh", "ps"):
            script_rel = scripts.get(key)
            assert script_rel, f"{contract_path.name} missing scripts.{key}"
            script_path = ROOT / script_rel
            assert script_path.exists(), f"{contract_path.name} references missing {key} script: {script_rel}"


def test_core_commands_reference_contracts():
    mapping = {
        "specify.md": "scripts/contracts/create-new-feature.json",
        "plan.md": "scripts/contracts/setup-plan.json",
        "tasks.md": "scripts/contracts/check-prerequisites.json",
        "implement.md": "scripts/contracts/check-prerequisites.json",
    }
    for cmd_file, expected_contract in mapping.items():
        content = (COMMANDS_DIR / cmd_file).read_text(encoding="utf-8")
        assert expected_contract in content, f"{cmd_file} should reference {expected_contract}"


def test_create_new_feature_contract_required_keys():
    data = _load_json(CONTRACTS_DIR / "create-new-feature.json")
    required = set(data["json_output"]["required_keys"])
    assert {"BRANCH_NAME", "SPEC_FILE", "FEATURE_NUM"}.issubset(required)


def test_setup_plan_contract_required_keys():
    data = _load_json(CONTRACTS_DIR / "setup-plan.json")
    required = set(data["json_output"]["required_keys"])
    assert {
        "FEATURE_SPEC",
        "IMPL_PLAN",
        "SPECS_DIR",
        "FEATURE_DIR",
        "INPUT_FILE_ABS",
        "BRANCH",
        "HAS_GIT",
    }.issubset(required)
    assert data["inputs"]["input_file"]["required"] is True


def test_check_prerequisites_contract_modes():
    data = _load_json(CONTRACTS_DIR / "check-prerequisites.json")
    assert "normal_mode_required_keys" in data["json_output"]
    assert "paths_only_required_keys" in data["json_output"]
    assert "input_file" in data["inputs"]
    assert "mode" in data["inputs"]
    assert "INPUT_FILE_ABS" in set(data["json_output"]["paths_only_required_keys"])


def test_update_agent_context_contract_supports_optional_input_file():
    data = _load_json(CONTRACTS_DIR / "update-agent-context.json")
    assert "input_file" in data["inputs"]
    assert data["inputs"]["input_file"]["required"] is False


def test_update_agent_context_allowed_agent_types_matches_registry_and_scripts():
    expected = set(build_cli_agent_config().keys())

    contract = _load_json(CONTRACTS_DIR / "update-agent-context.json")
    contract_allowed = set(contract["allowed_agent_types"])

    bash_labels = _extract_bash_update_specific_agent_labels(
        BASH_UPDATE_AGENT_CONTEXT.read_text(encoding="utf-8")
    )
    ps_labels = _extract_ps_update_specific_agent_labels(
        PS_UPDATE_AGENT_CONTEXT.read_text(encoding="utf-8")
    )

    assert contract_allowed == bash_labels
    assert contract_allowed == ps_labels
    assert contract_allowed <= expected

    # update-agent-context currently does not maintain a dedicated Cline context file
    # (unlike command/workflow generation), so cline is intentionally excluded.
    assert expected - contract_allowed == {"cline"}
