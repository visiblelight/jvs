from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.todo import TodoCategory, TodoItem, TodoTag, todo_item_tags


# ── 分类 ──

def get_category_tree(db: Session, user_id: int) -> list[dict]:
    categories = (
        db.query(TodoCategory)
        .filter(TodoCategory.user_id == user_id)
        .order_by(TodoCategory.sort_order)
        .all()
    )
    lookup: dict[int, dict] = {}
    for cat in categories:
        lookup[cat.id] = {
            "id": cat.id,
            "parent_id": cat.parent_id,
            "name": cat.name,
            "sort_order": cat.sort_order,
            "children": [],
        }
    roots = []
    for cat in categories:
        node = lookup[cat.id]
        if cat.parent_id and cat.parent_id in lookup:
            lookup[cat.parent_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


def create_category(db: Session, user_id: int, name: str, parent_id: Optional[int], sort_order: int) -> TodoCategory:
    cat = TodoCategory(user_id=user_id, name=name, parent_id=parent_id, sort_order=sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, category: TodoCategory, **kwargs) -> TodoCategory:
    for k, v in kwargs.items():
        if v is not None:
            setattr(category, k, v)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: TodoCategory) -> None:
    db.delete(category)
    db.commit()


# ── 标签 ──

def get_tags(db: Session, user_id: int) -> list[TodoTag]:
    return db.query(TodoTag).filter(TodoTag.user_id == user_id).order_by(TodoTag.id).all()


def create_tag(db: Session, user_id: int, name: str, color: str) -> TodoTag:
    tag = TodoTag(user_id=user_id, name=name, color=color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def update_tag(db: Session, tag: TodoTag, **kwargs) -> TodoTag:
    for k, v in kwargs.items():
        if v is not None:
            setattr(tag, k, v)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag: TodoTag) -> None:
    db.delete(tag)
    db.commit()


# ── 事项 ──

from sqlalchemy import or_

def get_items(
    db: Session,
    user_id: int,
    search: Optional[str] = None,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    priority: Optional[int] = None,
    importance: Optional[int] = None,
    is_deleted: bool = False,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[TodoItem], int]:
    query = db.query(TodoItem).filter(TodoItem.user_id == user_id, TodoItem.is_deleted == is_deleted)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(or_(
            TodoItem.title.ilike(search_pattern),
            TodoItem.description.ilike(search_pattern)
        ))

    if status:
        query = query.filter(TodoItem.status == status)
    if category_id is not None:
        query = query.filter(TodoItem.category_id == category_id)
    if tag_id is not None:
        query = query.filter(TodoItem.tags.any(TodoTag.id == tag_id))
    if priority is not None:
        query = query.filter(TodoItem.priority == priority)
    if importance is not None:
        query = query.filter(TodoItem.importance == importance)

    total = query.count()
    items = (
        query.order_by(TodoItem.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def create_item(db: Session, user_id: int, tag_ids: list[int], **kwargs) -> TodoItem:
    item = TodoItem(user_id=user_id, **kwargs)
    if tag_ids:
        tags = db.query(TodoTag).filter(TodoTag.id.in_(tag_ids), TodoTag.user_id == user_id).all()
        item.tags = tags
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item: TodoItem, tag_ids: Optional[list[int]], user_id: int, **kwargs) -> TodoItem:
    for k, v in kwargs.items():
        if v is not None:
            setattr(item, k, v)
    if tag_ids is not None:
        tags = db.query(TodoTag).filter(TodoTag.id.in_(tag_ids), TodoTag.user_id == user_id).all()
        item.tags = tags
    # 自动设置完成时间
    if kwargs.get("status") == "completed" and item.completed_at is None:
        item.completed_at = datetime.now(timezone.utc)
    elif kwargs.get("status") and kwargs["status"] != "completed":
        item.completed_at = None
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: TodoItem) -> None:
    item.is_deleted = True
    item.deleted_at = datetime.now(timezone.utc)
    db.commit()


def restore_item(db: Session, item: TodoItem) -> None:
    item.is_deleted = False
    item.deleted_at = None
    db.commit()


def hard_delete_item(db: Session, item: TodoItem) -> None:
    db.delete(item)
    db.commit()
