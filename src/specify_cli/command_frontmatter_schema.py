"""Schema loader and validator for templates/commands frontmatter.

Phase 1 goal: add a lightweight, YAML-driven schema contract for command
frontmatter so CI/tests can enforce consistency without introducing a new
runtime dependency.
"""

from __future__ import annotations

from pathlib import Path

import yaml


def _default_schema_path() -> Path:
    """Resolve command frontmatter schema path in both source and wheel layouts."""
    package_path = Path(__file__).parent / "templates" / "schemas" / "command-frontmatter.schema.yaml"
    if package_path.exists():
        return package_path

    # Source checkout fallback: src/specify_cli/.. -> repo root/templates/schemas
    source_path = Path(__file__).resolve().parents[2] / "templates" / "schemas" / "command-frontmatter.schema.yaml"
    return source_path


def load_command_frontmatter_schema(schema_path: Path | None = None) -> dict:
    """Load schema YAML for command frontmatter validation."""
    path = schema_path or _default_schema_path()
    if not path.exists():
        raise FileNotFoundError(f"Command frontmatter schema not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid command frontmatter schema format in: {path}")
    return data


def validate_frontmatter_against_schema(frontmatter: dict, schema: dict) -> list[str]:
    """Validate one command frontmatter dict against the YAML schema.

    Returns a list of human-readable error messages. Empty list means valid.
    """
    errors: list[str] = []

    if not isinstance(frontmatter, dict):
        return ["frontmatter must be a mapping/object"]

    allowed_keys = set(schema.get("allowed_keys", []))
    required_keys = set(schema.get("required_keys", []))
    fields = schema.get("fields", {})

    # required / unknown keys
    for key in sorted(required_keys):
        if key not in frontmatter:
            errors.append(f"missing required key: '{key}'")

    for key in sorted(frontmatter.keys()):
        if allowed_keys and key not in allowed_keys:
            errors.append(f"unknown key: '{key}'")

    # field-level validation
    for key, value in frontmatter.items():
        spec = fields.get(key)
        if not isinstance(spec, dict):
            continue

        field_type = spec.get("type")
        if field_type == "string":
            if not isinstance(value, str):
                errors.append(f"'{key}' must be a string")
                continue
            min_length = int(spec.get("min_length", 0))
            if len(value.strip()) < min_length:
                errors.append(f"'{key}' must have min length {min_length}")

        elif field_type == "string_list":
            if not isinstance(value, list):
                errors.append(f"'{key}' must be a list")
                continue
            min_items = int(spec.get("min_items", 0))
            if len(value) < min_items:
                errors.append(f"'{key}' must have at least {min_items} items")
            for i, item in enumerate(value):
                if not isinstance(item, str) or not item.strip():
                    errors.append(f"'{key}[{i}]' must be a non-empty string")

        elif field_type == "script_map":
            if not isinstance(value, dict):
                errors.append(f"'{key}' must be a mapping/object")
                continue

            min_entries = int(spec.get("min_entries", 0))
            if len(value) < min_entries:
                errors.append(f"'{key}' must have at least {min_entries} entries")

            allowed_map_keys = set(spec.get("allowed_map_keys", []))
            for map_key, map_value in value.items():
                if allowed_map_keys and map_key not in allowed_map_keys:
                    errors.append(f"'{key}.{map_key}' is not an allowed script key")
                if not isinstance(map_value, str) or not map_value.strip():
                    errors.append(f"'{key}.{map_key}' must be a non-empty string")

        elif field_type == "handoff_list":
            if not isinstance(value, list):
                errors.append(f"'{key}' must be a list")
                continue

            min_items = int(spec.get("min_items", 0))
            if len(value) < min_items:
                errors.append(f"'{key}' must have at least {min_items} items")

            item_required = set(spec.get("item_required_keys", []))
            item_allowed = set(spec.get("item_allowed_keys", []))
            item_fields = spec.get("item_fields", {})

            for i, item in enumerate(value):
                if not isinstance(item, dict):
                    errors.append(f"'{key}[{i}]' must be a mapping/object")
                    continue

                for req in sorted(item_required):
                    if req not in item:
                        errors.append(f"'{key}[{i}]' missing required key: '{req}'")

                for item_key, item_value in item.items():
                    if item_allowed and item_key not in item_allowed:
                        errors.append(f"'{key}[{i}].{item_key}' is not an allowed key")
                        continue

                    expected = item_fields.get(item_key)
                    if expected == "string":
                        if not isinstance(item_value, str) or not item_value.strip():
                            errors.append(f"'{key}[{i}].{item_key}' must be a non-empty string")
                    elif expected == "boolean":
                        if not isinstance(item_value, bool):
                            errors.append(f"'{key}[{i}].{item_key}' must be a boolean")

    # cross-field rules
    for rule in schema.get("cross_rules", []):
        if not isinstance(rule, dict):
            continue
        when_present = rule.get("when_present")
        requires = rule.get("requires")
        if when_present in frontmatter and requires and requires not in frontmatter:
            rule_name = rule.get("name", "unnamed-rule")
            errors.append(f"cross-rule '{rule_name}' failed: '{when_present}' requires '{requires}'")

    return errors


def validate_command_frontmatter(frontmatter: dict, schema_path: Path | None = None) -> list[str]:
    """Convenience wrapper: load default schema and validate frontmatter."""
    schema = load_command_frontmatter_schema(schema_path=schema_path)
    return validate_frontmatter_against_schema(frontmatter, schema)
