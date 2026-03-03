# Spec Kit 工作区变更日志

> 📝 记录工作区的所有重要变更

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### 计划添加
- [ ] PowerShell 版本的工具脚本
- [ ] 自动化的同步工具
- [ ] 需求模板生成器
- [ ] Git hooks 集成

---

## [1.0.0] - 2026-03-03

### 添加

#### 核心结构
- 创建 `.spec-workspace/` 独立开发工作区
- 添加 `requirements/` 需求管理目录
- 添加 `templates/` 实验性模板目录
- 添加 `sandbox/` 测试沙盒目录
- 添加 `docs/` 工作区文档目录
- 添加 `tools/` 辅助工具目录

#### 需求管理
- 添加 `REQUIREMENTS.md` 集中式需求管理表
- 创建需求模板系统（`requirements/_templates/`）:
  - `requirement-template.md` - 需求详细描述模板
  - `design-template.md` - 技术设计文档模板
  - `implementation-template.md` - 实现记录模板
  - `tests-template.md` - 测试文档模板
- 添加 EXT-001 示例需求（PRD 转 Spec）

#### 文档
- 添加 `README.md` 工作区说明文档
- 添加 `docs/WORKFLOW.md` 详细开发工作流文档
- 添加 `docs/ARCHITECTURE.md` 架构决策记录(ADR)
- 添加 `docs/CHANGELOG.md` 本文件

#### 工具脚本
- 添加 `tools/validate-requirement.sh` 需求验证工具
- 添加 `tools/generate-test.sh` 测试用例生成工具
- 添加 `tools/sync-to-main.sh` 主仓库同步工具

#### 配置
- 添加 `.gitignore` 工作区 Git 配置
- 定义文件提交和忽略规则

### 架构决策
- [ADR-001] 创建独立的开发工作区
- [ADR-002] 使用 Markdown 作为主要文档格式
- [ADR-003] 按需求ID组织文件结构
- [ADR-004] 工具脚本使用 Bash
- [ADR-005] 状态驱动的工作流
- [ADR-006] 集中式需求管理表

---

## 版本说明

### [1.0.0] - 初始发布

这是 Spec Kit 工作区的首个正式版本，提供：

✅ **完整的需求管理流程**
- 从提交到完成的全生命周期管理
- 规范化的文档模板
- 清晰的状态转换流程

✅ **隔离的开发环境**
- 不侵入主仓库
- 实验性修改受控
- 验证后同步机制

✅ **自动化工具支持**
- 需求验证工具
- 测试生成工具
- 同步辅助工具

✅ **详尽的文档**
- 工作区说明
- 开发工作流
- 架构决策记录

---

## 术语说明

### 变更类型

- **添加 (Added)**: 新功能
- **变更 (Changed)**: 已有功能的变更
- **废弃 (Deprecated)**: 即将移除的功能
- **移除 (Removed)**: 已移除的功能
- **修复 (Fixed)**: 任何 bug 修复
- **安全 (Security)**: 安全相关的修复或改进

### 版本号规则

给定版本号 MAJOR.MINOR.PATCH，递增规则如下：

- **MAJOR**: 不兼容的 API 修改
- **MINOR**: 向下兼容的功能性新增
- **PATCH**: 向下兼容的问题修正

---

## 贡献指南

### 如何更新此文件

1. **添加变更**到 `[Unreleased]` 部分
2. **选择正确的类别**（添加/变更/修复等）
3. **使用现在时**描述变更（如"添加功能"而非"添加了功能"）
4. **包含需求ID**（如果适用）：`[EXT-XXX] 描述`
5. **发布新版本时**，移动 `[Unreleased]` 内容到新版本部分

### 示例条目

```markdown
## [Unreleased]

### 添加
- [EXT-003] 添加 API 专用规格模板
- [EXT-004] 支持多语言文档生成

### 变更
- [EXT-001] 改进 PRD 章节映射逻辑

### 修复
- [EXT-002] 修复文件路径检测bug
```

---

## 里程碑

### 🎯 1.0 - 基础设施 ✅
发布日期: 2026-03-03
- 完成工作区基础结构
- 建立需求管理流程
- 提供基础工具支持

### 🎯 1.1 - 自动化增强（规划中）
预计: 2026-Q2
- 增强自动化工具
- 添加 PowerShell 支持
- 集成 Git hooks

### 🎯 2.0 - 高级功能（未来）
预计: 2026-Q3
- 需求依赖管理
- 自动化测试集成
- 可视化看板

---

**维护者**: Spec Kit 开发团队  
**最后更新**: 2026-03-03  
**下次审查**: 每月第一周

---

[Unreleased]: https://github.com/github/spec-kit/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/github/spec-kit/releases/tag/v1.0.0
