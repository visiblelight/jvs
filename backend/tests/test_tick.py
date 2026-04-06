"""
打卡板块测试：任务 CRUD、打卡/撤销、积分计算、周期判定、权限拦截
"""
from datetime import date

from app.services.tick import compute_period_key, compute_points, _prev_period_key


# ── 纯函数测试 ──

def test_compute_period_key_daily():
    assert compute_period_key("daily", date(2026, 4, 6)) == "2026-04-06"


def test_compute_period_key_weekly():
    # 2026-04-06 是周一，ISO week 15
    assert compute_period_key("weekly", date(2026, 4, 6)) == "2026-W15"


def test_compute_period_key_monthly():
    assert compute_period_key("monthly", date(2026, 4, 6)) == "2026-04"


def test_prev_period_key_daily():
    assert _prev_period_key("daily", "2026-04-06") == "2026-04-05"
    assert _prev_period_key("daily", "2026-01-01") == "2025-12-31"


def test_prev_period_key_weekly():
    assert _prev_period_key("weekly", "2026-W15") == "2026-W14"
    assert _prev_period_key("weekly", "2026-W01") == "2025-W52"


def test_prev_period_key_monthly():
    assert _prev_period_key("monthly", "2026-04") == "2026-03"
    assert _prev_period_key("monthly", "2026-01") == "2025-12"


def test_compute_points_empty_rule():
    assert compute_points([], 3) == 0


def test_compute_points_tiered():
    rules = [
        {"streak": 1, "points": 1},
        {"streak": 2, "points": 2},
        {"streak": 3, "points": 3},
    ]
    assert compute_points(rules, 1) == 1
    assert compute_points(rules, 2) == 2
    assert compute_points(rules, 3) == 3
    assert compute_points(rules, 10) == 3  # 超过最大档，沿用最后一档


def test_compute_points_single_rule():
    rules = [{"streak": 1, "points": 5}]
    assert compute_points(rules, 1) == 5
    assert compute_points(rules, 100) == 5


# ── API 测试 ──

def test_create_task(client, auth_headers):
    resp = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "跳绳",
        "frequency": "daily",
        "start_date": "2026-04-01",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "跳绳"
    assert data["frequency"] == "daily"
    assert data["total_ticks"] == 0
    assert data["current_streak"] == 0
    assert data["ticked_this_period"] is False


def test_list_tasks(client, auth_headers):
    client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "A", "frequency": "daily", "start_date": "2026-04-01",
    })
    client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "B", "frequency": "weekly", "start_date": "2026-04-01",
    })
    resp = client.get("/api/admin/tick/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 2


def test_list_tasks_filter_archived(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "Archived", "frequency": "daily", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    client.put(f"/api/admin/tick/tasks/{task_id}", headers=auth_headers, json={"is_archived": True})
    resp = client.get("/api/admin/tick/tasks?is_archived=false", headers=auth_headers)
    titles = [t["title"] for t in resp.json()["items"]]
    assert "Archived" not in titles


def test_get_task(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "详情", "frequency": "monthly", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    resp = client.get(f"/api/admin/tick/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "详情"


def test_update_task(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "旧名", "frequency": "daily", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    resp = client.put(f"/api/admin/tick/tasks/{task_id}", headers=auth_headers, json={"title": "新名"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "新名"


def test_delete_task(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "删我", "frequency": "daily", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    resp = client.delete(f"/api/admin/tick/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 204
    resp2 = client.get(f"/api/admin/tick/tasks/{task_id}", headers=auth_headers)
    assert resp2.status_code == 404


def test_do_tick_and_streak(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "打卡测试",
        "frequency": "daily",
        "start_date": "2026-04-01",
        "enable_points": True,
        "points_rule": [
            {"streak": 1, "points": 1},
            {"streak": 2, "points": 2},
            {"streak": 3, "points": 3},
        ],
    })
    task_id = r.json()["id"]
    resp = client.post(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers, json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_streak"] >= 1
    assert data["log"]["points_earned"] >= 0


def test_do_tick_duplicate_rejected(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "重复打卡", "frequency": "daily", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    client.post(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers, json={})
    resp = client.post(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers, json={})
    assert resp.status_code == 400
    assert "已打卡" in resp.json()["detail"]


def test_undo_tick(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "撤销测试", "frequency": "daily", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    client.post(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers, json={})
    # 撤销
    resp = client.delete(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers)
    assert resp.status_code == 204
    # 撤销后可重新打卡
    resp2 = client.post(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers, json={})
    assert resp2.status_code == 200


def test_undo_tick_when_not_ticked(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "未打卡撤销", "frequency": "daily", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    resp = client.delete(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers)
    assert resp.status_code == 400
    assert "未打卡" in resp.json()["detail"]


def test_tick_archived_task_rejected(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "归档任务", "frequency": "daily", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    client.put(f"/api/admin/tick/tasks/{task_id}", headers=auth_headers, json={"is_archived": True})
    resp = client.post(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers, json={})
    assert resp.status_code == 400
    assert "归档" in resp.json()["detail"]


def test_tick_with_quality(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "质量打卡", "frequency": "daily", "start_date": "2026-04-01",
        "enable_quality": True,
    })
    task_id = r.json()["id"]
    resp = client.post(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers, json={
        "quality": 4, "note": "不错的一天",
    })
    assert resp.status_code == 200
    assert resp.json()["log"]["quality"] == 4
    assert resp.json()["log"]["note"] == "不错的一天"


def test_get_logs(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "日志查询", "frequency": "daily", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    client.post(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers, json={})
    resp = client.get(f"/api/admin/tick/tasks/{task_id}/logs", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_ticked_this_period_flag(client, auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "周期标记", "frequency": "daily", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    # 未打卡
    detail = client.get(f"/api/admin/tick/tasks/{task_id}", headers=auth_headers).json()
    assert detail["ticked_this_period"] is False
    # 打卡后
    client.post(f"/api/admin/tick/tasks/{task_id}/tick", headers=auth_headers, json={})
    detail2 = client.get(f"/api/admin/tick/tasks/{task_id}", headers=auth_headers).json()
    assert detail2["ticked_this_period"] is True


def test_data_isolation(client, auth_headers, other_auth_headers):
    r = client.post("/api/admin/tick/tasks", headers=auth_headers, json={
        "title": "A的任务", "frequency": "daily", "start_date": "2026-04-01",
    })
    task_id = r.json()["id"]
    # B 不应看到 A 的任务
    resp = client.get(f"/api/admin/tick/tasks/{task_id}", headers=other_auth_headers)
    assert resp.status_code == 404


def test_tick_module_permission(client, user_no_modules_headers):
    resp = client.get("/api/admin/tick/tasks", headers=user_no_modules_headers)
    assert resp.status_code == 403


def test_superuser_bypasses_tick_permission(client, superuser_headers):
    resp = client.get("/api/admin/tick/tasks", headers=superuser_headers)
    assert resp.status_code == 200
