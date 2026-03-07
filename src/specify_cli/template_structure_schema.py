"""Lightweight structure-schema validation for markdown templates.

Phase 2 goal: validate mandatory headings in spec/plan templates without
changing the existing markdown-first authoring model.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml


def load_template_structure_schema(schema_path: Path) -> dict:
    """Load a template structure schema from YAML."""
    if not schema_path.exists():
        raise FileNotFoundError(f"Template structure schema not found: {schema_path}")

    data = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid template structure schema format in: {schema_path}")
    return data


def validate_markdown_template_structure(content: str, schema: dict) -> list[str]:
    """Validate markdown template content against required headings/patterns."""
    errors: list[str] = []

    required_headings = schema.get("required_headings", [])
    required_patterns = schema.get("required_patterns", [])

    for heading in required_headings:
        if heading not in content:
            errors.append(f"missing required heading: {heading}")

    for pattern in required_patterns:
        if not re.search(pattern, content, flags=re.MULTILINE):
            errors.append(f"missing required pattern: {pattern}")

    return errors
