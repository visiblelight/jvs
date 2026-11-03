# API 文档

管理端和移动端共用 `/api/admin`，使用 Bearer JWT。开放 API 位于 `/api/open`，使用带 scope 的 X-Access-Key。业务数据按用户隔离，普通编辑与快捷操作遵循同一业务规则。

- [认证、头像与图片约束](admin-auth.md)
- [事项、归档、回收站](admin-todo.md)
- [打卡、积分、补录与业务时区](admin-tick.md)
- [新闻](admin-news.md)
- [用户与板块权限](admin-users.md)
- [Access Key](admin-access-key.md)
- [开放新闻接口](open-news.md)
- [开放 API 使用说明](open-api.md)

时间点输出带 UTC 时区标记，时间点输入要求带 Z 或偏移量；纯日期不转换。打卡业务时区为 Asia/Shanghai。接口详细结构也可通过后端 /docs 查看。
