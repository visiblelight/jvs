"""
板块权限拦截测试：用户只能访问已授权的板块 API。
"""


def test_no_modules_cannot_access_todo(client, user_no_modules_headers):
    resp = client.get("/api/admin/todo/items", headers=user_no_modules_headers)
    assert resp.status_code == 403


def test_no_modules_cannot_access_news(client, user_no_modules_headers):
    resp = client.get("/api/admin/news/articles", headers=user_no_modules_headers)
    assert resp.status_code == 403


def test_no_modules_cannot_access_access_key(client, user_no_modules_headers):
    resp = client.get("/api/admin/access-keys", headers=user_no_modules_headers)
    assert resp.status_code == 403


def test_todo_only_can_access_todo(client, user_todo_only_headers):
    resp = client.get("/api/admin/todo/items", headers=user_todo_only_headers)
    assert resp.status_code == 200


def test_todo_only_cannot_access_news(client, user_todo_only_headers):
    resp = client.get("/api/admin/news/articles", headers=user_todo_only_headers)
    assert resp.status_code == 403


def test_todo_only_cannot_access_access_key(client, user_todo_only_headers):
    resp = client.get("/api/admin/access-keys", headers=user_todo_only_headers)
    assert resp.status_code == 403


def test_superuser_bypasses_module_check(client, superuser_headers):
    # superuser 没有 UserModule 记录，但应全部通过
    r1 = client.get("/api/admin/todo/items", headers=superuser_headers)
    assert r1.status_code == 200
    r2 = client.get("/api/admin/news/articles", headers=superuser_headers)
    assert r2.status_code == 200
    r3 = client.get("/api/admin/access-keys", headers=superuser_headers)
    assert r3.status_code == 200


def test_full_access_user_can_access_all(client, auth_headers):
    # test_user 被授予所有模块
    r1 = client.get("/api/admin/todo/items", headers=auth_headers)
    assert r1.status_code == 200
    r2 = client.get("/api/admin/news/articles", headers=auth_headers)
    assert r2.status_code == 200
    r3 = client.get("/api/admin/access-keys", headers=auth_headers)
    assert r3.status_code == 200


def test_module_check_write_also_blocked(client, user_todo_only_headers):
    # 写接口同样受保护 —— 创建分类
    resp = client.post(
        "/api/admin/news/categories",
        headers=user_todo_only_headers,
        json={"name": "x"},
    )
    assert resp.status_code == 403


def test_me_includes_modules(client, user_todo_only_headers):
    resp = client.get("/api/admin/auth/me", headers=user_todo_only_headers)
    assert resp.status_code == 200
    assert resp.json()["modules"] == ["todo"]


def test_me_superuser_modules_empty(client, superuser_headers):
    resp = client.get("/api/admin/auth/me", headers=superuser_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_superuser"] is True
    assert data["modules"] == []
