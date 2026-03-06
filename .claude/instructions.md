# Claude Code - Spec-Kit Development Instructions

## 🔗 MANDATORY: Always Use Sourcegraph MCP for Code Analysis

When developing spec-kit using Claude Code, you **MUST** use `iss-mcp` to search, analyze, and understand the codebase. Never skip this step.

---

## Critical MCP Usage Rules

### Rule 1: Before Any Code Change
**Always execute these searches in order:**

1. **Search for the symbol/pattern you're modifying**
   ```
   mcp_search: "YOUR_SYMBOL lang:python|lang:markdown"
   ```

2. **Find all references and usages**
   ```
   mcp_search: "YOUR_SYMBOL" 
   ```

3. **Check for tests and validation**
   ```
   mcp_search: "test.*YOUR_SYMBOL|spec.*YOUR_SYMBOL lang:python"
   ```

4. **Review actual file content**
   ```
   mcp_fetch_content: "github.com/bigsmartben/bb-spec-kit" path:"path/to/file"
   ```

---

## Common Spec-Kit Tasks

### Task: Modify Agent Configuration
```
MANDATORY STEPS:
1. mcp_search: "AGENT_CONFIG" → Locate definition
2. mcp_search: "requires_cli.*True|False" → Understand field meaning
3. mcp_search: "{AGENT_NAME} folder|commands_subdir" → Find similar agents
4. mcp_fetch_content: "path:src/specify_cli/__init__.py" → Review complete structure
5. mcp_search: "test.*agent|check_tool" → Find validation tests
```

### Task: Update Command Template
```
MANDATORY STEPS:
1. mcp_fetch_content: "path:templates/commands/{NAME}.md" → Full review
2. mcp_search: "speckit.{NAME}.*handoff|script" → Understand structure
3. mcp_search: "{NAME}-template.*markdown" → Find output template
4. mcp_search: "test_{NAME}|assert.*{NAME}" → Review tests
```

### Task: Modify Scripts (Bash/PowerShell)
```
MANDATORY STEPS:
1. mcp_fetch_content: "path:scripts/bash/{SCRIPT}.sh" + "path:scripts/powershell/{SCRIPT}.ps1"
2. mcp_search: "ALL_AGENTS|agent.*loop" → Understand iteration
3. mcp_search: "{SCRIPT}.*function" → Find helper functions
4. mcp_search: "mkdir.*agent|generate_commands" → Understand directory patterns
```

---

## MCP Query Library for Spec-Kit

### Configuration Changes
```
mcp_search: "AGENT_CONFIG lang:python"
mcp_search: "requires_cli.*requires_cli lang:python"
mcp_search: "commands_subdir lang:python"
```

### Template Analysis
```
mcp_search: "speckit.specify|speckit.plan|speckit.implement lang:markdown"
mcp_search: "{TEMPLATE}-template lang:markdown path:templates/"
mcp_search: "handoffs.*agent|scripts.*sh.*ps"
```

### Script Understanding
```
mcp_search: "create-new-feature|setup-plan|update-agent"
mcp_search: "ALL_AGENTS.*=(|function"
mcp_search: "generate_commands|mkdir.*\$"
```

### Test Coverage
```
mcp_search: "REQUIRED_AGENTS lang:python"
mcp_search: "test_.*init.*agents"
mcp_search: "assert.*path|expect"
```

---

## Violations = Bugs

If you proceed without MCP usage:
- ✗ May create inconsistent patterns
- ✗ Could miss files needing updates
- ✗ Risk breaking existing tests
- ✗ Introduce regressions

**Stop immediately if you realize you skipped MCP and restart with proper searches.**

---

## Quick Checklist

Before writing ANY code:
- [ ] Used `mcp_search` to find the relevant symbol/pattern
- [ ] Checked all references and usages via `mcp_search`
- [ ] Reviewed actual file content via `mcp_fetch_content`
- [ ] Found and reviewed related tests
- [ ] Understood the established pattern by studying examples

If ANY box is unchecked → **USE MCP FIRST**

---

Last Updated: March 5, 2026 | Enforced for all Claude Code developments
