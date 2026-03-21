from fastapi import APIRouter

from app.api.open.news import router as news_router

router = APIRouter(prefix="/api/open")
router.include_router(news_router)
