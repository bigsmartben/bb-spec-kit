# Cursor - Spec-Kit Development Instructions

## 🔗 MANDATORY: Use Sourcegraph MCP in All Code Tasks

When working on spec-kit in Cursor IDE, you **MUST** use `sourcegraph-mcp` to understand, search, and navigate the codebase. This is non-negotiable.

---

## Core Rules

### Rule 1: Every Task Starts with MCP Search
```
Before touching any file:
  1. Run mcp_search for the element you're examining
  2. Run mcp_fetch_content to read actual file
  3. Run mcp_search for all references
  4. Study 2-3 examples of the pattern
```

### Rule 2: No Assumptions
```
❌ DON'T:
  - Assume directory structure from memory
  - Copy-paste patterns without verification
  - Make changes based on partial context

✅ DO:
  - mcp_search for exact reference
  - mcp_fetch_content the actual file
  - mcp_search for all usages
  - Then make informed change
```

### Rule 3: Validation Before Commit
```
For every change:
  1. mcp_search for related tests
  2. mcp_search for all affected symbols
  3. mcp_fetch_content to verify breaking changes
  4. Review test expectations via mcp_fetch_content
```

---

## Essential MCP Queries for Spec-Kit

### Agent Configuration
```
mcp_search: "AGENT_CONFIG" lang:python
mcp_search: "requires_cli" lang:python
mcp_search: "commands_subdir" lang:python
```

### Templates & Commands
```
mcp_search: "speckit\." lang:markdown
mcp_search: "-template" lang:markdown path:templates/
mcp_search: "handoff.*agent" lang:markdown
```

### Scripts
```
mcp_search: "bash\|powershell" lang:bash lang:powershell
mcp_search: "create-new-feature\|setup-plan"
mcp_search: "ALL_AGENTS"
```

### Testing
```
mcp_search: "REQUIRED_AGENTS" lang:python
mcp_search: "test_" lang:python
mcp_search: "assert" path:tests/
```

---

## Task Examples

### Modify AGENT_CONFIG
```
Step 1: mcp_search "AGENT_CONFIG.*dict"
Step 2: mcp_search "claude\|gemini\|copilot" → Review structure
Step 3: mcp_fetch_content "src/specify_cli/__init__.py" → Full context
Step 4: mcp_search "\{AGENT_NAME\}" → Find all references
Step 5: Now safe to modify
```

### Update Command Template
```
Step 1: mcp_search "speckit\.\{COMMAND\}"
Step 2: mcp_fetch_content "templates/commands/\{COMMAND\}.md"
Step 3: mcp_search "test.*\{COMMAND\}" lang:python
Step 4: mcp_search "\{COMMAND\}-template"
Step 5: Now update safely
```

### Add Agent to Scripts
```
Step 1: mcp_fetch_content "scripts/bash/create-release-packages.sh"
Step 2: mcp_search "case.*agent\|ALL_AGENTS"
Step 3: mcp_search "\{AGENT_FOLDER\}" path:scripts/
Step 4: mcp_search "mkdir.*\{AGENT_NAME\}" → All references
Step 5: Make changes in both bash AND powershell
```

---

## Cursor-Specific Usage

### Use Cursor's MCP Tool Button
1. Open Command Palette: `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Search for "MCP: Use Tool"
3. Select the mcp_search tool
4. Enter your query with proper syntax

### Keep MCP Tool Panel Open
- Keep the MCP Tools panel visible in VS Code
- Reference search results while editing
- Don't rely on memory of search results

### Symbol Navigation with MCP
- Use `mcp_search: "def.*SYMBOL"` to find definitions
- Use `mcp_search: "SYMBOL" (lang:python OR lang:bash OR lang:markdown)` to find all usages
- Use `mcp_fetch_content` to read full files without opening them

---

## Validation Checklist

✅ Before writing code, confirm:
- [ ] Found the symbol via `mcp_search`
- [ ] Reviewed actual implementation via `mcp_fetch_content`
- [ ] Searched for all usages/references
- [ ] Located and understood existing tests
- [ ] Identified the pattern to follow

❌ If any checkbox is empty → **RUN MCP SEARCH FIRST**

---

## Common Mistakes to Avoid

| ❌ Wrong | ✅ Right |
|---------|---------|
| Assuming directory structure | mcp_search + mcp_fetch_content first |
| Copy-pasting pattern from memory | Find actual pattern in code via MCP |
| Making change without checking tests | mcp_search for test files first |
| Skipping "small" changes | Even small changes need MCP verification |
| Forgetting to update both bash and PS | mcp_search to find BOTH files |

---

## Quick Reference

| Need | MCP Query |
|------|-----------|
| Find agent config | `mcp_search: "AGENT_CONFIG"` |
| Find command | `mcp_search: "speckit\.\{CMD\}" lang:markdown` |
| Find script | `mcp_search: "\{SCRIPT\}\.sh\|\.ps1"` |
| Find tests | `mcp_search: "test_\{NAME\}" lang:python` |
| Find all references | `mcp_search: "\{SYMBOL\}"` (no lang filter) |
| Read file | `mcp_fetch_content: "path:to/file"` |

---

Last Updated: March 5, 2026 | Enforced for all Cursor AI-coding sessions
