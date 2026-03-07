"""Schema validation tests for templates/commands YAML frontmatter (Phase 1)."""

from pathlib import Path

import pytest
import yaml

from specify_cli.command_frontmatter_schema import (
    load_command_frontmatter_schema,
    validate_frontmatter_against_schema,
)

ROOT = Path(__file__).parent.parent
COMMANDS_DIR = ROOT / "templates" / "commands"
SCHEMA_PATH = ROOT / "templates" / "schemas" / "command-frontmatter.schema.yaml"


def _load_frontmatter(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    assert content.startswith("---"), f"{path.name} must start with YAML frontmatter"
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{path.name} missing closing frontmatter delimiter"
    fm = yaml.safe_load(parts[1]) or {}
    assert isinstance(fm, dict), f"{path.name} frontmatter must be a mapping"
    return fm


class TestCommandFrontmatterSchema:
    def test_schema_file_exists(self):
        assert SCHEMA_PATH.exists(), "Expected templates/schemas/command-frontmatter.schema.yaml"

    def test_schema_loads(self):
        schema = load_command_frontmatter_schema(schema_path=SCHEMA_PATH)
        assert isinstance(schema, dict)
        assert schema.get("required_keys")
        assert "description" in schema.get("required_keys", [])

    @pytest.mark.parametrize("path", sorted(COMMANDS_DIR.glob("*.md")), ids=lambda p: p.name)
    def test_all_command_frontmatter_conforms_to_schema(self, path: Path):
        schema = load_command_frontmatter_schema(schema_path=SCHEMA_PATH)
        fm = _load_frontmatter(path)
        errors = validate_frontmatter_against_schema(fm, schema)
        assert not errors, f"{path.name} frontmatter schema errors: {errors}"

    def test_rejects_unknown_key(self):
        schema = load_command_frontmatter_schema(schema_path=SCHEMA_PATH)
        fm = {"description": "x", "bad_key": True}
        errors = validate_frontmatter_against_schema(fm, schema)
        assert any("unknown key: 'bad_key'" in e for e in errors)

    def test_cross_rule_agent_scripts_requires_scripts(self):
        schema = load_command_frontmatter_schema(schema_path=SCHEMA_PATH)
        fm = {"description": "x", "agent_scripts": {"sh": "scripts/bash/a.sh"}}
        errors = validate_frontmatter_against_schema(fm, schema)
        assert any("requires 'scripts'" in e for e in errors)
