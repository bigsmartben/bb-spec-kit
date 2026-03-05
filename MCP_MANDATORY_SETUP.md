# 🔗 Spec-Kit MCP 强制使用指南

**当前状态**: ✅ 已启用强制 MCP 模式

---

## 快速开始

### 为什么强制使用 MCP？

在 spec-kit 开发中，使用 AI 时强制调用 `sourcegraph-mcp` 可以：
- ✅ 确保代码分析精确，避免幻觉
- ✅ 捕捉依赖关系和副作用
- ✅ 验证实际代码结构
- ✅ 防止破坏性更改
- ✅ 保持变更最小化和聚焦

---

## 配置文件位置

| Agent | 指令文件 | 用途 |
|------|---------|------|
| **GitHub Copilot** | `.github/copilot-instructions.md` | VS Code 中的 Copilot 聊天 |
| **Claude Code** | `.claude/instructions.md` | Claude 官方开发工具 |
| **Cursor** | `.cursor/instructions.md` | Cursor IDE |
| **通用（所有 Agent）** | `.agents/mcp-instructions.md` | 其他所有 AI coding 助手 |

---

## 核心工作流

### 三步验证法（必须跟随）

```python
# Step 1: 理解当前状态
mcp_search: "YOUR_SYMBOL"                        # 找定义
mcp_fetch_content: "path/to/file"               # 读实际代码
mcp_search: "YOUR_SYMBOL" (所有文件)             # 找所有引用

# Step 2: 学习模式
mcp_fetch_content: "similar/example/file"       # 学习相似实现
mcp_search: "related_pattern"                   # 找模式使用处
mcp_search: "test_YOUR_SYMBOL" lang:python      # 找相关测试

# Step 3: 制定变更
有了完整上下文，现在可以安全地计划改动
```

---

## 常见 MCP 查询

### Agent 配置
```bash
mcp_search: "AGENT_CONFIG" lang:python
mcp_search: "requires_cli.*True" lang:python
mcp_search: "{AGENT_NAME}" org:bigsmartben
```

### 模板和命令
```bash
mcp_search: "speckit\." lang:markdown
mcp_search: "{COMMAND}-template" lang:markdown
mcp_search: "handoff.*agent" lang:markdown
```

### 脚本（Bash/PowerShell）
```bash
mcp_search: "create-new-feature|setup-plan"
mcp_search: "ALL_AGENTS" lang:bash
mcp_search: "generate_commands"
```

### 测试
```bash
mcp_search: "REQUIRED_AGENTS" lang:python
mcp_search: "test_.*init.*agents"
mcp_search: "assert.*path" path:tests/
```

---

## 使用示例

### 例1: 添加新 Agent 支持

❌ **错误方式：**
```
假设 claude 的结构，直接添加到 AGENT_CONFIG
```

✅ **正确方式：**
```
1. mcp_search: "AGENT_CONFIG" → 找到配置
2. mcp_search: "claude|gemini|copilot" → 学习模式
3. mcp_fetch_content: "src/specify_cli/__init__.py" → 完整审查
4. mcp_search: "requires_cli|commands_subdir" → 理解所有字段
5. mcp_search: "test_.*init_creates" → 找相关测试
6. mcp_search: "update-agent-context" → 检查脚本要求
→ 现在安全地添加 agent
```

### 例2: 修改命令模板（speckit.specify）

❌ **错误方式：**
```
根据记忆编辑 templates/commands/specify.md
希望它与测试一致
```

✅ **正确方式：**
```
1. mcp_search: "speckit.specify" lang:markdown → 找命令
2. mcp_fetch_content: "templates/commands/specify.md" → 完整审查
3. mcp_search: "NEEDS CLARIFICATION|ERROR" → 理解验证器
4. mcp_fetch_content: "templates/spec-template.md" → 输出模板
5. mcp_search: "test_.*specify" → 找测试
6. mcp_fetch_content: "tests/test_speckit_commands.py" → 测试预期
→ 现在修改命令
```

---

## 强制执行检查清单

**在写任何代码前，确认以下各项：**

- [ ] 通过 `mcp_search` 找到了要修改的符号？
- [ ] 通过 `mcp_fetch_content` 读了实际代码？
- [ ] 通过 `mcp_search` 找了所有引用？
- [ ] 找到并理解了相关测试？
- [ ] 了解了已建立的模式？

**如果任何一项为否 → 先运行 MCP 搜索再继续**

---

## 禁止清单

❌ **不要做这些事：**

1. 跳过 MCP 搜索以"节省时间"
2. 依靠上下文/记忆而不是实际代码
3. 假设目录结构或命名约定
4. 在不验证的情况下复制粘贴模式
5. 在不理解影响的情况下进行"快速"更改
6. 修改文件但不搜索测试

---

## MCP 工具语法速查

### 搜索
```bash
mcp_search: "PATTERN" [lang:LANGUAGE] [path:FILTER]
```

**示例**:
```bash
mcp_search: "AGENT_CONFIG" lang:python
mcp_search: "speckit\." lang:markdown path:templates/commands/
mcp_search: "def check_tool"
mcp_search: "{SYMBOL}" (不加 lang 过滤器 = 所有文件)
```

### 获取内容
```bash
mcp_fetch_content: repo:"github.com/bigsmartben/bb-spec-kit" path:"RELATIVE/PATH"
```

**示例**:
```bash
mcp_fetch_content: repo:"github.com/bigsmartben/bb-spec-kit" path:"src/"
mcp_fetch_content: repo:"github.com/bigsmartben/bb-spec-kit" path:"templates/commands/specify.md"
mcp_fetch_content: repo:"github.com/bigsmartben/bb-spec-kit" path:".github/workflows/scripts/"
```

---

## 故障恢复

**如果你意识到跳过了 MCP 搜索：**

1. ⏸️ 立即停止
2. 🔍 运行相应的 `mcp_search` 或 `mcp_fetch_content`
3. 📋 审查结果
4. 🔄 调整方法
5. ✅ 继续，现在有了完整理解

---

## 快速参考表

| 需求 | MCP 查询 |
|------|---------|
| 找 Agent 配置 | `mcp_search: "AGENT_CONFIG"` |
| 找 speckit.* 命令 | `mcp_search: "speckit\." lang:markdown` |
| 找脚本 | `mcp_search: "create-new-feature\|setup-plan"` |
| 找测试 | `mcp_search: "test_.*" lang:python` |
| 找所有引用 | `mcp_search: "SYMBOL"` (无 lang 过滤) |
| 读文件 | `mcp_fetch_content: "path:to/file"` |

---

## 版本信息

- **创建日期**: 2026-03-05
- **执行级别**: 🔴 **强制**
- **适用范围**: 所有 spec-kit AI 辅助编码
- **生效指令文件**:
  - `.github/copilot-instructions.md` (GitHub Copilot)
  - `.claude/instructions.md` (Claude Code)
  - `.cursor/instructions.md` (Cursor IDE)
  - `.agents/mcp-instructions.md` (通用)

---

## 更多帮助

**在提问之前，先试试 MCP 搜索。**

99% 的 spec-kit 问题都可以通过以下方式回答：
```
1. mcp_search: "你的问题关键词"
2. mcp_fetch_content: "相关路径"
3. mcp_search: "相关模式"
```

*本指南确保 spec-kit 保持代码质量、一致性和可靠性。*
