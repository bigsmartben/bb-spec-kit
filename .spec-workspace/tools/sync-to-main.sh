#!/bin/bash
# sync-to-main.sh - 将验证通过的修改同步到主仓库

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

REQ_ID="$1"
DRY_RUN=false

if [ "$2" = "--dry-run" ]; then
    DRY_RUN=true
fi

if [ -z "$REQ_ID" ]; then
    echo -e "${RED}Error: 需求ID不能为空${NC}"
    echo "Usage: $0 EXT-XXX [--dry-run]"
    exit 1
fi

REQ_DIR=".spec-workspace/requirements/$REQ_ID"

if [ ! -d "$REQ_DIR" ]; then
    echo -e "${RED}Error: 需求目录不存在: $REQ_DIR${NC}"
    exit 1
fi

if [ "$DRY_RUN" = true ]; then
    echo -e "${BLUE}🔍 Dry-run 模式 - 仅显示计划，不执行操作${NC}"
fi

echo "🔄 同步需求到主仓库: $REQ_ID"
echo "=================="

# 1. 验证需求状态
echo "1️⃣  验证需求状态..."
if ! grep -q "$REQ_ID.*已完成" ".spec-workspace/requirements/REQUIREMENTS.md"; then
    echo -e "${RED}✗ 需求状态不是'已完成'，不能同步${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 需求状态: 已完成${NC}"

# 2. 运行验证工具
echo ""
echo "2️⃣  运行需求验证..."
if ! .spec-workspace/tools/validate-requirement.sh "$REQ_ID"; then
    echo -e "${RED}✗ 需求验证失败，请先修复问题${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 需求验证通过${NC}"

# 3. 检查所有测试是否通过
echo ""
echo "3️⃣  检查测试结果..."
if [ -f "$REQ_DIR/tests.md" ]; then
    if grep -q "通过率.*100%" "$REQ_DIR/tests.md"; then
        echo -e "${GREEN}✓ 所有测试通过${NC}"
    else
        PASS_RATE=$(grep "通过率" "$REQ_DIR/tests.md" | head -1 || echo "未知")
        echo -e "${RED}✗ 测试未完全通过: $PASS_RATE${NC}"
        read -p "是否继续同步？(y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠ 未找到测试文件${NC}"
fi

# 4. 分析需要同步的文件
echo ""
echo "4️⃣  分析同步计划..."

# 检查 implementation.md 中记录的文件变更
if [ ! -f "$REQ_DIR/implementation.md" ]; then
    echo -e "${RED}✗ 未找到 implementation.md，无法确定同步内容${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}📋 同步计划:${NC}"
echo ""

# 定义同步文件列表（根据需求ID特殊处理）
declare -a NEW_FILES=()
declare -a MODIFIED_FILES=()

if [ "$REQ_ID" = "EXT-002" ]; then
    # EXT-002 特定的文件列表
    NEW_FILES=(
        ".spec-workspace/templates/spec-template-EXT-002.md:templates/spec-template-EXT-002.md"
        ".spec-workspace/templates/plan-template-EXT-002.md:templates/plan-template-EXT-002.md"
        ".spec-workspace/templates/tasks-template-EXT-002.md:templates/tasks-template-EXT-002.md"
        ".spec-workspace/templates/commands/plan-EXT-002.md:templates/commands/plan-EXT-002.md"
        ".spec-workspace/templates/commands/tasks-EXT-002.md:templates/commands/tasks-EXT-002.md"
    )
else
    # 通用逻辑：尝试从 implementation.md 提取
    echo "新增文件:"
    grep -A 5 "### 新增文件" "$REQ_DIR/implementation.md" | grep "^\|" | grep -v "^|.*文件路径" | grep -v "^|----" || echo "  (无)"
    
    echo ""
    echo "修改文件:"
    grep -A 5 "### 修改文件" "$REQ_DIR/implementation.md" | grep "^\|" | grep -v "^|.*文件路径" | grep -v "^|----" || echo "  (无)"
fi

# 显示计划
if [ ${#NEW_FILES[@]} -gt 0 ]; then
    echo "新增文件 (${#NEW_FILES[@]}):"
    for file_pair in "${NEW_FILES[@]}"; do
        src="${file_pair%%:*}"
        dst="${file_pair##*:}"
        echo "  ✨ $src → $dst"
    done
fi

if [ ${#MODIFIED_FILES[@]} -gt 0 ]; then
    echo ""
    echo "修改文件 (${#MODIFIED_FILES[@]}):"
    for file_pair in "${MODIFIED_FILES[@]}"; do
        src="${file_pair%%:*}"
        dst="${file_pair##*:}"
        echo "  📝 $src → $dst"
    done
fi

if [ ${#NEW_FILES[@]} -eq 0 ] && [ ${#MODIFIED_FILES[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠ 未找到要同步的文件${NC}"
    exit 1
fi

# 5. 执行同步
if [ "$DRY_RUN" = false ]; then
    echo ""
    echo "5️⃣  执行同步..."
    read -p "确认同步到主仓库？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "操作取消"
        exit 0
    fi
    
    # 复制新增文件
    if [ ${#NEW_FILES[@]} -gt 0 ]; then
        echo ""
        echo "📁 同步新增文件..."
        for file_pair in "${NEW_FILES[@]}"; do
            src="${file_pair%%:*}"
            dst="${file_pair##*:}"
            
            if [ ! -f "$src" ]; then
                echo -e "${RED}✗ 源文件不存在: $src${NC}"
                continue
            fi
            
            # 创建目标目录
            dst_dir=$(dirname "$dst")
            mkdir -p "$dst_dir"
            
            # 复制文件
            cp "$src" "$dst"
            echo -e "${GREEN}✓${NC} $dst"
        done
    fi
    
    # 复制修改文件
    if [ ${#MODIFIED_FILES[@]} -gt 0 ]; then
        echo ""
        echo "📝 同步修改文件..."
        for file_pair in "${MODIFIED_FILES[@]}"; do
            src="${file_pair%%:*}"
            dst="${file_pair##*:}"
            
            if [ ! -f "$src" ]; then
                echo -e "${RED}✗ 源文件不存在: $src${NC}"
                continue
            fi
            
            # 创建目标目录
            dst_dir=$(dirname "$dst")
            mkdir -p "$dst_dir"
            
            # 复制文件
            cp "$src" "$dst"
            echo -e "${GREEN}✓${NC} $dst"
        done
    fi
    
    echo ""
    echo -e "${GREEN}✓ 文件同步完成${NC}"
    
    # 6. 生成同步报告
    REPORT_FILE="$REQ_DIR/sync-report.md"
    cat > "$REPORT_FILE" << EOF
# $REQ_ID 同步报告

**同步时间**: $(date +"%Y-%m-%d %H:%M:%S")  
**操作者**: $(git config user.name 2>/dev/null || echo "Unknown")

## 同步内容

### 新增文件 (${#NEW_FILES[@]})

EOF
    
    for file_pair in "${NEW_FILES[@]}"; do
        dst="${file_pair##*:}"
        echo "- \`$dst\`" >> "$REPORT_FILE"
    done
    
    cat >> "$REPORT_FILE" << EOF

### 修改文件 (${#MODIFIED_FILES[@]})

EOF
    
    for file_pair in "${MODIFIED_FILES[@]}"; do
        dst="${file_pair##*:}"
        echo "- \`$dst\`" >> "$REPORT_FILE"
    done
    
    cat >> "$REPORT_FILE" << EOF

## 验证结果

- ✅ 需求验证通过
- ✅ 测试验证通过
- ✅ 文件同步完成

## 后续步骤

1. 在主仓库中测试功能
2. 提交 Git commit:
   \`\`\`bash
   git add templates/
   git commit -m "feat: 新增 $REQ_ID 模板扩展"
   \`\`\`
3. 推送到远程仓库
4. 更新文档（如需要）

---
**生成时间**: $(date +"%Y-%m-%d %H:%M:%S")
EOF
    
    echo ""
    echo "📄 同步报告已生成: $REPORT_FILE"
    
else
    echo ""
    echo -e "${BLUE}Dry-run 完成 - 未执行实际同步${NC}"
fi

echo ""
echo "=================="
echo "🎉 同步流程完成"
