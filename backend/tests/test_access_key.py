"""
Access Key 测试：生成、列表、权限校验、隔离
"""
VALID_SCOPE = "news:create"


def create_key(client, headers, name="测试Key", scopes=None):
    payload = {"name": name, "scopes": scopes or [VALID_SCOPE]}
    resp = client.post("/api/admin/access-keys", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


class TestAccessKey:
    def test_create_and_list(self, client, auth_headers):
        create_key(client, auth_headers, "我的Key")
        resp = client.get("/api/admin/access-keys", headers=auth_headers)
        assert resp.status_code == 200
        assert any(k["name"] == "我的Key" for k in resp.json())

    def test_key_value_is_generated(self, client, auth_headers):
        key = create_key(client, auth_headers)
        assert key["key"] and len(key["key"]) > 10

    def test_invalid_scope_rejected(self, client, auth_headers):
        resp = client.post("/api/admin/access-keys", json={
            "name": "非法Key", "scopes": ["nonexistent:scope"]
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_update(self, client, auth_headers):
        key = create_key(client, auth_headers, "旧名称")
        resp = client.put(f"/api/admin/access-keys/{key['id']}",
                          json={"name": "新名称"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "新名称"

    def test_delete(self, client, auth_headers):
        key = create_key(client, auth_headers, "待删除Key")
        resp = client.delete(f"/api/admin/access-keys/{key['id']}", headers=auth_headers)
        assert resp.status_code == 204

    def test_isolation(self, client, auth_headers, other_auth_headers):
        key = create_key(client, auth_headers)
        resp = client.delete(f"/api/admin/access-keys/{key['id']}", headers=other_auth_headers)
        assert resp.status_code == 404

    def test_open_api_with_valid_key(self, client, auth_headers):
        """有效 key 可访问开放接口"""
        key = create_key(client, auth_headers, scopes=[VALID_SCOPE])
        resp = client.post("/api/open/news/articles",
                           json={"title": "开放接口文章", "content": "内容"},
                           headers={"X-Access-Key": key["key"]})
        assert resp.status_code == 201

    def test_open_api_with_invalid_key(self, client):
        resp = client.post("/api/open/news/articles",
                           json={"title": "测试", "content": "内容"},
                           headers={"X-Access-Key": "totally-fake-key"})
        assert resp.status_code == 401
