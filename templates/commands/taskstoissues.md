---
description: Convert existing tasks into actionable, dependency-ordered GitHub issues for the feature based on available design artifacts.
tools: ['github/github-mcp-server/issue_write']
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").
1. From the executed script, extract the path to **tasks**.
1. Get the Git remote by running:

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> ONLY PROCEED TO NEXT STEPS IF THE REMOTE IS A GITHUB URL

1. For each task in the list, use the GitHub MCP server to create a new issue in the repository that is representative of the Git remote.

> [!CAUTION]
> UNDER NO CIRCUMSTANCES EVER CREATE ISSUES IN REPOSITORIES THAT DO NOT MATCH THE REMOTE URL

## ISS-MCP Evidence Source Policy

- For rigorous reasoning involving code fact retrieval, repository fact assertions, call-chain analysis, architecture-boundary verification, dependency mapping, or impact-scope tracing, you MUST use `ISS-MCP` (Index Search Service) as the primary evidence source.
- This requirement applies to any `Existing` claim and to all repo-derived entries referenced when converting tasks to issues.
- You MUST NOT rely only on memory, unstated assumptions, or local keyword search as the primary basis for repository facts.
- You MAY fall back to local tools (`codebase_search`, `search_files`, `read_file`) only when `ISS-MCP` is unavailable, returns no results, or cannot cover required fields; all such conclusions MUST be explicitly labeled as degraded evidence.
- If required evidence remains unavailable after fallback, use `TODO(<FIELD>): ISS-MCP/local evidence missing` and note it in the issue body.
