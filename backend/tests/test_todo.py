"""
Todo 模块测试：事项 CRUD、分类、标签、执行时间/截止时间联动、权限隔离
"""
import pytest


# ── 辅助函数 ──────────────────────────────────────────────────────────────────

def create_item(client, headers, **kwargs):
    payload = {"title": "测试事项", "priority": 3, "importance": 3, **kwargs}
    resp = client.post("/api/admin/todo/items", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


def create_category(client, headers, name="默认分类"):
    resp = client.post("/api/admin/todo/categories", json={"name": name}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


def create_tag(client, headers, name="测试标签", color="#ff0000"):
    resp = client.post("/api/admin/todo/tags", json={"name": name, "color": color}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


# ── 分类 ─────────────────────────────────────────────────────────────────────

class TestCategory:
    def test_create_and_list(self, client, auth_headers):
        create_category(client, auth_headers, "工作")
        create_category(client, auth_headers, "生活")
        resp = client.get("/api/admin/todo/categories", headers=auth_headers)
        assert resp.status_code == 200
        names = [c["name"] for c in resp.json()]
        assert "工作" in names
        assert "生活" in names

    def test_create_subcategory(self, client, auth_headers):
        parent = create_category(client, auth_headers, "父分类")
        resp = client.post("/api/admin/todo/categories", json={
            "name": "子分类", "parent_id": parent["id"]
        }, headers=auth_headers)
        assert resp.status_code == 201

    def test_isolation_between_users(self, client, auth_headers, other_auth_headers):
        create_category(client, auth_headers, "用户A的分类")
        resp = client.get("/api/admin/todo/categories", headers=other_auth_headers)
        names = [c["name"] for c in resp.json()]
        assert "用户A的分类" not in names


# ── 标签 ─────────────────────────────────────────────────────────────────────

class TestTag:
    def test_create_and_list(self, client, auth_headers):
        create_tag(client, auth_headers, "紧急", "#ff0000")
        resp = client.get("/api/admin/todo/tags", headers=auth_headers)
        assert resp.status_code == 200
        assert any(t["name"] == "紧急" for t in resp.json())

    def test_update(self, client, auth_headers):
        tag = create_tag(client, auth_headers, "旧名称")
        resp = client.put(f"/api/admin/todo/tags/{tag['id']}", json={"name": "新名称"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "新名称"

    def test_delete(self, client, auth_headers):
        tag = create_tag(client, auth_headers, "待删除")
        resp = client.delete(f"/api/admin/todo/tags/{tag['id']}", headers=auth_headers)
        assert resp.status_code == 204


# ── 事项 CRUD ─────────────────────────────────────────────────────────────────

class TestTodoItem:
    def test_create_minimal(self, client, auth_headers):
        item = create_item(client, auth_headers, title="最简事项")
        assert item["title"] == "最简事项"
        assert item["status"] == "pending"

    def test_create_full(self, client, auth_headers):
        cat = create_category(client, auth_headers)
        tag = create_tag(client, auth_headers)
        item = create_item(
            client, auth_headers,
            title="完整事项",
            description="描述内容",
            priority=5,
            importance=4,
            category_id=cat["id"],
            tag_ids=[tag["id"]],
            due_date="2099-12-31T23:59:00Z",
        )
        assert item["priority"] == 5
        assert item["category_id"] == cat["id"]
        assert item["category_name"] == cat["name"]
        assert any(t["id"] == tag["id"] for t in item["tags"])

    def test_list(self, client, auth_headers):
        create_item(client, auth_headers, title="事项1")
        create_item(client, auth_headers, title="事项2")
        resp = client.get("/api/admin/todo/items", headers=auth_headers)
        assert resp.status_code == 200
        titles = [i["title"] for i in resp.json()["items"]]
        assert "事项1" in titles
        assert "事项2" in titles

    def test_get_single(self, client, auth_headers):
        item = create_item(client, auth_headers, title="单个事项")
        resp = client.get(f"/api/admin/todo/items/{item['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "单个事项"

    def test_update(self, client, auth_headers):
        item = create_item(client, auth_headers, title="原标题")
        resp = client.put(f"/api/admin/todo/items/{item['id']}", json={
            "title": "新标题", "priority": 5
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "新标题"
        assert resp.json()["priority"] == 5

    def test_soft_delete_and_restore(self, client, auth_headers):
        item = create_item(client, auth_headers)
        # 删除
        resp = client.delete(f"/api/admin/todo/items/{item['id']}", headers=auth_headers)
        assert resp.status_code == 204
        # 正常列表不再出现
        resp = client.get("/api/admin/todo/items", headers=auth_headers)
        ids = [i["id"] for i in resp.json()["items"]]
        assert item["id"] not in ids
        # 回收站里出现
        resp = client.get("/api/admin/todo/items?is_deleted=true", headers=auth_headers)
        ids = [i["id"] for i in resp.json()["items"]]
        assert item["id"] in ids
        # 恢复
        resp = client.post(f"/api/admin/todo/items/{item['id']}/restore", headers=auth_headers)
        assert resp.status_code == 200

    def test_status_update(self, client, auth_headers):
        item = create_item(client, auth_headers)
        resp = client.patch(f"/api/admin/todo/items/{item['id']}/status",
                            json={"status": "completed"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"
        assert resp.json()["completed_at"] is not None

    def test_filter_by_category(self, client, auth_headers):
        cat = create_category(client, auth_headers, "过滤分类")
        item_in = create_item(client, auth_headers, title="在分类中", category_id=cat["id"])
        create_item(client, auth_headers, title="不在分类中")
        resp = client.get(f"/api/admin/todo/items?category_id={cat['id']}", headers=auth_headers)
        ids = [i["id"] for i in resp.json()["items"]]
        assert item_in["id"] in ids
        assert len(ids) == 1

    def test_filter_by_tag(self, client, auth_headers):
        tag = create_tag(client, auth_headers, "过滤标签")
        item_with = create_item(client, auth_headers, title="有标签", tag_ids=[tag["id"]])
        create_item(client, auth_headers, title="无标签")
        resp = client.get(f"/api/admin/todo/items?tag_id={tag['id']}", headers=auth_headers)
        ids = [i["id"] for i in resp.json()["items"]]
        assert item_with["id"] in ids
        assert len(ids) == 1


# ── 执行时间 / 截止时间联动 ──────────────────────────────────────────────────────

class TestScheduledAndDueDate:
    def test_set_scheduled_at(self, client, auth_headers):
        item = create_item(client, auth_headers, scheduled_at="2099-06-01T10:00:00Z")
        assert item["scheduled_at"] is not None

    def test_clear_scheduled_at(self, client, auth_headers):
        """关闭执行时间开关后，scheduled_at 应能被清空为 null"""
        item = create_item(client, auth_headers, scheduled_at="2099-06-01T10:00:00Z")
        assert item["scheduled_at"] is not None
        resp = client.put(f"/api/admin/todo/items/{item['id']}", json={
            "scheduled_at": None,
            "due_date": None,
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["scheduled_at"] is None

    def test_scheduled_at_auto_sets_due_date(self, client, auth_headers):
        """前端逻辑：有执行时间时 due_date == scheduled_at"""
        ts = "2099-06-01T10:00:00Z"
        item = create_item(client, auth_headers, scheduled_at=ts, due_date=ts)
        assert item["scheduled_at"] is not None
        assert item["due_date"] is not None

    def test_due_date_independent(self, client, auth_headers):
        """无执行时间时，截止日期可独立设置"""
        item = create_item(client, auth_headers, due_date="2099-12-31T23:59:00Z")
        assert item["due_date"] is not None
        assert item["scheduled_at"] is None


# ── 权限隔离 ──────────────────────────────────────────────────────────────────

class TestIsolation:
    def test_user_cannot_read_others_item(self, client, auth_headers, other_auth_headers):
        item = create_item(client, auth_headers, title="A的私有事项")
        resp = client.get(f"/api/admin/todo/items/{item['id']}", headers=other_auth_headers)
        assert resp.status_code == 404

    def test_user_cannot_update_others_item(self, client, auth_headers, other_auth_headers):
        item = create_item(client, auth_headers)
        resp = client.put(f"/api/admin/todo/items/{item['id']}", json={"title": "篡改"},
                          headers=other_auth_headers)
        assert resp.status_code == 404

    def test_user_cannot_delete_others_item(self, client, auth_headers, other_auth_headers):
        item = create_item(client, auth_headers)
        resp = client.delete(f"/api/admin/todo/items/{item['id']}", headers=other_auth_headers)
        assert resp.status_code == 404

    def test_list_only_shows_own_items(self, client, auth_headers, other_auth_headers):
        create_item(client, auth_headers, title="A的事项")
        create_item(client, other_auth_headers, title="B的事项")
        resp_a = client.get("/api/admin/todo/items", headers=auth_headers)
        resp_b = client.get("/api/admin/todo/items", headers=other_auth_headers)
        titles_a = [i["title"] for i in resp_a.json()["items"]]
        titles_b = [i["title"] for i in resp_b.json()["items"]]
        assert "A的事项" in titles_a and "B的事项" not in titles_a
        assert "B的事项" in titles_b and "A的事项" not in titles_b
