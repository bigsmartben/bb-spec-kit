# Universal MCP Instructions for Spec-Kit Development

**Applies to**: All AI coding assistants (Claude, Gemini, Cursor, Codex, Opencode, etc.)

---

## The MCP Mandate

**When working on spec-kit:**

You **MUST** use `sourcegraph-mcp` to search, fetch, and analyze code. This is the authoritative source of truth for the spec-kit codebase.

**Why?**
- Ensures accuracy and prevents hallucinations
- Catches dependencies and side effects
- Validates against actual code structure
- Keeps changes minimal and focused
- Prevents breaking changes

---

## MCP Workflow

### Step 1: Understand Current State
```
mcp_search → Find the element you're modifying
mcp_fetch_content → Read the actual file content
mcp_search → Find all usages and references
```

### Step 2: Study the Pattern
```
mcp_fetch_content → Read similar examples
mcp_search → Find how this pattern is used elsewhere
mcp_search → Check test expectations
```

### Step 3: Plan the Change
```
With full context from MCP, now you can safely plan
- Identify all files to modify
- Ensure pattern consistency
- Check for breaking changes
```

### Step 4: Make the Change
```
Make minimal, focused changes based on actual code understanding
```

### Step 5: Verify
```
mcp_search → Confirm all affected references
mcp_search → Find related tests
mcp_fetch_content → Review test expectations
```

---

## Spec-Kit MCP Query Reference

### Core Searches

**Find agent configuration**:
```
mcp_search: "AGENT_CONFIG" lang:python
mcp_search: "requires_cli" lang:python
mcp_search: "{AGENT_NAME}" lang:python
```

**Find command/template**:
```
mcp_search: "speckit.{COMMAND}" lang:markdown
mcp_search: "{COMMAND}-template" lang:markdown path:templates/
mcp_search: "handoff.*agent" lang:markdown path:templates/commands/
```

**Find scripts**:
```
mcp_search: "create-new-feature|setup-plan|update-agent-context" lang:bash lang:powershell
mcp_search: "ALL_AGENTS" lang:bash lang:powershell
mcp_search: "{FUNCTION_NAME}" lang:bash
```

**Find tests**:
```
mcp_search: "REQUIRED_AGENTS" lang:python
mcp_search: "test_{FEATURE}" lang:python
mcp_search: "assert|expect" path:tests/ lang:python
```

**Find all references**:
```
mcp_search: "{SYMBOL_NAME}"
(Include all file types, don't filter by language)
```

### Fetch File Content

**Repository structure**:
```
mcp_fetch_content: "github.com/bigsmartben/bb-spec-kit" path:""
```

**Specific directory**:
```
mcp_fetch_content: "github.com/bigsmartben/bb-spec-kit" path:"src/specify_cli"
```

**Specific file**:
```
mcp_fetch_content: "github.com/bigsmartben/bb-spec-kit" path:"src/specify_cli/__init__.py"
```

---

## Task Checklist

### Before Every Change

- [ ] What exact symbol/file am I modifying?
- [ ] Have I searched for its current definition?
- [ ] Have I found all usages and references?
- [ ] Have I reviewed the actual implementation?
- [ ] Have I identified related tests?
- [ ] Have I understood the established pattern?
- [ ] Am I confident about breaking changes?

**If any box is unchecked → USE MCP FIRST BEFORE PROCEEDING**

---

## Common Spec-Kit Tasks

### Adding New Agent Support
```
1. mcp_search: "AGENT_CONFIG" → Find configuration
2. mcp_search: "claude|gemini|copilot" → Study existing agents
3. mcp_fetch_content: "src/specify_cli/__init__.py" → Full config review
4. mcp_search: "requires_cli|commands_subdir" → Understand all fields
5. mcp_search: "check_tool|install_url" → Understand validation
6. mcp_search: "test_.*_init_creates" → Review test patterns
7. mcp_search: "update-agent-context" → Check script requirements
→ NOW add the agent
```

### Modifying Command Template (e.g., speckit.specify)
```
1. mcp_search: "speckit.specify" lang:markdown → Find command
2. mcp_fetch_content: "templates/commands/specify.md" → Full review
3. mcp_search: "NEEDS CLARIFICATION|ERROR" → Understand validators
4. mcp_search: "specify.*handoff" → Check handoff targets
5. mcp_fetch_content: "templates/spec-template.md" → Output template
6. mcp_search: "test_.*specify" lang:python → Find tests
7. mcp_fetch_content: "tests/test_speckit_commands.py" → Test expectations
→ NOW modify the command
```

### Adding to Release Package Scripts
```
1. mcp_fetch_content: ".github/workflows/scripts/create-release-packages.sh"
2. mcp_search: "ALL_AGENTS" → Find agent list
3. mcp_search: "case.*agent|mkdir.*agent" → Find pattern
4. mcp_search: "{AGENT_NAME}.*folder" → Known folder name
5. mcp_search: "generate_commands" → Understand helper function
6. Also check PowerShell: create-release-packages.ps1
→ NOW add agent to BOTH scripts
```

### Debugging Test Failures
```
1. mcp_search: "test_.*{FAILING_TEST}" lang:python → Find test
2. mcp_fetch_content: "tests/test_*.py" → Review test file
3. mcp_search: "{ASSERTION_SUBJECT}" → Find related code
4. mcp_search: "ERROR|WARN" lang:python → Check error handling
→ NOW determine fix
```

---

## Non-Negotiable Rules

### ✅ MUST DO

- ✅ Search for the symbol before modifying
- ✅ Read actual file content via mcp_fetch_content
- ✅ Find all usages via mcp_search
- ✅ Review test expectations
- ✅ Verify against existing patterns
- ✅ Check for breaking changes

### ❌ MUST NOT DO

- ❌ Skip MCP searches to "save time"
- ❌ Rely on context/memory instead of actual code
- ❌ Assume directory structure or naming
- ❌ Copy-paste patterns without verification
- ❌ Make "quick" changes without understanding impact
- ❌ Modify files without searching for tests

---

## MCP Tool Syntax

### Search
```
mcp_search(query: str, language: optional, path_filter: optional) → Results
```

**Examples**:
```
mcp_search: "AGENT_CONFIG" lang:python
mcp_search: "speckit\." lang:markdown
mcp_search: "import.*sourcegraph" lang:python
mcp_search: "def check_tool" lang:python path:src/
```

### Fetch Content
```
mcp_fetch_content(repo: str, path: str) → File or Directory Content
```

**Examples**:
```
mcp_fetch_content: repo:"github.com/bigsmartben/bb-spec-kit" path:"src/"
mcp_fetch_content: repo:"github.com/bigsmartben/bb-spec-kit" path:"templates/commands/specify.md"
mcp_fetch_content: repo:"github.com/bigsmartben/bb-spec-kit" path:".github/workflows/scripts/"
```

---

## Recovery Protocol

**If you realize you skipped MCP partway through:**

1. STOP immediately
2. Run the appropriate mcp_search or mcp_fetch_content
3. Review the results
4. Adjust your approach
5. Resume with full understanding

---

## Violation Consequences

| If You Skip MCP | Likely Outcome |
|-----------------|----------------|
| Make change without searching | Miss other files needing updates |
| Copy pattern from memory | Create inconsistencies or errors |
| Assume file structure | Break downstream automation |
| Skip test review | Introduce test failures |
| Ignore all usages | Create breaking changes |

---

## Questions?

**Before asking, search MCP first.**

99% of spec-kit questions can be answered by:
```
1. mcp_search: "{YOUR_QUESTION}"
2. mcp_fetch_content: "relevant/path"
3. mcp_search: "related_pattern"
```

---

**Last Updated**: March 5, 2026  
**Enforcement Level**: MANDATORY  
**Scope**: All AI-coding assistance on spec-kit  

*This guidance ensures spec-kit maintains code quality, consistency, and reliability.*
