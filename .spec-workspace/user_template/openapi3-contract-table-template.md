# OpenAPI 3.0 Interface Contract Table Template（接口契约表格模板）: [I-XXX-InterfaceName（接口名）]

> 用途：将 `contracts/api.openapi.yaml`（OpenAPI 3.0.x）中的单个接口定义，
> 进行 **可读性优先** 的结构化表格镜像，便于评审、联调与实现落地。

**Interface ID**: [I-XXX]  
**Path**: [/api/v1/...]  
**Method**: [GET/POST/PUT/DELETE/PATCH]  
**OperationId**: [operationId]  
**Tags**: [[tag1], [tag2]]

---

## 1. Operation Summary（摘要）

| Field（字段） | Value（值） |
|------|----|
| summary | [接口摘要] |
| description | [接口详细说明] |
| deprecated | [true/false] |
| security | [如: bearerAuth / apiKeyAuth / none] |
| servers | [如有覆盖: https://api.example.com] |

---

## 2. Parameters（path/query/header/cookie）

> 对应 OpenAPI: `paths.{path}.{method}.parameters[]` 与 path-level `parameters[]`

| ParameterName（参数名） | in | required | schema.type | schema.format | schema.$ref | style/explode | enum/default/example | Constraints（约束；min/max/pattern） | Description（描述） |
|--------|----|----------|-------------|---------------|-------------|---------------|----------------------|---------------------------|------|
| [id] | path | true | string | uuid | - | simple/false | - | pattern: `^[0-9a-fA-F-]{36}$` | [资源主键] |
| [page] | query | false | integer | int32 | - | form/true | default=1 | minimum=1 | [分页页码] |
| [X-Trace-Id] | header | false | string | - | - | simple/false | example=`trace-xxx` | maxLength=64 | [链路追踪] |

---

## 3. Request Body

> 对应 OpenAPI: `requestBody`

### 3.1 Request Body Metadata（元信息）

| Field（字段） | Value（值） |
|------|----|
| requestBody.required | [true/false] |
| content-type | [application/json / multipart/form-data / application/xml ...] |
| schema.$ref | [#/components/schemas/XxxRequest] |
| oneOf/anyOf/allOf | [若存在则注明组合关系] |
| example/examples | [示例名称或简述] |

### 3.2 Request Body Field Expansion (Optional but Recommended)（字段展开）

| FieldPath（字段路径） | Type（类型） | Required（必填） | Constraints（约束） | Example（示例） | Description（描述） |
|----------|------|------|------|------|------|
| [name] | string | 是 | maxLength=64 | `"Alice"` | [姓名] |
| [address.city] | string | 否 | - | `"Shanghai"` | [城市] |
| [items[].sku] | string | 是 | pattern=`^[A-Z0-9_-]+$` | `"SKU_001"` | [商品编码] |

---

## 4. Responses

> 对应 OpenAPI: `responses`

### 4.1 Response Overview（响应总览）

| HTTPStatus（HTTP状态码） | content-type | schema.$ref / schema.type | headers | description |
|-------------|--------------|---------------------------|---------|-------------|
| 200 | application/json | `#/components/schemas/XxxResponse` | `X-Request-Id` | [成功响应] |
| 400 | application/json | `#/components/schemas/ErrorResponse` | - | [参数错误] |
| 401 | application/json | `#/components/schemas/ErrorResponse` | - | [未认证] |
| 500 | application/json | `#/components/schemas/ErrorResponse` | - | [服务异常] |

### 4.2 Response Field Expansion (by status code, repeatable)（响应体字段展开）

#### 200 Response Fields（字段）

| FieldPath（字段路径） | Type（类型） | Required（必填） | Constraints（约束） | Example（示例） | Description（描述） |
|----------|------|------|------|------|------|
| [code] | integer | 是 | enum=[0] | `0` | [业务成功码] |
| [message] | string | 是 | - | `"OK"` | [提示信息] |
| [data.id] | string | 是 | format=uuid | `"..."` | [业务实体ID] |

#### 400 Response Fields（字段）

| FieldPath（字段路径） | Type（类型） | Required（必填） | Constraints（约束） | Example（示例） | Description（描述） |
|----------|------|------|------|------|------|
| [error.code] | string | 是 | - | `"INVALID_PARAM"` | [错误码] |
| [error.message] | string | 是 | - | `"name is required"` | [错误描述] |

---

## 5. Components Reference List (Trace)（引用清单）

> 对应 OpenAPI: `components.schemas / parameters / responses / headers / securitySchemes`

| ReferenceType（引用类型） | ReferencePath（引用路径） | Purpose（用途） | Notes（备注） |
|----------|----------|------|------|
| schema | `#/components/schemas/XxxRequest` | 请求体 | - |
| schema | `#/components/schemas/XxxResponse` | 成功响应 | - |
| response | `#/components/responses/BadRequest` | 复用错误响应 | - |
| securityScheme | `#/components/securitySchemes/bearerAuth` | 鉴权 | JWT |

---

## 6. Consistency Checklist（一致性Checklist（检查清单））（OpenAPI 3.0）

- [ ] parameters 的 `in/required/schema` 与原 OpenAPI 定义一致
- [ ] requestBody 的 `required/content/schema` 与原 OpenAPI 定义一致
- [ ] responses 的每个状态码、content-type、schema 引用完整
- [ ] headers / examples / default / enum / deprecated 信息未遗漏
- [ ] 组件引用路径（`#/components/...`）全部可解析
