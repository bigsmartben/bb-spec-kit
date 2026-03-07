from pathlib import Path

from specify_cli import AGENT_CONFIG, _generate_commands_for_agent


def test_cline_agent_config():
    cfg = AGENT_CONFIG["cline"]
    assert cfg["name"] == "Cline"
    assert cfg["folder"] == ".cline/"
    assert cfg["commands_subdir"] == "workflows"
    assert cfg["requires_cli"] is False


def test_generate_cline_prompt_md_commands(tmp_path: Path):
    commands_src = tmp_path / "templates" / "commands"
    commands_src.mkdir(parents=True)
    (commands_src / "specify.md").write_text(
        "---\n"
        'description: "Specify command"\n'
        "scripts:\n"
        "  sh: scripts/bash/create-new-feature.sh\n"
        "  ps: scripts/powershell/create-new-feature.ps1\n"
        "---\n"
        "\n"
        "Use {SCRIPT} with {ARGS}\n",
        encoding="utf-8",
    )

    base_dir = tmp_path / "out"
    base_dir.mkdir()

    _generate_commands_for_agent("cline", "sh", commands_src, base_dir)

    output_file = base_dir / ".cline" / "workflows" / "sdd.specify.prompt.md"
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "$ARGUMENTS" in content
    assert "{ARGS}" not in content
