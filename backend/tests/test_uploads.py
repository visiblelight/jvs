"""
图片上传测试：类型校验、大小校验、正常上传
用 monkeypatch.chdir 将工作目录切到临时目录，uploads/ 会写到临时目录里，测试结束自动清理。
"""
import io
import pytest


def make_image_file(content=b"fake-image-data", filename="test.png", content_type="image/png"):
    return ("file", (filename, io.BytesIO(content), content_type))


@pytest.fixture(autouse=True)
def use_tmp_uploads(monkeypatch, tmp_path):
    """把工作目录切到临时目录，uploads/ 相对路径写入临时位置"""
    monkeypatch.chdir(tmp_path)


class TestUploads:
    def test_upload_png(self, client, auth_headers):
        resp = client.post(
            "/api/admin/uploads/images?module=todo",
            files=[make_image_file()],
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert "url" in resp.json()
        assert resp.json()["url"].startswith("/uploads/todo/")

    def test_upload_jpeg(self, client, auth_headers):
        resp = client.post(
            "/api/admin/uploads/images?module=news",
            files=[make_image_file(filename="photo.jpg", content_type="image/jpeg")],
            headers=auth_headers,
        )
        assert resp.status_code == 201

    def test_reject_non_image(self, client, auth_headers):
        resp = client.post(
            "/api/admin/uploads/images",
            files=[make_image_file(filename="evil.pdf", content_type="application/pdf")],
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_reject_oversized_file(self, client, auth_headers):
        big_content = b"x" * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte
        resp = client.post(
            "/api/admin/uploads/images",
            files=[make_image_file(content=big_content)],
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_module_name_sanitized(self, client, auth_headers):
        """路径穿越攻击：模块名含 ../ 应被净化"""
        resp = client.post(
            "/api/admin/uploads/images?module=../../etc",
            files=[make_image_file()],
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert "../" not in resp.json()["url"]

    def test_require_auth(self, client):
        resp = client.post(
            "/api/admin/uploads/images",
            files=[make_image_file()],
        )
        assert resp.status_code == 401
