from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.news import NewsArticle, NewsCategory, NewsSource


# ── 分类 ──

def get_categories(db: Session, user_id: int) -> list[NewsCategory]:
    return (
        db.query(NewsCategory)
        .filter(NewsCategory.user_id == user_id)
        .order_by(NewsCategory.sort_order, NewsCategory.id)
        .all()
    )


def create_category(db: Session, user_id: int, name: str, sort_order: int = 0) -> NewsCategory:
    cat = NewsCategory(user_id=user_id, name=name, sort_order=sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, category: NewsCategory, **kwargs) -> NewsCategory:
    for k, v in kwargs.items():
        if v is not None:
            setattr(category, k, v)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: NewsCategory) -> None:
    db.delete(category)
    db.commit()


# ── 来源 ──

def get_sources(db: Session, user_id: int) -> list[NewsSource]:
    return (
        db.query(NewsSource)
        .filter(NewsSource.user_id == user_id)
        .order_by(NewsSource.id)
        .all()
    )


def create_source(db: Session, user_id: int, name: str) -> NewsSource:
    src = NewsSource(user_id=user_id, name=name)
    db.add(src)
    db.commit()
    db.refresh(src)
    return src


def update_source(db: Session, source: NewsSource, **kwargs) -> NewsSource:
    for k, v in kwargs.items():
        if v is not None:
            setattr(source, k, v)
    db.commit()
    db.refresh(source)
    return source


def delete_source(db: Session, source: NewsSource) -> None:
    db.delete(source)
    db.commit()


# ── 文章 ──

def get_articles(
    db: Session,
    user_id: int,
    category_id: Optional[int] = None,
    source_id: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[NewsArticle], int]:
    query = db.query(NewsArticle).filter(NewsArticle.user_id == user_id)

    if category_id is not None:
        query = query.filter(NewsArticle.category_id == category_id)
    if source_id is not None:
        query = query.filter(NewsArticle.source_id == source_id)
    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                NewsArticle.title.ilike(like_pattern),
                NewsArticle.summary.ilike(like_pattern),
                NewsArticle.content.ilike(like_pattern),
                NewsArticle.author.ilike(like_pattern),
            )
        )

    total = query.count()
    items = (
        query.order_by(NewsArticle.published_at.desc().nullslast(), NewsArticle.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def create_article(db: Session, user_id: int, **kwargs) -> NewsArticle:
    article = NewsArticle(user_id=user_id, **kwargs)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int, user_id: int) -> Optional[NewsArticle]:
    return (
        db.query(NewsArticle)
        .filter(NewsArticle.id == article_id, NewsArticle.user_id == user_id)
        .first()
    )


def update_article(db: Session, article: NewsArticle, **kwargs) -> NewsArticle:
    for k, v in kwargs.items():
        if v is not None:
            setattr(article, k, v)
    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article: NewsArticle) -> None:
    db.delete(article)
    db.commit()


# ── 开放 API 辅助 ──

def get_or_create_source(db: Session, user_id: int, name: str) -> NewsSource:
    src = db.query(NewsSource).filter(
        NewsSource.user_id == user_id, NewsSource.name == name
    ).first()
    if not src:
        src = NewsSource(user_id=user_id, name=name)
        db.add(src)
        db.flush()
    return src


def get_or_create_category(db: Session, user_id: int, name: str) -> NewsCategory:
    cat = db.query(NewsCategory).filter(
        NewsCategory.user_id == user_id, NewsCategory.name == name
    ).first()
    if not cat:
        cat = NewsCategory(user_id=user_id, name=name)
        db.add(cat)
        db.flush()
    return cat
