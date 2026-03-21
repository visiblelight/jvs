from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.scopes import require_scope
from app.models.user import User
from app.schemas.news import NewsArticleOut, OpenNewsArticleCreate
from app.services import news as news_svc

router = APIRouter(prefix="/news", tags=["open-news"])


@router.post("/articles", response_model=NewsArticleOut, status_code=status.HTTP_201_CREATED)
def submit_article(
    body: OpenNewsArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_scope("news:create")),
):
    source_id = None
    category_id = None

    if body.source_name:
        src = news_svc.get_or_create_source(db, current_user.id, body.source_name)
        source_id = src.id

    if body.category_name:
        cat = news_svc.get_or_create_category(db, current_user.id, body.category_name)
        category_id = cat.id

    article = news_svc.create_article(
        db, current_user.id,
        title=body.title,
        summary=body.summary,
        content=body.content,
        source_url=body.source_url,
        source_id=source_id,
        author=body.author,
        published_at=body.published_at,
        category_id=category_id,
    )
    return article
