"""
认证模块测试：登录、token 校验、权限拦截
"""


def test_login_success(client, test_user):
    resp = client.post("/api/admin/auth/login", json={
        "username": "testuser",
        "password": "testpass123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    resp = client.post("/api/admin/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    resp = client.post("/api/admin/auth/login", json={
        "username": "nobody",
        "password": "whatever",
    })
    assert resp.status_code == 401


def test_protected_route_without_token(client):
    resp = client.get("/api/admin/todo/items")
    assert resp.status_code == 401


def test_protected_route_with_invalid_token(client):
    resp = client.get(
        "/api/admin/todo/items",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert resp.status_code == 401


def test_protected_route_with_valid_token(client, auth_headers):
    resp = client.get("/api/admin/todo/items", headers=auth_headers)
    assert resp.status_code == 200


def test_get_me(client, auth_headers, test_user):
    resp = client.get("/api/admin/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == test_user.username
