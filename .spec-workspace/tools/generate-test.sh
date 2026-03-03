#!/bin/bash
# generate-test.sh - 从需求自动生成测试用例框架

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

REQ_ID="$1"

if [ -z "$REQ_ID" ]; then
    echo -e "${RED}Error: 需求ID不能为空${NC}"
    echo "Usage: $0 EXT-XXX"
    exit 1
fi

REQ_DIR=".spec-workspace/requirements/$REQ_ID"
REQ_FILE="$REQ_DIR/requirement.md"
TEST_FILE="$REQ_DIR/tests.md"

if [ ! -f "$REQ_FILE" ]; then
    echo -e "${RED}Error: 需求文件不存在: $REQ_FILE${NC}"
    exit 1
fi

if [ -f "$TEST_FILE" ]; then
    echo -e "${YELLOW}Warning: 测试文件已存在: $TEST_FILE${NC}"
    read -p "是否覆盖？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "操作取消"
        exit 0
    fi
fi

echo "🧪 生成测试用例框架: $REQ_ID"
echo "=================="

# 从模板创建测试文件
cp .spec-workspace/requirements/_templates/tests-template.md "$TEST_FILE"

# 提取需求信息
REQ_TITLE=$(grep "需求标题" "$REQ_FILE" | head -1 | sed 's/.*: //' | sed 's/\*\*//g')
REQ_TYPE=$(grep "扩展类型" "$REQ_FILE" | head -1 | sed 's/.*: //' | sed 's/\*\*//g')

# 更新测试文件中的占位符
sed -i.bak "s/EXT-XXX/$REQ_ID/g" "$TEST_FILE"
sed -i.bak "s/YYYY-MM-DD/$(date +%Y-%m-%d)/g" "$TEST_FILE"
rm "$TEST_FILE.bak"

echo -e "${GREEN}✓ 测试框架已生成${NC}"
echo ""
echo "📝 生成的测试文件: $TEST_FILE"
echo ""
echo "下一步:"
echo "1. 编辑 $TEST_FILE"
echo "2. 根据需求填写具体测试用例"
echo "3. 执行测试并记录结果"
echo "4. 更新测试状态和汇总"

# 尝试从需求中提取验收标准生成测试用例提示
echo ""
echo "💡 提示: 从需求中提取的验收标准:"
grep -A 10 "## .*验收标准" "$REQ_FILE" | grep "^-\|^✅" | head -5
