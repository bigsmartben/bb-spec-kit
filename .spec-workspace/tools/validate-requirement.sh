#!/bin/bash
# validate-requirement.sh - 验证需求文档的完整性和格式正确性

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取需求ID
REQ_ID="$1"

if [ -z "$REQ_ID" ]; then
    echo -e "${RED}Error: 需求ID不能为空${NC}"
    echo "Usage: $0 EXT-XXX"
    exit 1
fi

REQ_DIR=".spec-workspace/requirements/$REQ_ID"

echo "🔍 验证需求: $REQ_ID"
echo "=================="

# 检查需求目录是否存在
if [ ! -d "$REQ_DIR" ]; then
    echo -e "${RED}✗ 需求目录不存在: $REQ_DIR${NC}"
    exit 1
fi

ERRORS=0
WARNINGS=0

# 1. 检查 requirement.md
echo -n "📄 检查 requirement.md... "
if [ -f "$REQ_DIR/requirement.md" ]; then
    # 检查必需章节
    REQUIRED_SECTIONS=(
        "需求概述"
        "用户场景"
        "功能需求"
        "验收标准"
    )
    
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! grep -q "$section" "$REQ_DIR/requirement.md"; then
            echo -e "${YELLOW}⚠ 缺少章节: $section${NC}"
            ((WARNINGS++))
        fi
    done
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ 文件不存在${NC}"
    ((ERRORS++))
fi

# 2. 检查 design.md (如果状态是设计中或之后)
echo -n "🏗️  检查 design.md... "
if grep -q "状态.*设计中\|开发中\|测试中\|已完成" ".spec-workspace/requirements/REQUIREMENTS.md" 2>/dev/null; then
    if [ -f "$REQ_DIR/design.md" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠ 建议创建设计文档${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "⊘ 跳过 (需求未进入设计阶段)"
fi

# 3. 检查 implementation.md (如果状态是开发中或之后)
echo -n "💻 检查 implementation.md... "
if grep -q "状态.*开发中\|测试中\|已完成" ".spec-workspace/requirements/REQUIREMENTS.md" 2>/dev/null; then
    if [ -f "$REQ_DIR/implementation.md" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠ 建议创建实现记录${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "⊘ 跳过 (需求未进入开发阶段)"
fi

# 4. 检查 tests.md (如果状态是测试中或之后)
echo -n "🧪 检查 tests.md... "
if grep -q "状态.*测试中\|已完成" ".spec-workspace/requirements/REQUIREMENTS.md" 2>/dev/null; then
    if [ -f "$REQ_DIR/tests.md" ]; then
        # 检查测试用例数量
        TEST_COUNT=$(grep -c "^### TC-" "$REQ_DIR/tests.md" || echo "0")
        if [ "$TEST_COUNT" -gt 0 ]; then
            echo -e "${GREEN}✓ (包含 $TEST_COUNT 个测试用例)${NC}"
        else
            echo -e "${YELLOW}⚠ 没有找到测试用例${NC}"
            ((WARNINGS++))
        fi
    else
        echo -e "${RED}✗ 文件不存在（测试阶段必需）${NC}"
        ((ERRORS++))
    fi
else
    echo -e "⊘ 跳过 (需求未进入测试阶段)"
fi

# 5. 检查 REQUIREMENTS.md 中的条目
echo -n "📋 检查 REQUIREMENTS.md 条目... "
if grep -q "^### $REQ_ID:" ".spec-workspace/requirements/REQUIREMENTS.md"; then
    echo -e "${GREEN}✓${NC}"
    
    # 检查必填字段
    echo "   检查必填字段:"
    FIELDS=("需求ID" "需求标题" "扩展类型" "优先级" "状态" "验收标准")
    for field in "${FIELDS[@]}"; do
        if grep -A 20 "^### $REQ_ID:" ".spec-workspace/requirements/REQUIREMENTS.md" | grep -q "$field"; then
            echo -e "   ${GREEN}✓${NC} $field"
        else
            echo -e "   ${RED}✗${NC} $field 缺失"
            ((ERRORS++))
        fi
    done
else
    echo -e "${RED}✗ 未在 REQUIREMENTS.md 中找到${NC}"
    ((ERRORS++))
fi

# 6. 检查文件格式
echo "📝 检查文件格式:"
for file in "$REQ_DIR"/*.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        # 检查是否有 BOM
        if file "$file" | grep -q "with BOM"; then
            echo -e "   ${YELLOW}⚠${NC} $filename: 包含 BOM，建议移除"
            ((WARNINGS++))
        fi
        
        # 检查行尾符
        if file "$file" | grep -q "CRLF"; then
            echo -e "   ${YELLOW}⚠${NC} $filename: 使用 CRLF 行尾，建议使用 LF"
            ((WARNINGS++))
        fi
    fi
done

# 7. 汇总
echo ""
echo "=================="
echo "验证总结:"
echo -e "错误: ${RED}$ERRORS${NC}"
echo -e "警告: ${YELLOW}$WARNINGS${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ 验证通过！需求文档完整且格式正确。${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ 验证通过但有警告，建议修复。${NC}"
    exit 0
else
    echo -e "${RED}✗ 验证失败，请修复错误后重试。${NC}"
    exit 1
fi
