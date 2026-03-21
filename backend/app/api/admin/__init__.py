from fastapi import APIRouter

from app.api.admin.auth import router as auth_router
from app.api.admin.todo import router as todo_router
from app.api.admin.news import router as news_router
from app.api.admin.access_key import router as access_key_router

router = APIRouter(prefix="/api/admin")
router.include_router(auth_router)
router.include_router(todo_router)
router.include_router(news_router)
router.include_router(access_key_router)
