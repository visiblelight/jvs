from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.todo import TodoCategory, TodoItem, TodoTag
from app.models.user import User
from app.schemas.todo import (
    CategoryCreate, CategoryItem, CategoryOut, CategoryUpdate,
    TagCreate, TagOut, TagUpdate,
    TodoItemCreate, TodoItemListOut, TodoItemOut, TodoItemUpdate, TodoStatusUpdate,
)
from app.services import todo as todo_svc

router = APIRouter(prefix="/todo", tags=["admin-todo"])


# ── 分类 ──

@router.get("/categories", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return todo_svc.get_category_tree(db, current_user.id)


@router.post("/categories", response_model=CategoryItem, status_code=status.HTTP_201_CREATED)
def create_category(
    body: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.parent_id:
        parent = db.query(TodoCategory).filter(
            TodoCategory.id == body.parent_id, TodoCategory.user_id == current_user.id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父分类不存在")
    cat = todo_svc.create_category(db, current_user.id, body.name, body.parent_id, body.sort_order)
    return cat


@router.put("/categories/{category_id}", response_model=CategoryItem)
def update_category(
    category_id: int,
    body: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = db.query(TodoCategory).filter(
        TodoCategory.id == category_id, TodoCategory.user_id == current_user.id
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    return todo_svc.update_category(db, cat, **body.model_dump(exclude_unset=True))


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = db.query(TodoCategory).filter(
        TodoCategory.id == category_id, TodoCategory.user_id == current_user.id
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    # 检查子分类
    children = db.query(TodoCategory).filter(TodoCategory.parent_id == category_id).count()
    if children > 0:
        raise HTTPException(status_code=400, detail="该分类下存在子分类，无法删除")
    # 检查关联事项
    items = db.query(TodoItem).filter(TodoItem.category_id == category_id).count()
    if items > 0:
        raise HTTPException(status_code=400, detail="该分类下存在事项，无法删除")
    todo_svc.delete_category(db, cat)


# ── 标签 ──

@router.get("/tags", response_model=list[TagOut])
def list_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return todo_svc.get_tags(db, current_user.id)


@router.post("/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(
    body: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return todo_svc.create_tag(db, current_user.id, body.name, body.color)


@router.put("/tags/{tag_id}", response_model=TagOut)
def update_tag(
    tag_id: int,
    body: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = db.query(TodoTag).filter(TodoTag.id == tag_id, TodoTag.user_id == current_user.id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return todo_svc.update_tag(db, tag, **body.model_dump(exclude_unset=True))


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = db.query(TodoTag).filter(TodoTag.id == tag_id, TodoTag.user_id == current_user.id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    todo_svc.delete_tag(db, tag)


# ── 事项 ──

@router.get("/items", response_model=TodoItemListOut)
def list_items(
    status_filter: Optional[str] = Query(None, alias="status"),
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    priority: Optional[int] = None,
    importance: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = todo_svc.get_items(
        db, current_user.id,
        status=status_filter, category_id=category_id, tag_id=tag_id,
        priority=priority, importance=importance,
        page=page, page_size=page_size,
    )
    return TodoItemListOut(items=items, total=total)


@router.post("/items", response_model=TodoItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    body: TodoItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = body.model_dump(exclude={"tag_ids"})
    return todo_svc.create_item(db, current_user.id, tag_ids=body.tag_ids, **data)


@router.get("/items/{item_id}", response_model=TodoItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(TodoItem).filter(TodoItem.id == item_id, TodoItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="事项不存在")
    return item


@router.put("/items/{item_id}", response_model=TodoItemOut)
def update_item(
    item_id: int,
    body: TodoItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(TodoItem).filter(TodoItem.id == item_id, TodoItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="事项不存在")
    data = body.model_dump(exclude={"tag_ids"}, exclude_unset=True)
    return todo_svc.update_item(db, item, tag_ids=body.tag_ids, user_id=current_user.id, **data)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(TodoItem).filter(TodoItem.id == item_id, TodoItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="事项不存在")
    todo_svc.delete_item(db, item)


@router.patch("/items/{item_id}/status", response_model=TodoItemOut)
def update_item_status(
    item_id: int,
    body: TodoStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(TodoItem).filter(TodoItem.id == item_id, TodoItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="事项不存在")
    return todo_svc.update_item(db, item, tag_ids=None, user_id=current_user.id, status=body.status)
