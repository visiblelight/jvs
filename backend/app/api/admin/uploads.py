import os
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status

from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["admin-uploads"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/images", status_code=status.HTTP_201_CREATED)
async def upload_image(
    module: str = Query(default="general", description="所属模块，如 todo / news / general"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型 {file.content_type}，仅允许 jpg/png/gif/webp",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")

    # 限制 module 名只含字母数字和横线，防止路径穿越
    safe_module = "".join(c for c in module if c.isalnum() or c == "-") or "general"

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        ext = ".png"

    dest_dir = os.path.join("uploads", safe_module)
    os.makedirs(dest_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}{ext}"
    dest_path = os.path.join(dest_dir, filename)

    with open(dest_path, "wb") as f:
        f.write(contents)

    return {"url": f"/uploads/{safe_module}/{filename}"}
