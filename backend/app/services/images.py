"""Content-validated image uploads and safe serving of legacy upload files."""
import io
import os
from pathlib import Path
import uuid
import warnings
from functools import lru_cache

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

FORMATS = {"JPEG": ("jpg", "image/jpeg"), "PNG": ("png", "image/png"),
           "GIF": ("gif", "image/gif"), "WEBP": ("webp", "image/webp")}
EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_PIXELS = 20_000_000
MAX_TOTAL_PIXELS = 40_000_000
MAX_FRAMES = 200
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def image_format(contents: bytes) -> tuple[str, str]:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(contents)) as image:
                fmt = image.format
                if fmt not in FORMATS or image.width * image.height > MAX_PIXELS:
                    raise ValueError("图片格式或像素大小不支持")
                image.verify()
            # verify() is not a full decoder for every format, especially animated files.
            with Image.open(io.BytesIO(contents)) as image:
                total = 0
                frame = 0
                while True:
                    total += image.width * image.height
                    frame += 1
                    if frame > MAX_FRAMES or total > MAX_TOTAL_PIXELS:
                        raise ValueError("图片帧数或总像素超过限制")
                    image.load()
                    try:
                        image.seek(frame)
                    except EOFError:
                        break
        return FORMATS[fmt]
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError("图片损坏、格式不支持或超过像素限制") from exc


async def read_image(file: UploadFile, max_size: int):
    contents = await file.read(max_size + 1)
    if len(contents) > max_size:
        raise HTTPException(status_code=400, detail=f"图片大小不能超过 {max_size // 1024 // 1024}MB")
    try:
        ext, mime = await run_in_threadpool(image_format, contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if file.content_type != mime:
        raise HTTPException(status_code=400, detail="文件声明类型与实际图片格式不一致")
    return contents, ext


def write_image(directory, contents, ext, prefix="") -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{prefix}{uuid.uuid4().hex}.{ext}"
    temp = target.with_suffix(".tmp")
    try:
        temp.write_bytes(contents)
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)
    return target


@lru_cache(maxsize=512)
def _checked_file(path, mtime_ns, size, inode):
    if size > MAX_IMAGE_SIZE:
        raise ValueError("图片太大")
    ext, mime = image_format(Path(path).read_bytes())
    suffix = Path(path).suffix.lower().lstrip(".")
    if suffix != ext and not (ext == "jpg" and suffix == "jpeg"):
        raise ValueError("文件扩展名与内容不一致")
    return mime


class ImageStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        if Path(path).suffix.lower() not in EXTENSIONS:
            raise StarletteHTTPException(status_code=404)
        full_path, stat = await run_in_threadpool(self.lookup_path, path)
        if stat is None:
            raise StarletteHTTPException(status_code=404)
        try:
            mime = await run_in_threadpool(_checked_file, full_path, stat.st_mtime_ns, stat.st_size, stat.st_ino)
        except (ValueError, OSError):
            raise StarletteHTTPException(status_code=404)
        response = await super().get_response(path, scope)
        response.headers["Content-Type"] = mime
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'none'; sandbox"
        return response
