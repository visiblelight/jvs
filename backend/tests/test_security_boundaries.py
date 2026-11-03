import io
from pathlib import Path

from PIL import Image
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models.news import NewsArticle, NewsCategory
from app.models.todo import TodoItem, TodoCategory, TodoTag
from app.services.images import ImageStaticFiles


@pytest.mark.parametrize("module,collection,payload,relation", [
    ("todo", "items", {"title": "item"}, "categories"),
    ("news", "articles", {"title": "article", "content": "body"}, "categories"),
    ("news", "articles", {"title": "article", "content": "body"}, "sources"),
])
def test_foreign_relation_rejected_atomically(client, auth_headers, other_auth_headers, module, collection, payload, relation):
    other = client.post(f"/api/admin/{module}/{relation}", headers=other_auth_headers, json={"name": "private"}).json()
    field = "source_id" if relation == "sources" else "category_id"
    base = f"/api/admin/{module}/{collection}"
    assert client.post(base, headers=auth_headers, json={**payload, field: other["id"]}).status_code == 404
    item = client.post(base, headers=auth_headers, json=payload).json()
    assert client.put(f"{base}/{item['id']}", headers=auth_headers, json={"title": "changed", field: other["id"]}).status_code == 404
    assert client.get(f"{base}/{item['id']}", headers=auth_headers).json()["title"] == payload["title"]


def test_tags_and_category_cycles(client, auth_headers, other_auth_headers):
    foreign = client.post('/api/admin/todo/tags', headers=other_auth_headers, json={"name": "foreign"}).json()
    assert client.post('/api/admin/todo/items', headers=auth_headers, json={"title": "x", "tag_ids": [foreign['id']]}).status_code == 404
    root = client.post('/api/admin/todo/categories', headers=auth_headers, json={"name": "root"}).json()
    child = client.post('/api/admin/todo/categories', headers=auth_headers, json={"name": "child", "parent_id": root['id']}).json()
    base='/api/admin/todo/categories'
    assert client.put(f"{base}/{root['id']}", headers=auth_headers, json={"parent_id": child['id']}).status_code == 400
    assert client.put(f"{base}/{child['id']}", headers=auth_headers, json={"parent_id": child['id']}).status_code == 400
    assert client.put(f"{base}/{child['id']}", headers=auth_headers, json={"parent_id": None}).json()['parent_id'] is None


def test_legacy_foreign_relations_hidden(client, db, test_user, other_user, auth_headers):
    cat = TodoCategory(user_id=other_user.id, name="private todo")
    news_cat = NewsCategory(user_id=other_user.id, name="private news")
    tag = TodoTag(user_id=other_user.id, name="private tag")
    db.add_all([cat, news_cat, tag]); db.flush()
    item = TodoItem(user_id=test_user.id, title="own", category_id=cat.id, tags=[tag])
    article = NewsArticle(user_id=test_user.id, title="own", content="own", category_id=news_cat.id)
    db.add_all([item, article]); db.commit()
    data = client.get(f'/api/admin/todo/items/{item.id}', headers=auth_headers).json()
    assert data['category_name'] is None and data['category_id'] is None and data['tags'] == []
    data = client.get(f'/api/admin/news/articles/{article.id}', headers=auth_headers).json()
    assert data['category'] is None and data['category_id'] is None
    assert db.get(TodoItem, item.id).category_id == cat.id  # serialization must not mutate the DB


def test_nullable_news_fields(client, auth_headers):
    article = client.post('/api/admin/news/articles', headers=auth_headers, json={"title":"x", "content":"x", "summary":"old"}).json()
    url=f"/api/admin/news/articles/{article['id']}"
    assert client.put(url, headers=auth_headers, json={"summary": None}).json()['summary'] is None
    assert client.put(url, headers=auth_headers, json={"title": None}).status_code == 422


def image_bytes(fmt):
    buf = io.BytesIO()
    Image.new("RGB", (3, 3), "red").save(buf, format=fmt)
    return buf.getvalue()


@pytest.mark.parametrize('fmt,mime,ext', [('PNG','image/png','png'),('JPEG','image/jpeg','jpg'),('GIF','image/gif','gif'),('WEBP','image/webp','webp')])
def test_valid_upload_content_sets_extension(client, auth_headers, monkeypatch, tmp_path, fmt, mime, ext):
    monkeypatch.chdir(tmp_path)
    r=client.post('/api/admin/uploads/images', headers=auth_headers, files={'file':('wrong.html',image_bytes(fmt),mime)})
    assert r.status_code == 201
    assert r.json()['url'].endswith('.'+ext)


def test_avatar_validation_and_legacy_serving(client, auth_headers, monkeypatch, tmp_path):
    from app.api.admin import auth
    monkeypatch.setattr(auth, 'AVATARS_DIR', str(tmp_path))
    ok=client.post('/api/admin/auth/avatar', headers=auth_headers, files={'file':('a.png',image_bytes('PNG'),'image/png')})
    assert ok.status_code == 200
    old=tmp_path / ok.json()['avatar']
    assert old.is_file()
    for contents, mime in [(b'<html>test</html>', 'image/png'), (image_bytes('PNG'),'image/jpeg'), (b'bad','image/png')]:
        r=client.post('/api/admin/auth/avatar', headers=auth_headers, files={'file':('a.html',contents,mime)})
        assert r.status_code == 400
        assert old.is_file()
    (tmp_path/'legacy.html').write_text('<html>test</html>')
    (tmp_path/'legacy.png').write_text('<html>test</html>')
    app=FastAPI(); app.mount('/uploads', ImageStaticFiles(directory=tmp_path))
    with TestClient(app) as static:
        assert static.get('/uploads/legacy.html').status_code == 404
        assert static.get('/uploads/legacy.png').status_code == 404
        r=static.get('/uploads/'+old.name)
        assert r.status_code == 200
        assert r.headers['content-type'] == 'image/png'
        assert r.headers['x-content-type-options'] == 'nosniff'


def test_failed_avatar_commit_keeps_old(client, auth_headers, db, monkeypatch, tmp_path):
    from app.api.admin import auth
    monkeypatch.setattr(auth, 'AVATARS_DIR', str(tmp_path))
    old=client.post('/api/admin/auth/avatar', headers=auth_headers, files={'file':('a.png',image_bytes('PNG'),'image/png')}).json()['avatar']
    def fail():
        raise RuntimeError('simulated commit failure')
    monkeypatch.setattr(db, 'commit', fail)
    with pytest.raises(RuntimeError, match='simulated'):
        client.post('/api/admin/auth/avatar', headers=auth_headers, files={'file':('a.png',image_bytes('PNG'),'image/png')})
    assert [p.name for p in tmp_path.iterdir()] == [old]


def test_image_resource_limits_and_missing_filename(client, auth_headers, monkeypatch, tmp_path):
    from app.services import images
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(images, 'MAX_PIXELS', 8)
    r = client.post('/api/admin/uploads/images', headers=auth_headers,
                    files={'file': ('a.png', image_bytes('PNG'), 'image/png')})
    assert r.status_code == 400
    r = client.post('/api/admin/uploads/images', headers=auth_headers,
                    files={'file': ('', image_bytes('PNG'), 'image/png')})
    assert r.status_code == 422
    assert not (tmp_path / 'uploads').exists()
