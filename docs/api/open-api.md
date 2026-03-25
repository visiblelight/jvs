# JVS 开放 API 文档

**版本**: v1
**Base URL**: `https://<your-domain>/api/open`
**本地开发**: `http://localhost:8000/api/open`
**交互式文档**: `http://localhost:8000/docs`

---

## 目录

1. [概述](#1-概述)
2. [鉴权：Access Key](#2-鉴权access-key)
3. [接口：提交文章](#3-接口提交文章)
4. [数据结构](#4-数据结构)
5. [错误处理](#5-错误处理)
6. [代码示例](#6-代码示例)
7. [Agent 使用指南](#7-agent-使用指南)

---

## 1. 概述

JVS 开放 API 允许经过授权的第三方（开发者、脚本、AI Agent）向系统提交内容。

**当前支持能力**

| 功能 | 方法 | 路径 |
|------|------|------|
| 提交新闻文章 | `POST` | `/api/open/news/articles` |

**协议约定**

- 所有请求和响应均使用 `application/json`
- 时间字段均为 UTC，格式遵循 [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html)（例：`2026-03-22T10:30:00Z`）
- 字符串字段不自动截断，超长会返回 `422`

---

## 2. 鉴权：Access Key

### 2.1 什么是 Access Key

Access Key 是一个 64 位十六进制字符串，用于标识调用方身份。每个 Key 绑定到一个 JVS 账号，并附带细粒度的权限范围（scope）。

**示例**
```
a3f8c2d1e4b5a6f7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1
```

### 2.2 如何获取 Access Key

1. 登录 JVS 管理后台
2. 点击左侧栏头像 → 进入「个人中心」
3. 切换到「Access Keys」标签页
4. 点击「新建 Key」，填写名称，勾选所需权限（`news:create`）
5. **Key 仅在创建时完整显示一次**，请立即复制保存

### 2.3 在请求中携带 Key

将 Access Key 放在 HTTP 请求头 `X-Access-Key` 中：

```http
X-Access-Key: a3f8c2d1e4b5a6f7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1
```

### 2.4 权限范围（Scopes）

| Scope | 描述 | 所需接口 |
|-------|------|----------|
| `news:create` | 提交新闻文章 | `POST /api/open/news/articles` |

创建 Key 时必须勾选对应 scope，否则调用会返回 `403`。

---

## 3. 接口：提交文章

### `POST /api/open/news/articles`

向 JVS 系统提交一篇新闻文章。

#### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| `Content-Type` | 是 | `application/json` |
| `X-Access-Key` | 是 | 持有 `news:create` 权限的 Access Key |

#### 请求体

```json
{
  "title": "string",
  "summary": "string | null",
  "content": "string",
  "source_url": "string | null",
  "source_name": "string | null",
  "author": "string | null",
  "published_at": "string (ISO 8601) | null",
  "category_name": "string | null"
}
```

**字段说明**

| 字段 | 类型 | 必填 | 最大长度 | 说明 |
|------|------|------|----------|------|
| `title` | string | **是** | 300 | 文章标题 |
| `summary` | string | 否 | 200 | 摘要，用于列表页展示 |
| `content` | string | **是** | 无限制 | 正文，支持 Markdown |
| `source_url` | string | 否 | 500 | 原文链接 URL |
| `source_name` | string | 否 | 100 | 来源名称（如「澎湃新闻」）。若不存在则自动创建 |
| `author` | string | 否 | 100 | 作者姓名 |
| `published_at` | string | 否 | — | 原始发布时间，ISO 8601 格式，建议带时区（`Z` 或 `+08:00`） |
| `category_name` | string | 否 | 100 | 分类名称（如「科技」）。若不存在则自动创建 |

> **自动创建机制**：`source_name` 和 `category_name` 若在系统中不存在，会自动创建并归属到当前 Access Key 对应的账号下，无需预先配置。

#### 响应

**成功** — HTTP `201 Created`

```json
{
  "id": 42,
  "title": "示例文章标题",
  "summary": "这是文章摘要",
  "content": "正文内容...",
  "source_url": "https://example.com/article/123",
  "source_id": 5,
  "author": "张三",
  "published_at": "2026-03-22T08:00:00Z",
  "category_id": 3,
  "created_at": "2026-03-22T10:30:00Z",
  "updated_at": "2026-03-22T10:30:00Z",
  "category": {
    "id": 3,
    "name": "科技",
    "sort_order": 0,
    "created_at": "2026-03-01T00:00:00Z"
  },
  "source": {
    "id": 5,
    "name": "澎湃新闻",
    "created_at": "2026-03-10T00:00:00Z"
  }
}
```

**响应字段说明**

| 字段 | 说明 |
|------|------|
| `id` | 文章在系统中的唯一 ID |
| `source_id` | 系统内部来源 ID（自动关联） |
| `category_id` | 系统内部分类 ID（自动关联） |
| `created_at` | 系统接收时间（UTC） |
| `updated_at` | 最后更新时间（UTC） |
| `category` | 完整分类对象，`null` 表示未分类 |
| `source` | 完整来源对象，`null` 表示无来源 |

---

## 4. 数据结构

### Article 对象（完整）

```typescript
interface Article {
  id: number
  title: string
  summary: string | null
  content: string
  source_url: string | null
  source_id: number | null
  author: string | null
  published_at: string | null    // ISO 8601 UTC
  category_id: number | null
  created_at: string             // ISO 8601 UTC
  updated_at: string             // ISO 8601 UTC
  category: Category | null
  source: Source | null
}

interface Category {
  id: number
  name: string
  sort_order: number
  created_at: string
}

interface Source {
  id: number
  name: string
  created_at: string
}
```

---

## 5. 错误处理

所有错误响应均返回如下结构：

```json
{
  "detail": "错误说明"
}
```

**HTTP 状态码说明**

| 状态码 | 含义 | 常见原因 |
|--------|------|----------|
| `201` | 创建成功 | — |
| `401` | 鉴权失败 | `X-Access-Key` 缺失、Key 不存在或已禁用 |
| `403` | 权限不足 | Key 未授予 `news:create` scope；或账号已被系统管理员禁用 |
| `422` | 请求体校验失败 | 字段超长、类型错误、缺少必填字段 |
| `500` | 服务器内部错误 | 联系系统管理员 |

**422 示例**（字段类型错误）

```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "title"],
      "msg": "String should have at most 300 characters",
      "input": "...(过长的字符串)..."
    }
  ]
}
```

---

## 6. 代码示例

### cURL

```bash
curl -X POST "http://localhost:8000/api/open/news/articles" \
  -H "Content-Type: application/json" \
  -H "X-Access-Key: <your-access-key>" \
  -d '{
    "title": "OpenAI 发布 GPT-5",
    "summary": "GPT-5 在多项基准测试中超越人类专家",
    "content": "## 发布详情\n\nOpenAI 于今日正式发布 GPT-5...",
    "source_url": "https://openai.com/blog/gpt-5",
    "source_name": "OpenAI Blog",
    "author": "OpenAI Team",
    "published_at": "2026-03-22T09:00:00Z",
    "category_name": "AI"
  }'
```

### Python

```python
import httpx
from datetime import datetime, timezone

ACCESS_KEY = "your-access-key-here"
BASE_URL = "http://localhost:8000/api/open"

def submit_article(title: str, content: str, **kwargs) -> dict:
    response = httpx.post(
        f"{BASE_URL}/news/articles",
        headers={
            "Content-Type": "application/json",
            "X-Access-Key": ACCESS_KEY,
        },
        json={
            "title": title,
            "content": content,
            **kwargs,
        },
    )
    response.raise_for_status()
    return response.json()

# 使用示例
article = submit_article(
    title="OpenAI 发布 GPT-5",
    content="## 发布详情\n\nOpenAI 于今日正式发布 GPT-5...",
    summary="GPT-5 在多项基准测试中超越人类专家",
    source_url="https://openai.com/blog/gpt-5",
    source_name="OpenAI Blog",
    author="OpenAI Team",
    published_at="2026-03-22T09:00:00Z",
    category_name="AI",
)
print(f"文章已创建，ID: {article['id']}")
```

### JavaScript / Node.js

```javascript
const ACCESS_KEY = 'your-access-key-here';
const BASE_URL = 'http://localhost:8000/api/open';

async function submitArticle({ title, content, ...options }) {
  const response = await fetch(`${BASE_URL}/news/articles`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Access-Key': ACCESS_KEY,
    },
    body: JSON.stringify({ title, content, ...options }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`${response.status}: ${JSON.stringify(error.detail)}`);
  }

  return response.json();
}

// 使用示例
const article = await submitArticle({
  title: 'OpenAI 发布 GPT-5',
  content: '## 发布详情\n\nOpenAI 于今日正式发布 GPT-5...',
  summary: 'GPT-5 在多项基准测试中超越人类专家',
  source_url: 'https://openai.com/blog/gpt-5',
  source_name: 'OpenAI Blog',
  author: 'OpenAI Team',
  published_at: '2026-03-22T09:00:00Z',
  category_name: 'AI',
});
console.log(`文章已创建，ID: ${article.id}`);
```

---

## 7. Agent 使用指南

本节专为 AI Agent（如 OpenClaw、AutoGPT 等）设计，描述如何通过工具调用提交文章。

### 7.1 工具定义（Tool Spec）

以下为标准 JSON Schema 格式的工具定义，可直接注册到 Agent 框架：

```json
{
  "name": "jvs_submit_article",
  "description": "向 JVS 系统提交一篇新闻文章。支持自动创建分类和来源。成功后返回文章 ID。",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "文章标题，必填，最长 300 字符"
      },
      "content": {
        "type": "string",
        "description": "文章正文，必填，支持 Markdown 格式"
      },
      "summary": {
        "type": "string",
        "description": "文章摘要，可选，最长 200 字符，用于列表页预览"
      },
      "source_url": {
        "type": "string",
        "description": "原文链接 URL，可选"
      },
      "source_name": {
        "type": "string",
        "description": "来源名称，可选，如「Reuters」「澎湃新闻」。若系统中不存在则自动创建"
      },
      "author": {
        "type": "string",
        "description": "作者姓名，可选"
      },
      "published_at": {
        "type": "string",
        "description": "原始发布时间，可选，ISO 8601 格式，例：2026-03-22T09:00:00Z"
      },
      "category_name": {
        "type": "string",
        "description": "分类名称，可选，如「科技」「财经」。若系统中不存在则自动创建"
      }
    },
    "required": ["title", "content"]
  }
}
```

### 7.2 调用约定

**HTTP 请求**

```
POST {BASE_URL}/api/open/news/articles
Header: X-Access-Key: {ACCESS_KEY}
Header: Content-Type: application/json
Body: { ...工具参数 }
```

**成功判断**：HTTP 状态码为 `201`，响应体中 `id` 字段即为创建的文章 ID。

**失败处理**：

| 状态码 | Agent 应对策略 |
|--------|--------------|
| `401` | 停止重试，上报 Key 无效，需人工介入 |
| `403` | 停止重试，上报权限不足，需人工介入 |
| `422` | 检查参数是否超长或格式错误，修正后可重试 |
| `5xx` | 可指数退避重试，最多 3 次 |

### 7.3 内容质量建议

- **`content`** 建议使用 Markdown，换行用 `\n`，代码块用 ` ``` `
- **`summary`** 建议控制在 100 字以内，作为可读性最强的一句话摘要
- **`published_at`** 应使用原文发布时间，而非 Agent 执行时间；如无法获取则留空
- **`category_name`** 建议从固定词表中选取（如「科技」「财经」「政策」「国际」），避免过度细分导致分类碎片化
- 同一篇文章不要重复提交；如需检查是否已存在，可通过 `source_url` 在业务层做去重判断

### 7.4 最简调用示例（Agent 伪代码）

```python
# Agent 执行步骤示意
result = call_tool("jvs_submit_article", {
    "title": extracted_title,
    "content": extracted_content,
    "summary": generated_summary[:200],
    "source_url": original_url,
    "source_name": extracted_source,
    "published_at": publish_time.isoformat() + "Z",
    "category_name": classified_category,
})

if result["status_code"] == 201:
    article_id = result["body"]["id"]
    # 任务完成，记录 article_id
else:
    # 根据状态码决定是否重试或上报
```

---

## 附录：完整 cURL 示例（可直接运行）

将下方的 `<your-access-key>` 替换为真实 Key 后直接执行：

```bash
curl -s -X POST "http://localhost:8000/api/open/news/articles" \
  -H "Content-Type: application/json" \
  -H "X-Access-Key: <your-access-key>" \
  -d '{
    "title": "测试文章",
    "content": "这是一篇测试文章的正文内容。",
    "category_name": "测试"
  }' | python3 -m json.tool
```

预期输出（HTTP 201）：

```json
{
    "id": 1,
    "title": "测试文章",
    "summary": null,
    "content": "这是一篇测试文章的正文内容。",
    "source_url": null,
    "source_id": null,
    "author": null,
    "published_at": null,
    "category_id": 1,
    "created_at": "2026-03-22T10:30:00Z",
    "updated_at": "2026-03-22T10:30:00Z",
    "category": {
        "id": 1,
        "name": "测试",
        "sort_order": 0,
        "created_at": "2026-03-22T10:30:00Z"
    },
    "source": null
}
```
