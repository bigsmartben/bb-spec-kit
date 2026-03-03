---
name: auto-test
description: 全自动测试-修复-循环技能。覆盖 uv 安装检测、specify init (codex/claude/opencode/roo 四个 Agent 必须通过)、prd2spec 及所有 speckit 阶段指令的完整测试套件。发现失败后自动分析、定位根因、修改源码或测试，然后重新运行，直到全部通过（最多 6 轮迭代）。全程本地静默执行，无需用户确认。
compatibility: 需要 spec-kit 仓库、已激活 Python 虚拟环境（tmp-env）
metadata:
  author: github-spec-kit
  source: .agents/skills/auto-test/SKILL.md
---

# Spec-Kit 全自动测试-修复-循环技能

## 目标

在不打扰用户的前提下，**自主完成**以下闭环：

1. 确保测试依赖已安装
2. 执行完整测试套件
3. 若有失败 → 精准定位根因 → 修改最少文件集修复 → 重新执行
4. 重复直到全绿或超过最大迭代次数（6 轮）

---

## 测试范围（必须全部通过）

| 模块 | 文件 | 覆盖重点 |
|------|------|----------|
| uv 环境 | `tests/test_uv_env.py` | uv 可用性、版本、`uv run python` 正常 |
| Init Agent | `tests/test_init_agents.py` | codex / claude / opencode / roo 四个 Agent 的 AGENT_CONFIG、目录映射、mocked init 流程 |
| Speckit 指令 | `tests/test_speckit_commands.py` | 所有 `templates/commands/*.md` 存在性、frontmatter 合法性、prd2spec 关键内容、必填字段 |
| AI Skills | `tests/test_ai_skills.py` | （已有测试，保持通过） |
| Extensions | `tests/test_extensions.py` | （已有测试，保持通过） |
| Cursor Frontmatter | `tests/test_cursor_frontmatter.py` | （已有测试，保持通过） |

---

## 自动执行工作流

### Phase 0 — 环境准备

```bash
# 激活虚拟环境（已在 tmp-env）
source /home/ben/project/spec-kit/tmp-env/bin/activate

# 安装测试依赖（幂等）
pip install -e ".[test]" -q
```

若 `pip install` 报错，检查 `pyproject.toml` 的 `[project.optional-dependencies] test` 段，确认 `pytest` 和 `pytest-cov` 定义正确后修复。

---

### Phase 1 — 执行完整测试套件

```bash
cd /home/ben/project/spec-kit
python -m pytest tests/ \
  -v \
  --tb=short \
  --no-header \
  -q \
  2>&1 | tee /tmp/spec-kit-test-run.log
```

**退出码规则**：
- `0` → 全绿，工作结束  
- 非 `0` → 进入 Phase 2

---

### Phase 2 — 失败解析与根因定位

读取 `/tmp/spec-kit-test-run.log`，逐条分析失败条目：

```
FAILED tests/test_foo.py::TestBar::test_baz - AssertionError: ...
```

**根因分类**：

| 类型 | 症状 | 修复路径 |
|------|------|----------|
| A — AGENT_CONFIG 缺失字段 | `KeyError` 或 `AssertionError` on agent key | `src/specify_cli/__init__.py` → 补全 AGENT_CONFIG 条目 |
| B — 命令模板缺失 | `FileNotFoundError` 或 `assert exists()` 失败 | `templates/commands/<name>.md` → 创建或补全 |
| C — frontmatter 格式错误 | `yaml.YAMLError` 或字段断言失败 | 对应 `templates/commands/<name>.md` → 修复 YAML 头 |
| D — prd2spec 内容缺失 | `assert "..." in content` 失败 | `templates/commands/prd2spec.md` → 补充关键内容 |
| E — uv 不可用 | `FileNotFoundError: uv` | 检查 PATH，若确实未安装则 `curl -LsSf https://astral.sh/uv/install.sh | sh` |
| F — 测试逻辑错误 | 测试本身断言写错 | 修改对应测试文件 |
| G — import 错误 | `ImportError` / `ModuleNotFoundError` | 检查 `src/specify_cli/__init__.py` 暴露的公共符号 |

---

### Phase 3 — 精准修复

**约束规则（严格遵守）**：

1. **最小变更原则**：只修改根因对应的文件，不扩散
2. **保持幂等**：修复后的文件应能被多次测试而结果一致
3. **不破坏已有测试**：每次修复前先确认修改不会让已过测试失败
4. **同步性**：若修改 bash 脚本，对应 PowerShell 脚本同步跟进

修复完成后，**立即**跳转回 Phase 1 重新运行全套测试。

---

### Phase 4 — 终止条件

```
if ALL tests PASS:
    print("✅ 全部测试通过")
    DONE

if iteration >= 6:
    print("❌ 超过最大迭代次数（6轮），输出失败摘要")
    DONE（向用户报告剩余问题）
```

---

## 关键文件所有权

| 测试失败点 | 可修改文件 | 禁止触及 |
|-----------|-----------|----------|
| AGENT_CONFIG 断言 | `src/specify_cli/__init__.py` | 测试文件（除非测试逻辑本身有误） |
| 命令模板断言 | `templates/commands/<name>.md` | `src/` 下非 `__init__.py` 的文件 |
| prd2spec 内容断言 | `templates/commands/prd2spec.md` | 其他命令文件 |
| uv 相关断言 | `tests/test_uv_env.py` 测试逻辑 | 系统环境（除非确实需要安装） |
| init agent 断言 | `tests/test_init_agents.py` 或 `src/specify_cli/__init__.py` | extensions.py |
| Skills 断言 | `src/specify_cli/__init__.py` (install_ai_skills) | 其他模块 |

---

## 快速启动命令（一键运行本 Skill）

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO=/home/ben/project/spec-kit
LOG=/tmp/spec-kit-test-run.log
MAX_ITER=6
ITER=0

cd "$REPO"
source tmp-env/bin/activate
pip install -e ".[test]" -q

while true; do
  ITER=$((ITER + 1))
  echo "=== Iteration $ITER / $MAX_ITER ==="

  if python -m pytest tests/ -v --tb=short -q 2>&1 | tee "$LOG"; then
    echo "✅ All tests passed on iteration $ITER"
    exit 0
  fi

  if [ "$ITER" -ge "$MAX_ITER" ]; then
    echo "❌ Max iterations reached. See $LOG for details."
    exit 1
  fi

  echo "--- Failures detected, triggering AI fix loop ---"
  # AI agent reads $LOG and applies fixes here, then loop continues
done
```

---

## 已知环境限制（不计入修复范围）

以下失败是 **CI 沙箱环境特有限制**，在本地开发环境下不会出现，AI 修复循环应当识别并跳过它们：

| 测试类 | 失败原因 | 处理方式 |
|--------|---------|---------|
| `TestCursorFrontmatterIntegration`（4条） | `/tmp` 只读：`mktemp: failed to create file: Read-only file system` | 沙箱环境跳过；本地环境应通过 |
| `TestUvPackageManagement`（2条） | `uv cache is read-only` | 自动 skip（测试已处理） |

**判断规则**：失败日志包含 `Read-only file system` → 视为环境限制，**不修改代码**，直接跳过。

---



```bash
# 只运行某个模块
python -m pytest tests/test_init_agents.py -v --tb=long

# 只运行四个必须通过的 Agent 测试
python -m pytest tests/test_init_agents.py -k "codex or claude or opencode or roo" -v

# 查看最近失败摘要
python -m pytest tests/ --tb=no -q 2>&1 | grep "FAILED"

# 检查 AGENT_CONFIG 中目标 agent 的配置
python -c "from specify_cli import AGENT_CONFIG; \
  for k in ['codex','claude','opencode','roo']: \
    print(k, AGENT_CONFIG[k])"
```
