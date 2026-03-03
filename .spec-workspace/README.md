# Spec Kit 需求工作区（Backlog）

> 🎯 **目的**：只保留“需求管理”。其余交付活动（设计/实现/测试/发布）统一在**仓库根目录**基于 `main`/`master` 创建分支完成。

## 📁 目录结构（最小集）

```
.spec-workspace/
├── README.md
├── GETTING-STARTED.md
├── requirements/
│   ├── REQUIREMENTS.md              # 需求总表（状态追踪）
│   ├── _templates/
│   │   └── requirement-template.md  # 需求模板
│   └── EXT-XXX/
│       └── requirement.md           # 需求详情（必需）
└── tools/
    └── validate-requirement.sh      # 需求管理校验（可选）
```

## 🚀 快速开始

### 1) 新建需求（只在 `.spec-workspace` 修改文档）

```bash
vim .spec-workspace/requirements/REQUIREMENTS.md

mkdir -p .spec-workspace/requirements/EXT-003
cp .spec-workspace/requirements/_templates/requirement-template.md \
  .spec-workspace/requirements/EXT-003/requirement.md
vim .spec-workspace/requirements/EXT-003/requirement.md
```

### 2) 校验需求（可选）

```bash
.spec-workspace/tools/validate-requirement.sh EXT-003
```

### 3) 开始交付（在仓库根目录开分支）

```bash
git switch -c feature/ext-003-brief-description

# 直接修改主工作区文件：templates/、src/、docs/…
git commit -am "[EXT-003] <your change summary>"

# 提交 PR → Review → Merge
```

### 4) 关闭需求

- PR 合并后，将 `.spec-workspace/requirements/REQUIREMENTS.md` 中对应条目的状态更新为 `已完成`
- 如有需要，在条目中补充 PR/commit 链接（便于追溯）

## 🔒 交付隔离（用 Git 分支实现）

- 交付改动一律通过 **分支 + PR** 完成；避免在 `main`/`master` 直接开发
- 提交信息/PR 标题建议包含 `EXT-XXX`，实现“需求 ↔ 变更”可追溯

## 📖 相关文档

- [需求管理表](./requirements/REQUIREMENTS.md)
- [交付工作流](./docs/WORKFLOW.md)

---

**维护者**: Spec Kit 开发团队  
**最后更新**: 2026-03-03  
**版本**: 2.0.0
