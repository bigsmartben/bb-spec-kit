"""Phase 2 tests: markdown template structure schemas for spec/plan."""

from pathlib import Path

from specify_cli.template_structure_schema import (
    load_template_structure_schema,
    validate_markdown_template_structure,
)

ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = ROOT / "templates" / "schemas"


class TestTemplateStructureSchemas:
    def test_spec_template_structure_schema_passes(self):
        schema_path = SCHEMAS_DIR / "spec-template-structure.schema.yaml"
        template_path = ROOT / "templates" / "spec-template.md"

        schema = load_template_structure_schema(schema_path)
        content = template_path.read_text(encoding="utf-8")

        errors = validate_markdown_template_structure(content, schema)
        assert not errors, f"spec-template.md structure errors: {errors}"

    def test_plan_template_structure_schema_passes(self):
        schema_path = SCHEMAS_DIR / "plan-template-structure.schema.yaml"
        template_path = ROOT / "templates" / "plan-template.md"

        schema = load_template_structure_schema(schema_path)
        content = template_path.read_text(encoding="utf-8")

        errors = validate_markdown_template_structure(content, schema)
        assert not errors, f"plan-template.md structure errors: {errors}"

    def test_missing_heading_is_reported(self):
        schema = {
            "required_headings": ["## Must Exist"],
            "required_patterns": [],
        }
        errors = validate_markdown_template_structure("# Title\n", schema)
        assert errors == ["missing required heading: ## Must Exist"]

    def test_missing_pattern_is_reported(self):
        schema = {
            "required_headings": [],
            "required_patterns": [r"^### Required Subheading$"],
        }
        errors = validate_markdown_template_structure("# Title\n", schema)
        assert errors == [r"missing required pattern: ^### Required Subheading$"]
