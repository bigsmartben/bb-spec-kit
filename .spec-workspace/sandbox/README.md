# Sandbox 测试沙盒

> 🧪 **目的**: 安全的测试和实验环境

## 📁 目录结构

```
sandbox/
├── README.md              # 本文件
├── test-prds/            # 测试用的 PRD 文档
│   ├── sample-login.md
│   ├── sample-api.md
│   └── edge-cases/       # 边界情况测试
├── test-outputs/         # 生成的测试输出
│   ├── spec-*.md
│   ├── plan-*.md
│   └── tasks-*.md
└── scratch/              # 临时文件和草稿
    └── .gitkeep
```

## 🎯 使用场景

### 1. 功能测试

在 AI 编辑器中测试新命令或增强功能：

```bash
# 1. 准备测试 PRD
cat > sandbox/test-prds/test-case-1.md << 'EOF'
# User Authentication PRD
[PRD 内容...]
EOF

# 2. 在 AI 编辑器中执行命令
> /speckit.specify sandbox/test-prds/test-case-1.md

# 3. 检查生成的输出
cat spec.md  # 或移动到 test-outputs/
```

### 2. 边界测试

测试各种边界情况：

```bash
# 空文件
touch sandbox/test-prds/empty.md

# 超大文件
cat /dev/urandom | base64 | head -c 1M > sandbox/test-prds/large.md

# 特殊字符
echo "# 测试 PRD 📝" > sandbox/test-prds/special-chars.md
```

### 3. 性能测试

测试不同大小文件的处理性能：

```bash
# 生成不同大小的测试文件
for size in 1K 10K 50K 100K; do
    head -c $size /dev/urandom > sandbox/test-prds/test-${size}.md
done

# 记录处理时间
time /speckit.specify sandbox/test-prds/test-50K.md
```

### 4. 集成测试

测试完整的工作流：

```bash
# 1. 生成 spec
> /speckit.specify sandbox/test-prds/sample-login.md
mv spec.md sandbox/test-outputs/spec-login.md

# 2. 生成 plan
> /speckit.plan
mv plan.md sandbox/test-outputs/plan-login.md

# 3. 生成 tasks
> /speckit.tasks
mv tasks.md sandbox/test-outputs/tasks-login.md

# 4. 验证所有文件格式正确
ls -lh sandbox/test-outputs/
```

## 📝 测试 PRD 示例

### sample-login.md - 完整标准 PRD

```markdown
# User Login PRD

## Business Objective
Enable secure user authentication to improve user retention by 25%.

## User Stories
1. As a user, I want to log in with email and password
2. As a user, I want to reset my password if forgotten
3. As a user, I want to stay logged in

## Functional Requirements
1. Support email/password authentication
2. Implement "forgot password" flow
3. Session management with JWT tokens
4. Remember me functionality

## Non-Functional Requirements
1. Login must complete within 2 seconds (p95)
2. Support 10,000 concurrent users
3. 99.9% uptime SLA

## Acceptance Criteria
- [ ] Users can successfully log in with valid credentials
- [ ] Password reset email is sent within 5 seconds
- [ ] Invalid login attempts are logged
- [ ] Session expires after 24 hours of inactivity
```

### sample-api.md - API 功能 PRD

```markdown
# User API PRD

## Business Context
Provide RESTful API for user management operations.

## Endpoints

### GET /api/users/{id}
Returns user details

### POST /api/users
Creates new user

### PUT /api/users/{id}
Updates user information

## Requirements
1. JWT authentication required
2. Rate limiting: 100 requests/minute
3. Response time < 200ms (p95)

## Error Handling
- 400: Invalid input
- 401: Unauthorized
- 404: User not found
- 429: Rate limit exceeded
```

### edge-cases/ - 边界情况

```
edge-cases/
├── empty.md              # 空文件
├── minimal.md            # 最小内容
├── no-sections.md        # 缺少标准章节
├── malformed.md          # 格式错误
└── special-chars.md      # 特殊字符
```

## 🔧 最佳实践

### 测试文件命名

使用描述性的文件名：

```
test-prds/
├── happy-path/              # 正常流程
│   ├── standard-feature.md
│   └── api-endpoint.md
├── edge-cases/              # 边界情况
│   ├── empty-prd.md
│   └── large-prd.md
└── error-cases/             # 错误场景
    ├── invalid-format.md
    └── missing-sections.md
```

### 输出文件命名

包含测试编号和时间戳：

```
test-outputs/
├── TC-001-spec-20260303-1430.md
├── TC-002-spec-20260303-1445.md
└── results-summary.md
```

### 测试记录

在 `scratch/` 中记录测试过程：

```bash
# 创建测试记录
cat > sandbox/scratch/test-session-$(date +%Y%m%d).md << 'EOF'
# Test Session - 2026-03-03

## TC-001: Standard PRD Conversion
- Input: test-prds/sample-login.md
- Command: /speckit.specify
- Result: ✅ Pass
- Notes: All sections mapped correctly

## TC-002: Empty PRD
- Input: test-prds/empty.md
- Command: /speckit.specify
- Result: ❌ Fail - No error message
- Action: Add input validation
EOF
```

## 🚫 注意事项

### 不要提交

- `scratch/` 中的临时文件
- `test-outputs/` 中的生成文件
- 包含敏感信息的测试数据

### 应该提交

- `test-prds/` 中的标准测试用例
- 边界情况测试文件
- 测试结果汇总 (summary.md)

## 📊 测试结果模板

在 `test-outputs/` 中创建汇总文件：

```markdown
# Test Results Summary

**Date**: 2026-03-03  
**Tester**: [Your Name]  
**Requirement**: EXT-001

## Test Cases

| ID | Description | Result | Notes |
|----|-------------|--------|-------|
| TC-001 | Standard PRD | ✅ Pass | All sections correct |
| TC-002 | API PRD | ✅ Pass | API chapters included |
| TC-003 | Empty PRD | ❌ Fail | No validation |
| TC-004 | Large PRD | ⏳ Pending | Performance test |

## Issues Found

1. **Empty file handling**: No error message
2. **Performance**: Large files (>100KB) slow

## Recommendations

- Add input validation
- Optimize large file processing
```

## 🔄 清理

定期清理 sandbox：

```bash
# 清理临时文件
rm -rf sandbox/scratch/*.tmp
rm -rf sandbox/test-outputs/*.md

# 保留测试用例
# test-prds/ 不删除

# 创建清理脚本
cat > sandbox/clean.sh << 'EOF'
#!/bin/bash
echo "🧹 Cleaning sandbox..."
rm -rf scratch/*.tmp
rm -rf scratch/*.bak
find test-outputs/ -name "*.md" -mtime +7 -delete
echo "✓ Done"
EOF
chmod +x sandbox/clean.sh
```

---

**维护者**: Spec Kit 开发团队  
**最后更新**: 2026-03-03
