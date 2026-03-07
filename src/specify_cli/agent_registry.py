"""Single source of truth for Spec Kit agent metadata."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class AgentMeta:
    """Metadata used across CLI, extensions, release packaging, and docs."""

    key: str
    name: str
    folder: str | None
    commands_subdir: str
    install_url: str | None
    requires_cli: bool
    command_format: str
    output_extension: str
    arg_placeholder: str
    template_folder: str
    supports_extensions: bool = True
    include_in_release: bool = True
    include_in_docs: bool = True


_AGENTS: tuple[AgentMeta, ...] = (
    AgentMeta(
        key="copilot",
        name="GitHub Copilot",
        folder=".github/",
        commands_subdir="agents",
        install_url=None,
        requires_cli=False,
        command_format="markdown",
        output_extension=".agent.md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".github/",
    ),
    AgentMeta(
        key="claude",
        name="Claude Code",
        folder=".claude/",
        commands_subdir="commands",
        install_url="https://docs.anthropic.com/en/docs/claude-code/setup",
        requires_cli=True,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".claude/",
    ),
    AgentMeta(
        key="gemini",
        name="Gemini CLI",
        folder=".gemini/",
        commands_subdir="commands",
        install_url="https://github.com/google-gemini/gemini-cli",
        requires_cli=True,
        command_format="toml",
        output_extension=".toml",
        arg_placeholder="{{args}}",
        template_folder=".gemini/",
    ),
    AgentMeta(
        key="cursor-agent",
        name="Cursor",
        folder=".cursor/",
        commands_subdir="commands",
        install_url=None,
        requires_cli=False,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".cursor/",
    ),
    AgentMeta(
        key="qwen",
        name="Qwen Code",
        folder=".qwen/",
        commands_subdir="commands",
        install_url="https://github.com/QwenLM/qwen-code",
        requires_cli=True,
        command_format="toml",
        output_extension=".toml",
        arg_placeholder="{{args}}",
        template_folder=".qwen/",
    ),
    AgentMeta(
        key="opencode",
        name="opencode",
        folder=".opencode/",
        commands_subdir="command",
        install_url="https://opencode.ai",
        requires_cli=True,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".opencode/",
    ),
    AgentMeta(
        key="codex",
        name="Codex CLI",
        folder=".codex/",
        commands_subdir="prompts",
        install_url="https://github.com/openai/codex",
        requires_cli=False,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".codex/",
    ),
    AgentMeta(
        key="windsurf",
        name="Windsurf",
        folder=".windsurf/",
        commands_subdir="workflows",
        install_url=None,
        requires_cli=False,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".windsurf/",
    ),
    AgentMeta(
        key="kilocode",
        name="Kilo Code",
        folder=".kilocode/",
        commands_subdir="workflows",
        install_url=None,
        requires_cli=False,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".kilocode/",
    ),
    AgentMeta(
        key="auggie",
        name="Auggie CLI",
        folder=".augment/",
        commands_subdir="commands",
        install_url="https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
        requires_cli=True,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".augment/",
    ),
    AgentMeta(
        key="codebuddy",
        name="CodeBuddy",
        folder=".codebuddy/",
        commands_subdir="commands",
        install_url="https://www.codebuddy.ai/cli",
        requires_cli=True,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".codebuddy/",
    ),
    AgentMeta(
        key="cline",
        name="Cline",
        folder=".cline/",
        commands_subdir="workflows",
        install_url=None,
        requires_cli=False,
        command_format="markdown",
        output_extension=".prompt.md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".cline/",
    ),
    AgentMeta(
        key="qodercli",
        name="Qoder CLI",
        folder=".qoder/",
        commands_subdir="commands",
        install_url="https://qoder.com/cli",
        requires_cli=True,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".qoder/",
    ),
    AgentMeta(
        key="roo",
        name="Roo Code",
        folder=".roo/",
        commands_subdir="commands",
        install_url=None,
        requires_cli=False,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".roo/",
    ),
    AgentMeta(
        key="q",
        name="Amazon Q Developer CLI",
        folder=".amazonq/",
        commands_subdir="prompts",
        install_url="https://aws.amazon.com/developer/learning/q-developer-cli/",
        requires_cli=True,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".amazonq/",
    ),
    AgentMeta(
        key="amp",
        name="Amp",
        folder=".agents/",
        commands_subdir="commands",
        install_url="https://ampcode.com/manual#install",
        requires_cli=True,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".agents/",
    ),
    AgentMeta(
        key="shai",
        name="SHAI",
        folder=".shai/",
        commands_subdir="commands",
        install_url="https://github.com/ovh/shai",
        requires_cli=True,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".shai/",
    ),
    AgentMeta(
        key="agy",
        name="Antigravity",
        folder=".agent/",
        commands_subdir="workflows",
        install_url=None,
        requires_cli=False,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".agent/",
    ),
    AgentMeta(
        key="bob",
        name="IBM Bob",
        folder=".bob/",
        commands_subdir="commands",
        install_url=None,
        requires_cli=False,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".bob/",
    ),
    AgentMeta(
        key="generic",
        name="Generic (bring your own agent)",
        folder=None,
        commands_subdir="commands",
        install_url=None,
        requires_cli=False,
        command_format="markdown",
        output_extension=".md",
        arg_placeholder="$ARGUMENTS",
        template_folder=".speckit/",
        supports_extensions=False,
    ),
)


def get_agent_registry() -> "OrderedDict[str, AgentMeta]":
    """Return ordered registry keyed by agent key."""

    return OrderedDict((agent.key, agent) for agent in _AGENTS)


AGENT_REGISTRY = get_agent_registry()


def build_cli_agent_config() -> Dict[str, Dict[str, object]]:
    """Project metadata used by CLI init/check behavior."""

    return {
        key: {
            "name": meta.name,
            "folder": meta.folder,
            "commands_subdir": meta.commands_subdir,
            "install_url": meta.install_url,
            "requires_cli": meta.requires_cli,
        }
        for key, meta in AGENT_REGISTRY.items()
    }


def build_extension_agent_configs() -> Dict[str, Dict[str, str]]:
    """Project metadata used by extension command registration."""

    result: Dict[str, Dict[str, str]] = {}
    for key, meta in AGENT_REGISTRY.items():
        if not meta.supports_extensions:
            continue
        result[key] = {
            "dir": f"{meta.template_folder.rstrip('/')}/{meta.commands_subdir}",
            "format": meta.command_format,
            "args": meta.arg_placeholder,
            "extension": meta.output_extension,
        }
    return result


def release_agent_keys() -> List[str]:
    """Ordered agent keys expected in release scripts."""

    return [meta.key for meta in _AGENTS if meta.include_in_release]


def documented_agent_keys() -> List[str]:
    """Ordered agent keys expected in machine-readable docs blocks."""

    return [meta.key for meta in _AGENTS if meta.include_in_docs]
