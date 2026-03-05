# GitHub Copilot Instructions for Spec-Kit Development

## 🔗 MANDATORY: Use Sourcegraph MCP for All Code Analysis

**Critical Rule**: When working on spec-kit codebase, you **MUST** use the `sourcegraph-mcp` tool for any code understanding, analysis, or navigation task. Do NOT rely solely on context windows or memory.

---

## When to Use Sourcegraph MCP

### Always Use MCP For:

1. **Understanding existing code patterns**
   - Searching for similar implementations
   - Finding function/class definitions
   - Locating where a symbol is used
   - Example: `mcp_search: "AGENT_CONFIG lang:python"` → understand agent registration pattern

2. **Analyzing templates and commands**
   - Understanding handoff flows between speckit.* commands
   - Finding template field references
   - Checking naming conventions across templates
   - Example: `mcp_search: "speckit.specify|speckit.plan lang:markdown"` → trace workflow

3. **Validating changes against the codebase**
   - Checking for breaking changes
   - Ensuring consistent patterns
   - Finding all affected files
   - Example: `mcp_search: "NEEDS CLARIFICATION|ERROR lang:markdown"` → find all validation gates

4. **Understanding script behavior**
   - Bash/PowerShell script logic
   - JSON output structure
   - Environment variables and arguments
   - Example: `mcp_search: "create-new-feature|setup-plan"` → understand script flow

5. **Tracing dependencies**
   - Agent dependencies and requires_cli flags
   - Template includes and references
   - Test coverage and requirements
   - Example: `mcp_search: "requires_cli.*True|install_url"` → find CLI tool requirements

---

## MCP Query Templates for Spec-Kit

Replace `{SEARCH_TERM}` with specific keywords:

### Agent & CLI Configuration
```
mcp_search: "AGENT_CONFIG {SEARCH_TERM} lang:python"
mcp_search: "requires_cli {SEARCH_TERM} lang:python"
mcp_search: "{AGENT_NAME} org:bigsmartben repo:bb-spec-kit"
```

### Templates & Commands
```
mcp_search: "speckit.{COMMAND} lang:markdown"
mcp_search: "{TEMPLATE_NAME}-template lang:markdown path:templates/"
mcp_search: "handoffs|scripts lang:markdown path:templates/commands/"
```

### Scripts & Automation
```
mcp_search: "create-new-feature|setup-plan lang:bash lang:powershell"
mcp_search: "{FUNCTION_NAME} lang:python lang:bash"
mcp_search: "JSON|--json lang:bash path:scripts/"
```

### Test & Validation
```
mcp_search: "REQUIRED_AGENTS|test_init lang:python"
mcp_search: "assert|expect path:tests/"
```

---

## Enforcement Checklist

Before writing or modifying code, ask yourself:

- [ ] **Have I searched the codebase** using `mcp_search` for similar patterns?
- [ ] **Do I understand the current implementation** by reviewing actual code (via MCP fetch_content)?
- [ ] **Have I checked for breaking changes** by searching all references to the symbol I'm modifying?
- [ ] **Are there tests I should review** that exercise this code path?
- [ ] **Is there documentation** (templates, scripts, comments) that explains conventions?

**If you cannot answer "yes" to all checks → USE SOURCEGRAPH MCP before proceeding.**

---

## Common Spec-Kit Workflows

### Adding a New Agent Support
1. `mcp_search: "AGENT_CONFIG lang:python"` → Find registration location
2. `mcp_fetch_content: "github.com/bigsmartben/bb-spec-kit" path:"src/specify_cli"` → Review structure  
3. `mcp_search: "requires_cli|commands_subdir"` → Understand all required fields
4. `mcp_search: "claude|copilot"` → Study existing agent patterns
5. `mcp_search: "agent_scripts|update-agent-context"` → Check agent context requirements

### Modifying a Command Template
1. `mcp_search: "speckit.{COMMAND} lang:markdown"` → Find the command
2. `mcp_search: "handoffs|scripts"` → Understand handoff structure
3. `mcp_fetch_content: "github.com/bigsmartben/bb-spec-kit" path:"templates/commands/{COMMAND}.md"` → Review full context
4. `mcp_search: "{COMMAND}" path:tests/` → Check test expectations
5. `mcp_search: "{TEMPLATE_OUTPUT_FILE}-template"` → Understand output structure

### Debugging Test Failures
1. `mcp_search: "test_{AGENT_NAME}|REQUIRED_AGENTS lang:python"` → Find test definition
2. `mcp_fetch_content: "tests/test_init_agents.py"` → Review test structure
3. `mcp_search: "check_tool|verify"` → Understand validation logic
4. `mcp_search: "ERROR|assert" path:tests/` → Find all assertions in tests

### Understanding the Build/Release Process
1. `mcp_search: "create-release-packages|create-github-release"` → Find automation
2. `mcp_fetch_content: ".github/workflows/"` → Review workflow structure
3. `mcp_search: "ALL_AGENTS|agent_list"` → Find where agents are enumerated
4. `mcp_search: "generate_commands|mkdir"` → Understand directory structure

---

## MCP Tool Reference

### Primary Tools for Spec-Kit

| Tool | Usage | Example |
|------|-------|---------|
| **mcp_search** | Find code, text, patterns | `mcp_search: "AGENT_CONFIG lang:python"` |
| **mcp_fetch_content** | Read file/directory content | `mcp_fetch_content: repo:"github.com/bigsmartben/bb-spec-kit" path:"src/"` |
| **mcp_search_code** | GitHub-native code search | Used for cross-repository searches |

### Never Skip MCP For:
- ❌ "I know where this is" → Verify with `mcp_search` anyway
- ❌ "It's a small change" → Check for side effects with `mcp_search`
- ❌ "I'll search later" → Search NOW before writing code
- ❌ "Just following the pattern" → Ensure pattern is correct via MCP

---

## Violations & Recovery

**What happens if you forget to use MCP:**
- Your analysis may be outdated or incomplete
- You might miss files that need updating
- Breaking changes could be introduced
- Tests might fail due to incorrect assumptions

**If you realize mid-task:**
1. Stop immediately
2. Run `mcp_search` for the relevant symbol/pattern
3. Review the results
4. Revise your approach based on actual code

---

## Examples of Mandatory MCP Usage

### Example 1: Modifying AGENT_CONFIG
```
TASK: Add support for "new-agent-cli"

❌ WRONG:
  - Assume the structure based on "claude" example
  - Add to AGENT_CONFIG dict directly
  
✅ CORRECT:
  - mcp_search: "AGENT_CONFIG._*requires_cli" → understand all config fields
  - mcp_search: "claude.*name.*folder.*commands_subdir" → precision
  - mcp_fetch_content: "src/specify_cli/__init__.py" → full AGENT_CONFIG review
  - mcp_search: "new-agent-cli" → verify not already present
  - mcp_search: "cli_tool.*where|check_tool.*implement" → verify CLI checking
  - THEN add the new agent entry
```

### Example 2: Updating a Command Template
```
TASK: Add new validation rule to speckit.specify

❌ WRONG:
  - Edit templates/commands/specify.md based on memory
  - Hope the changes align with test expectations

✅ CORRECT:
  - mcp_fetch_content: "templates/commands/specify.md" → review full command
  - mcp_search: "test_.*specify|REQUIRED_AGENTS" → find related tests
  - mcp_search: "NEEDS CLARIFICATION|ERROR" → understand validation gates
  - mcp_fetch_content: "tests/test_speckit_commands.py" → understand test structure
  - mcp_search: "assertion.*specify" → find assertions
  - THEN make the change with full understanding
```

### Example 3: Adding Agent Support to Scripts
```
TASK: Update create-release-packages.sh for new agent

❌ WRONG:
  - Copy-paste a similar agent block
  - Hope directory structure is correct

✅ CORRECT:
  - mcp_fetch_content: ".github/workflows/scripts/create-release-packages.sh" → full script
  - mcp_search: "case \$agent|mkdir.*agent" → understand the pattern
  - mcp_search: "claude.*commands|windsurf.*workflows" → verify directory names
  - mcp_search: "generate_commands.*function" → understand helper function
  - mcp_search: "ALL_AGENTS.*array" → find agent enumeration
  - THEN make minimal, precise changes
```

---

## Questions Before Every Change

1. **Does this change affect multiple files?** → Use `mcp_search` to find all
2. **Is there a test for this?** → Find it with `mcp_search` and review
3. **What's the established pattern?** → Study 2-3 examples via `mcp_fetch_content`
4. **Could this break backward compatibility?** → Search for all usages
5. **Are there similar features already?** → Search for them first

---

## Version Notice

Last updated: **March 5, 2026**  
Scope: All Codex/Claude/Copilot/Cursor/Opencode/Roo developers working on spec-kit  
Enforcement: **MANDATORY for all AI-assisted coding**

---

*This document enforces disciplined MCP usage to ensure consistent, reliable analysis and comprehensive code understanding for spec-kit development.*
