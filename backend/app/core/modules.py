"""后台板块注册表。

单一事实源：MODULES 列表定义了所有可分配的业务板块。
- key         : 板块唯一标识（对应 require_module 依赖）
- label       : 展示名称
- sort_order  : 排序权重（升序）
"""

MODULES = [
    {"key": "todo",       "label": "事项管理", "sort_order": 10},
    {"key": "tick",       "label": "打卡管理", "sort_order": 15},
    {"key": "news",       "label": "新闻资讯", "sort_order": 20},
    {"key": "access_key", "label": "开放接口", "sort_order": 30},
]

MODULE_KEYS = {m["key"] for m in MODULES}


def get_modules_sorted() -> list[dict]:
    return sorted(MODULES, key=lambda m: m["sort_order"])
