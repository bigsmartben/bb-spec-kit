# Spec Kit 开发工作区

> 🎯 **目的**: 隔离的扩展开发环境，不侵入主仓库核心文件

## 📁 目录结构

```
.spec-workspace/
├── README.md                    # 本文件 - 工作区说明
├── requirements/                # 需求管理
│   ├── REQUIREMENTS.md         # 需求管理主表格
│   ├── EXT-001/                # 按需求ID组织
│   │   ├── requirement.md      # 需求详细描述
│   │   ├── design.md           # 技术设计文档
│   │   ├── implementation.md   # 实现记录
│   │   └── tests.md            # 测试用例和结果
│   └── EXT-002/
│       └── ...
├── templates/                   # 工作区模板（实验性修改）
│   ├── commands/               # 实验性命令模板
│   └── spec-template-*.md      # 实验性 spec 模板
├── sandbox/                     # 临时测试和实验
│   ├── test-prds/              # 测试用的 PRD 文档
│   ├── test-outputs/           # 生成的测试输出
│   └── scratch/                # 临时文件
├── docs/                        # 开发文档
│   ├── WORKFLOW.md             # 开发工作流程
│   ├── ARCHITECTURE.md         # 架构决策记录
│   └── CHANGELOG.md            # 变更日志
└── tools/                       # 辅助工具脚本
    ├── validate-requirement.sh # 验证需求格式
    ├── generate-test.sh        # 生成测试用例
    └── sync-to-main.sh         # 同步到主仓库
```

## 🚀 快速开始

### 1. 提交新需求

```bash
# 编辑需求管理表
vim .spec-workspace/requirements/REQUIREMENTS.md

# 为新需求创建目录
mkdir -p .spec-workspace/requirements/EXT-003
cd .spec-workspace/requirements/EXT-003

# 从模板创建需求文档
cp ../../_templates/requirement-template.md requirement.md
vim requirement.md
```

### 2. 开发和测试

```bash
# 在工作区创建实验性修改
cp templates/commands/specify.md .spec-workspace/templates/commands/specify-enhanced.md

# 进行修改和测试
vim .spec-workspace/templates/commands/specify-enhanced.md

# 在 sandbox 中测试
cd .spec-workspace/sandbox
```

### 3. 验证和同步

```bash
# 验证需求完整性
.spec-workspace/tools/validate-requirement.sh EXT-003

# 验证通过后，同步到主仓库
.spec-workspace/tools/sync-to-main.sh EXT-003
```

## 📋 工作流程

### 阶段 1: 需求定义
1. 在 `requirements/REQUIREMENTS.md` 中填写需求
2. 创建需求专属目录 `requirements/EXT-XXX/`
3. 填写详细的 `requirement.md`
4. 状态: `待评审`

### 阶段 2: 设计
1. 创建 `design.md` 说明技术方案
2. 在 `templates/` 中创建实验性模板
3. 状态: `设计中`

### 阶段 3: 实现
1. 在工作区中修改和测试
2. 记录实现过程到 `implementation.md`
3. 状态: `开发中`

### 阶段 4: 测试
1. 在 `sandbox/` 中创建测试场景
2. 执行测试并记录到 `tests.md`
3. 状态: `测试中`

### 阶段 5: 同步
1. 验证所有测试通过
2. 使用 `sync-to-main.sh` 同步到主仓库
3. 更新状态为 `已完成`
4. 提交 Git commit

## 🔒 隔离原则

### ✅ 工作区内操作（安全）
- 修改 `.spec-workspace/` 下的任何文件
- 创建实验性模板和命令
- 运行测试和验证

### ❌ 禁止直接操作（风险）
- **不要**直接修改 `templates/` 目录
- **不要**直接修改 `src/` 目录
- **不要**直接修改 `.claude/` 等 agent 目录

### 🔄 同步规则
只有通过 `sync-to-main.sh` 验证后才能同步到主仓库：
- ✅ 需求已完成
- ✅ 测试全部通过
- ✅ 文档齐全
- ✅ 符合仓库规范

## 📖 相关文档

- [需求管理表](./requirements/REQUIREMENTS.md) - 所有需求的状态追踪
- [开发工作流](./docs/WORKFLOW.md) - 详细的开发流程
- [架构决策](./docs/ARCHITECTURE.md) - 技术决策记录
- [变更日志](./docs/CHANGELOG.md) - 所有变更的历史记录

## 🎯 设计目标

1. **隔离性**: 工作区与主仓库独立，避免污染
2. **可追溯**: 每个需求都有完整的开发记录
3. **可重复**: 清晰的流程确保团队协作
4. **可验证**: 所有修改经过验证才能同步
5. **长期维护**: 文档和结构支持持续迭代

## 🛡️ Git 集成

工作区有独立的 `.gitignore` 配置：

```gitignore
# 保留在 Git 中
requirements/
docs/
tools/
README.md

# 不提交临时文件
sandbox/scratch/
sandbox/test-outputs/*.md
*.tmp
*.bak

# 根据需要提交测试文件
# sandbox/test-prds/ 可以提交作为测试数据
```

## 💡 最佳实践

### 命名规范
- 需求ID: `EXT-XXX` (从 001 开始)
- 分支命名: `feature/ext-xxx-brief-description`
- Commit 消息: `[EXT-XXX] Brief description`

### 文档规范
- 每个需求必须有完整的 requirement.md
- 技术决策必须记录在 design.md
- 测试结果必须记录在 tests.md

### 代码规范
- 遵循主仓库的代码风格
- 模板文件使用 Markdown 格式
- 命令文件遵循 YAML frontmatter 规范

## 🔧 工具说明

### validate-requirement.sh
验证需求文档的完整性和格式正确性

```bash
Usage: ./tools/validate-requirement.sh EXT-XXX
```

### generate-test.sh
从需求自动生成测试用例框架

```bash
Usage: ./tools/generate-test.sh EXT-XXX
```

### sync-to-main.sh
将验证通过的修改同步到主仓库

```bash
Usage: ./tools/sync-to-main.sh EXT-XXX [--dry-run]
```

---

**维护者**: Spec Kit 开发团队  
**最后更新**: 2026-03-03  
**版本**: 1.0.0
