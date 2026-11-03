# 开放 API — 新闻接口文档

基础路径：`/api/open/news`

所有接口使用 Access Key 鉴权，请求头传递 `X-Access-Key: <key>`。提交的数据自动归属 Key 所属用户。

---

## POST /articles
Agent 提交新闻文章。

**鉴权**：`X-Access-Key` 请求头

**请求体**
```json
{
  "title": "文章标题",
  "summary": "简要介绍（可选，200字以内）",
  "content": "Markdown 格式正文",
  "source_url": "https://原文链接（可选）",
  "source_name": "来源名称（可选，不存在则自动创建）",
  "author": "作者（可选）",
  "published_at": "2026-03-20T10:00:00Z（可选）",
  "category_name": "分类名称（可选，不存在则自动创建）"
}
```

**说明**
- `source_name` 和 `category_name` 通过名称匹配该用户已有的来源/分类，不存在则自动创建
- `source_id` 和 `category_id` 由服务端通过名称解析，无需客户端传递

**响应** `201`
```json
{
  "id": 1,
  "title": "文章标题",
  "summary": "...",
  "content": "...",
  "source_url": "...",
  "source_id": 1,
  "author": "...",
  "published_at": "...",
  "category_id": 1,
  "created_at": "...",
  "updated_at": "...",
  "category": { "id": 1, "name": "科技", "sort_order": 0, "created_at": "..." },
  "source": { "id": 1, "name": "微信公众号", "created_at": "..." }
}
```

**错误响应**
- `401` — Access Key 无效或未提供
- `403` — Key 关联的用户不存在或已被禁用
- `422` — 请求体验证失败

## 时间格式（Plan 024）

所有时间点返回带 `Z`（UTC）的 ISO 8601，例如 `2026-11-03T05:00:00Z`，上海客户端显示 13:00。写入截止时间、执行时间、新闻发布时间或提交日历查询边界时必须带 `Z` 或 `+08:00` 等偏移量；无时区时间点返回 422。纯日期 `YYYY-MM-DD` 不做时间点转换。未传字段保持不变，可选字段传 null 可清空。
