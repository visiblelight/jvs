from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.ownership import owned, owned_many

from app.models.todo import TodoCategory, TodoComment, TodoItem, TodoTag, todo_item_tags


# ── 分类 ──

def get_category_tree(db: Session, user_id: int) -> list[dict]:
    categories = (
        db.query(TodoCategory)
        .filter(TodoCategory.user_id == user_id)
        .order_by(TodoCategory.sort_order)
        .all()
    )
    lookup: dict[int, dict] = {}
    category_ids = {cat.id for cat in categories}
    for cat in categories:
        lookup[cat.id] = {
            "id": cat.id,
            "parent_id": cat.parent_id if cat.parent_id in category_ids else None,
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
    owned(db, TodoCategory, parent_id, user_id, "父分类")
    cat = TodoCategory(user_id=user_id, name=name, parent_id=parent_id, sort_order=sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, category: TodoCategory, **kwargs) -> TodoCategory:
    parent_id = kwargs.get("parent_id")
    seen = {category.id}
    while parent_id is not None:
        if parent_id in seen:
            raise HTTPException(status_code=400, detail="分类不能循环引用")
        seen.add(parent_id)
        parent = owned(db, TodoCategory, parent_id, category.user_id, "父分类")
        parent_id = parent.parent_id
    for k, v in kwargs.items():
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

TRANSITIONS = {
    "pending": {"pending", "paused", "completed"},
    "paused": {"pending", "paused", "completed"},
    "completed": {"pending", "paused", "completed", "archived"},
    "archived": {"archived", "completed"},
}


def get_item(db: Session, item_id: int, user_id: int, include_deleted=False) -> TodoItem:
    query = db.query(TodoItem).filter(
        TodoItem.id == item_id, TodoItem.user_id == user_id, TodoItem.purged_at.is_(None)
    )
    if not include_deleted:
        query = query.filter(TodoItem.is_deleted.is_(False))
    item = query.first()
    if item is None:
        raise HTTPException(status_code=404, detail="事项不存在")
    return item


def require_editable(item):
    if item.purged_at is not None or item.is_deleted:
        raise HTTPException(status_code=404, detail="事项不存在")


from sqlalchemy import and_, or_

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
    query = db.query(TodoItem).filter(
        TodoItem.user_id == user_id,
        TodoItem.is_deleted == is_deleted,
        TodoItem.purged_at == None,
    )

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(or_(
            TodoItem.title.ilike(search_pattern),
            TodoItem.description.ilike(search_pattern)
        ))

    if status:
        query = query.filter(TodoItem.status == status)
    elif not is_deleted:
        # 默认不显示归档事项
        query = query.filter(TodoItem.status != "archived")
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
    owned(db, TodoCategory, kwargs.get("category_id"), user_id, "分类")
    tags = owned_many(db, TodoTag, tag_ids, user_id, "标签")
    item = TodoItem(user_id=user_id, **kwargs)
    item.tags = tags
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item: TodoItem, tag_ids: Optional[list[int]], user_id: int, **kwargs) -> TodoItem:
    require_editable(item)
    old_status = item.status
    new_status = kwargs.get("status", old_status)
    if "status" in kwargs and new_status not in TRANSITIONS.get(old_status, set()):
        raise HTTPException(status_code=400, detail="不允许该状态转换；仅已完成事项可归档，归档事项需先取消归档")
    if "category_id" in kwargs:
        owned(db, TodoCategory, kwargs["category_id"], user_id, "分类")
    tags = owned_many(db, TodoTag, tag_ids, user_id, "标签") if tag_ids is not None else None
    for k, v in kwargs.items():
        setattr(item, k, v)
    if tag_ids is not None:
        item.tags = tags
    if new_status != old_status:
        now = datetime.now(timezone.utc)
        if new_status == "completed" and item.completed_at is None:
            item.completed_at = now
        elif new_status in ("pending", "paused"):
            item.completed_at = None
        item.archived_at = now if new_status == "archived" else None
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: TodoItem) -> None:
    if item.purged_at is not None:
        raise HTTPException(status_code=404, detail="事项不存在")
    if not item.is_deleted:
        item.is_deleted = True
        item.deleted_at = datetime.now(timezone.utc)
    db.commit()


def restore_item(db: Session, item: TodoItem) -> None:
    if item.purged_at is not None:
        raise HTTPException(status_code=404, detail="事项不存在")
    if not item.is_deleted:
        raise HTTPException(status_code=400, detail="事项不在回收站中")
    item.is_deleted = False
    item.deleted_at = None
    db.commit()


def hard_delete_item(db: Session, item: TodoItem) -> None:
    if item.purged_at is not None:
        raise HTTPException(status_code=404, detail="事项不存在")
    if not item.is_deleted and item.status != "archived":
        raise HTTPException(status_code=400, detail="仅回收站或归档事项可永久删除")
    item.purged_at = datetime.now(timezone.utc)
    db.commit()


# ── 评论 ──

def get_comments(db: Session, item_id: int, user_id: int) -> list[TodoComment]:
    return (
        db.query(TodoComment)
        .filter(
            TodoComment.todo_item_id == item_id,
            TodoComment.user_id == user_id,
            TodoComment.deleted_at == None,
        )
        .order_by(TodoComment.created_at.asc())
        .all()
    )


def create_comment(db: Session, item_id: int, user_id: int, content: str) -> TodoComment:
    get_item(db, item_id, user_id)
    now = datetime.now(timezone.utc)
    comment = TodoComment(
        todo_item_id=item_id, user_id=user_id, content=content,
        created_at=now, updated_at=now,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def update_comment(db: Session, comment: TodoComment, content: str) -> TodoComment:
    get_item(db, comment.todo_item_id, comment.user_id)
    comment.content = content
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment: TodoComment) -> None:
    get_item(db, comment.todo_item_id, comment.user_id)
    comment.deleted_at = datetime.now(timezone.utc)
    db.commit()


def get_calendar_items(
    db: Session,
    user_id: int,
    start: datetime,
    end: datetime,
) -> list[TodoItem]:
    return (
        db.query(TodoItem)
        .filter(
            TodoItem.user_id == user_id,
            TodoItem.is_deleted == False,
            TodoItem.purged_at == None,
            or_(
                and_(TodoItem.due_date != None, TodoItem.due_date >= start, TodoItem.due_date < end),
                and_(TodoItem.scheduled_at != None, TodoItem.scheduled_at >= start, TodoItem.scheduled_at < end),
            ),
        )
        .order_by(TodoItem.scheduled_at, TodoItem.due_date)
        .all()
    )
