import os
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status

from app.core.deps import get_current_user
from app.models.user import User
from app.services.images import read_image, write_image

router = APIRouter(prefix="/uploads", tags=["admin-uploads"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/images", status_code=status.HTTP_201_CREATED)
async def upload_image(
    module: str = Query(default="general", description="所属模块，如 todo / news / general"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    contents, ext = await read_image(file, MAX_SIZE)
    safe_module = "".join(c for c in module if c.isascii() and (c.isalnum() or c == "-"))[:64] or "general"
    target = write_image(os.path.join("uploads", safe_module), contents, ext)
    return {"url": f"/uploads/{safe_module}/{target.name}"}
