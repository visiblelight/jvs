from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.news import NewsArticle, NewsCategory, NewsSource
from app.models.user import User
from app.schemas.news import (
    NewsArticleCreate, NewsArticleListOut, NewsArticleOut, NewsArticleUpdate,
    NewsCategoryCreate, NewsCategoryOut, NewsCategoryUpdate,
    NewsSourceCreate, NewsSourceOut, NewsSourceUpdate,
)
from app.services import news as news_svc

router = APIRouter(prefix="/news", tags=["admin-news"])


# ── 分类 ──

@router.get("/categories", response_model=list[NewsCategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return news_svc.get_categories(db, current_user.id)


@router.post("/categories", response_model=NewsCategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    body: NewsCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return news_svc.create_category(db, current_user.id, body.name, body.sort_order)


@router.put("/categories/{category_id}", response_model=NewsCategoryOut)
def update_category(
    category_id: int,
    body: NewsCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = db.query(NewsCategory).filter(
        NewsCategory.id == category_id, NewsCategory.user_id == current_user.id
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    return news_svc.update_category(db, cat, **body.model_dump(exclude_unset=True))


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = db.query(NewsCategory).filter(
        NewsCategory.id == category_id, NewsCategory.user_id == current_user.id
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    articles = db.query(NewsArticle).filter(NewsArticle.category_id == category_id).count()
    if articles > 0:
        raise HTTPException(status_code=400, detail="该分类下存在文章，无法删除")
    news_svc.delete_category(db, cat)


# ── 来源 ──

@router.get("/sources", response_model=list[NewsSourceOut])
def list_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return news_svc.get_sources(db, current_user.id)


@router.post("/sources", response_model=NewsSourceOut, status_code=status.HTTP_201_CREATED)
def create_source(
    body: NewsSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return news_svc.create_source(db, current_user.id, body.name)


@router.put("/sources/{source_id}", response_model=NewsSourceOut)
def update_source(
    source_id: int,
    body: NewsSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    src = db.query(NewsSource).filter(
        NewsSource.id == source_id, NewsSource.user_id == current_user.id
    ).first()
    if not src:
        raise HTTPException(status_code=404, detail="来源不存在")
    return news_svc.update_source(db, src, **body.model_dump(exclude_unset=True))


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    src = db.query(NewsSource).filter(
        NewsSource.id == source_id, NewsSource.user_id == current_user.id
    ).first()
    if not src:
        raise HTTPException(status_code=404, detail="来源不存在")
    articles = db.query(NewsArticle).filter(NewsArticle.source_id == source_id).count()
    if articles > 0:
        raise HTTPException(status_code=400, detail="该来源下存在文章，无法删除")
    news_svc.delete_source(db, src)


# ── 文章 ──

@router.get("/articles", response_model=NewsArticleListOut)
def list_articles(
    category_id: Optional[int] = None,
    source_id: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = news_svc.get_articles(
        db, current_user.id,
        category_id=category_id, source_id=source_id, keyword=keyword,
        page=page, page_size=page_size,
    )
    return NewsArticleListOut(items=items, total=total)


@router.post("/articles", response_model=NewsArticleOut, status_code=status.HTTP_201_CREATED)
def create_article(
    body: NewsArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return news_svc.create_article(db, current_user.id, **body.model_dump())


@router.get("/articles/{article_id}", response_model=NewsArticleOut)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = news_svc.get_article(db, article_id, current_user.id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article


@router.put("/articles/{article_id}", response_model=NewsArticleOut)
def update_article(
    article_id: int,
    body: NewsArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = news_svc.get_article(db, article_id, current_user.id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return news_svc.update_article(db, article, **body.model_dump(exclude_unset=True))


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = news_svc.get_article(db, article_id, current_user.id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    news_svc.delete_article(db, article)
