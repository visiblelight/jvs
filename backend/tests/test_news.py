"""
News 模块测试：文章 CRUD、分类、来源、权限隔离
"""


def create_article(client, headers, **kwargs):
    payload = {
        "title": "测试文章",
        "content": "# 正文\n这是内容。",
        **kwargs,
    }
    resp = client.post("/api/admin/news/articles", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


def create_category(client, headers, name="测试分类"):
    resp = client.post("/api/admin/news/categories", json={"name": name}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


def create_source(client, headers, name="测试来源"):
    resp = client.post("/api/admin/news/sources", json={"name": name}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


# ── 分类 & 来源 ───────────────────────────────────────────────────────────────

class TestNewsCategory:
    def test_create_and_list(self, client, auth_headers):
        create_category(client, auth_headers, "科技")
        resp = client.get("/api/admin/news/categories", headers=auth_headers)
        assert any(c["name"] == "科技" for c in resp.json())

    def test_update(self, client, auth_headers):
        cat = create_category(client, auth_headers, "旧分类")
        resp = client.put(f"/api/admin/news/categories/{cat['id']}", json={"name": "新分类"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "新分类"

    def test_delete(self, client, auth_headers):
        cat = create_category(client, auth_headers, "待删除")
        resp = client.delete(f"/api/admin/news/categories/{cat['id']}", headers=auth_headers)
        assert resp.status_code == 204


class TestNewsSource:
    def test_create_and_list(self, client, auth_headers):
        create_source(client, auth_headers, "新华社")
        resp = client.get("/api/admin/news/sources", headers=auth_headers)
        assert any(s["name"] == "新华社" for s in resp.json())


# ── 文章 CRUD ─────────────────────────────────────────────────────────────────

class TestNewsArticle:
    def test_create_minimal(self, client, auth_headers):
        article = create_article(client, auth_headers)
        assert article["title"] == "测试文章"

    def test_create_with_category_and_source(self, client, auth_headers):
        cat = create_category(client, auth_headers)
        src = create_source(client, auth_headers)
        article = create_article(client, auth_headers,
                                 category_id=cat["id"], source_id=src["id"],
                                 author="记者甲", summary="简短摘要")
        assert article["category_id"] == cat["id"]
        assert article["source_id"] == src["id"]
        assert article["author"] == "记者甲"

    def test_list(self, client, auth_headers):
        create_article(client, auth_headers, title="文章A")
        create_article(client, auth_headers, title="文章B")
        resp = client.get("/api/admin/news/articles", headers=auth_headers)
        assert resp.status_code == 200
        titles = [a["title"] for a in resp.json()["items"]]
        assert "文章A" in titles
        assert "文章B" in titles

    def test_get_single(self, client, auth_headers):
        article = create_article(client, auth_headers, title="单篇文章")
        resp = client.get(f"/api/admin/news/articles/{article['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "单篇文章"

    def test_update(self, client, auth_headers):
        article = create_article(client, auth_headers, title="原标题")
        resp = client.put(f"/api/admin/news/articles/{article['id']}",
                          json={"title": "新标题", "content": "新内容"},
                          headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "新标题"

    def test_delete(self, client, auth_headers):
        article = create_article(client, auth_headers)
        resp = client.delete(f"/api/admin/news/articles/{article['id']}", headers=auth_headers)
        assert resp.status_code == 204
        resp = client.get(f"/api/admin/news/articles/{article['id']}", headers=auth_headers)
        assert resp.status_code == 404


# ── 权限隔离 ──────────────────────────────────────────────────────────────────

class TestNewsIsolation:
    def test_cannot_read_others_article(self, client, auth_headers, other_auth_headers):
        article = create_article(client, auth_headers, title="A的私有文章")
        resp = client.get(f"/api/admin/news/articles/{article['id']}", headers=other_auth_headers)
        assert resp.status_code == 404

    def test_list_only_shows_own_articles(self, client, auth_headers, other_auth_headers):
        create_article(client, auth_headers, title="A的文章")
        create_article(client, other_auth_headers, title="B的文章")
        resp_a = client.get("/api/admin/news/articles", headers=auth_headers)
        titles_a = [a["title"] for a in resp_a.json()["items"]]
        assert "A的文章" in titles_a and "B的文章" not in titles_a
