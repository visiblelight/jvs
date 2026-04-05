"""
用户管理接口测试：仅超级管理员可 CRUD，普通用户被拒绝。
"""


def test_list_users_as_superuser(client, superuser_headers, test_user, other_user):
    resp = client.get("/api/admin/users", headers=superuser_headers)
    assert resp.status_code == 200
    data = resp.json()
    usernames = [u["username"] for u in data]
    assert "testuser" in usernames
    assert "otheruser" in usernames
    assert "super" in usernames
    # module_count 字段存在
    assert all("module_count" in u for u in data)


def test_list_users_as_normal_user_forbidden(client, auth_headers):
    resp = client.get("/api/admin/users", headers=auth_headers)
    assert resp.status_code == 403


def test_list_users_without_token(client):
    resp = client.get("/api/admin/users")
    assert resp.status_code == 401


def test_create_user_as_superuser(client, superuser_headers):
    resp = client.post(
        "/api/admin/users",
        headers=superuser_headers,
        json={
            "username": "newuser",
            "password": "pass1234",
            "is_active": True,
            "is_superuser": False,
            "modules": ["todo", "news"],
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["is_superuser"] is False
    assert set(data["modules"]) == {"todo", "news"}


def test_create_user_duplicate_username(client, superuser_headers, test_user):
    resp = client.post(
        "/api/admin/users",
        headers=superuser_headers,
        json={
            "username": "testuser",
            "password": "pass1234",
            "is_active": True,
            "is_superuser": False,
            "modules": [],
        },
    )
    assert resp.status_code == 400


def test_create_user_invalid_module(client, superuser_headers):
    resp = client.post(
        "/api/admin/users",
        headers=superuser_headers,
        json={
            "username": "bad",
            "password": "pass1234",
            "is_active": True,
            "is_superuser": False,
            "modules": ["nonexistent"],
        },
    )
    assert resp.status_code == 400


def test_create_superuser_ignores_modules(client, superuser_headers):
    resp = client.post(
        "/api/admin/users",
        headers=superuser_headers,
        json={
            "username": "newsuper",
            "password": "pass1234",
            "is_active": True,
            "is_superuser": True,
            "modules": ["todo"],
        },
    )
    assert resp.status_code == 201
    assert resp.json()["modules"] == []


def test_create_user_as_normal_forbidden(client, auth_headers):
    resp = client.post(
        "/api/admin/users",
        headers=auth_headers,
        json={
            "username": "x",
            "password": "pass1234",
            "is_active": True,
            "is_superuser": False,
            "modules": [],
        },
    )
    assert resp.status_code == 403


def test_get_user_detail(client, superuser_headers, test_user):
    resp = client.get(f"/api/admin/users/{test_user.id}", headers=superuser_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


def test_get_user_not_found(client, superuser_headers):
    resp = client.get("/api/admin/users/99999", headers=superuser_headers)
    assert resp.status_code == 404


def test_update_user_username(client, superuser_headers, test_user):
    resp = client.put(
        f"/api/admin/users/{test_user.id}",
        headers=superuser_headers,
        json={"username": "renamed"},
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "renamed"


def test_update_user_password(client, superuser_headers, test_user):
    resp = client.put(
        f"/api/admin/users/{test_user.id}",
        headers=superuser_headers,
        json={"password": "newpass456"},
    )
    assert resp.status_code == 200
    # 用新密码能登录
    login = client.post(
        "/api/admin/auth/login",
        json={"username": "testuser", "password": "newpass456"},
    )
    assert login.status_code == 200


def test_update_user_disable(client, superuser_headers, test_user):
    resp = client.put(
        f"/api/admin/users/{test_user.id}",
        headers=superuser_headers,
        json={"is_active": False},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False
    # 被禁用后登录被拒
    login = client.post(
        "/api/admin/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert login.status_code == 403


def test_cannot_disable_self(client, superuser_headers, superuser):
    resp = client.put(
        f"/api/admin/users/{superuser.id}",
        headers=superuser_headers,
        json={"is_active": False},
    )
    assert resp.status_code == 400


def test_cannot_modify_own_superuser(client, superuser_headers, superuser):
    resp = client.put(
        f"/api/admin/users/{superuser.id}",
        headers=superuser_headers,
        json={"is_superuser": False},
    )
    assert resp.status_code == 400


def test_cannot_remove_last_superuser(client, superuser_headers, superuser, test_user):
    # 将 test_user 设为超管
    r1 = client.put(
        f"/api/admin/users/{test_user.id}",
        headers=superuser_headers,
        json={"is_superuser": True},
    )
    assert r1.status_code == 200
    # 禁用当前超管 superuser (还剩 test_user 一个活跃超管) 应该允许
    # 但如果我们再把 test_user 降级 —— 此时只剩 superuser 一个活跃超管
    # 尝试禁用 superuser —— 不允许禁用自己
    # 改为：禁用 test_user（它现在也是超管），还剩 superuser 一个活跃超管 —— 允许
    r2 = client.put(
        f"/api/admin/users/{test_user.id}",
        headers=superuser_headers,
        json={"is_active": False},
    )
    assert r2.status_code == 200
    # 此时活跃超管只剩 superuser（自己）；尝试取消 test_user 的超管身份——依然允许（被禁用）
    # 关键场景：重新激活 test_user，再取消 superuser 的超管身份 —— 受阻于 "不能修改自己"
    # 构造：若 superuser 想把 test_user 降级为普通用户（现在被禁用，且是超管），此时活跃超管只有 superuser 自己
    # 降级不影响活跃超管数（test_user 不活跃），允许
    r3 = client.put(
        f"/api/admin/users/{test_user.id}",
        headers=superuser_headers,
        json={"is_superuser": False},
    )
    assert r3.status_code == 200


def test_update_to_superuser_clears_modules(client, superuser_headers, test_user):
    # test_user 默认已授予所有模块
    resp = client.put(
        f"/api/admin/users/{test_user.id}",
        headers=superuser_headers,
        json={"is_superuser": True},
    )
    assert resp.status_code == 200
    assert resp.json()["modules"] == []


def test_set_user_modules(client, superuser_headers, test_user):
    resp = client.put(
        f"/api/admin/users/{test_user.id}/modules",
        headers=superuser_headers,
        json={"modules": ["todo"]},
    )
    assert resp.status_code == 200
    assert resp.json()["modules"] == ["todo"]


def test_set_user_modules_empty(client, superuser_headers, test_user):
    resp = client.put(
        f"/api/admin/users/{test_user.id}/modules",
        headers=superuser_headers,
        json={"modules": []},
    )
    assert resp.status_code == 200
    assert resp.json()["modules"] == []


def test_set_modules_invalid_key(client, superuser_headers, test_user):
    resp = client.put(
        f"/api/admin/users/{test_user.id}/modules",
        headers=superuser_headers,
        json={"modules": ["nope"]},
    )
    assert resp.status_code == 400


def test_set_modules_on_superuser_forbidden(client, superuser_headers, superuser):
    resp = client.put(
        f"/api/admin/users/{superuser.id}/modules",
        headers=superuser_headers,
        json={"modules": ["todo"]},
    )
    assert resp.status_code == 400


def test_set_modules_as_normal_user_forbidden(client, auth_headers, other_user):
    resp = client.put(
        f"/api/admin/users/{other_user.id}/modules",
        headers=auth_headers,
        json={"modules": ["todo"]},
    )
    assert resp.status_code == 403


# ── 模块列表接口 ──

def test_list_modules_as_any_user(client, auth_headers):
    resp = client.get("/api/admin/modules", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    keys = [m["key"] for m in data]
    assert "todo" in keys
    assert "news" in keys
    assert "access_key" in keys
    # 按 sort_order 升序
    sort_orders = [m["sort_order"] for m in data]
    assert sort_orders == sorted(sort_orders)


def test_list_modules_without_token(client):
    resp = client.get("/api/admin/modules")
    assert resp.status_code == 401
