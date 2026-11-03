"""Read-only report of broken ownership links, statuses and unsafe uploaded files.

Run from backend: python -m scripts.audit_integrity [--uploads uploads]
No changes are applied; proposed detach operations retain primary records.
"""
import argparse
import json
from pathlib import Path

from app.core.database import SessionLocal
from app.models.todo import TodoCategory, TodoItem
from app.models.news import NewsArticle
from app.services.images import EXTENSIONS, MAX_IMAGE_SIZE, image_format


def audit_relations(db):
    issues = []
    for model, relations in [(TodoItem, ('category',)), (NewsArticle, ('category','source'))]:
        for item in db.query(model).order_by(model.id):
            for relation in relations:
                value = getattr(item, relation)
                old_id = getattr(item, relation + '_id')
                if old_id is not None and (value is None or value.user_id != item.user_id):
                    issues.append(dict(table=model.__tablename__, id=item.id, field=relation+'_id', old=old_id, proposed=None))
            if isinstance(item, TodoItem):
                for tag in item.tags:
                    if tag.user_id != item.user_id:
                        issues.append(dict(table='todo_item_tags', id=item.id, tag_id=tag.id, proposed='detach'))
                if item.status not in {'pending','paused','completed','archived'}:
                    issues.append(dict(table='todo_items', id=item.id, field='status', old=item.status, proposed='manual_review'))
    categories = {c.id:c for c in db.query(TodoCategory)}
    for item in categories.values():
        seen = {item.id}
        parent_id = item.parent_id
        while parent_id is not None:
            parent = categories.get(parent_id)
            if parent_id in seen or parent is None or parent.user_id != item.user_id:
                issues.append(dict(table='todo_categories', id=item.id, field='parent_id', old=item.parent_id, proposed=None))
                break
            seen.add(parent_id)
            parent_id = parent.parent_id
    return issues


def audit_uploads(root):
    issues = []
    for path in sorted(Path(root).rglob('*')):
        if not path.is_file() or path.name == '.gitkeep':
            continue
        try:
            if path.is_symlink() or path.suffix.lower() not in EXTENSIONS or path.stat().st_size > MAX_IMAGE_SIZE:
                raise ValueError('not an allowed image file')
            ext, _ = image_format(path.read_bytes())
            if path.suffix.lower() not in ('.'+ext, '.jpeg' if ext=='jpg' else '.'+ext):
                raise ValueError('extension mismatch')
        except (ValueError, OSError) as exc:
            issues.append(dict(path=str(path.relative_to(root)), reason=str(exc), proposed='review_and_quarantine'))
    return issues


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--uploads')
    args=parser.parse_args()
    with SessionLocal() as db:
        report={'relations':audit_relations(db)}
    if args.uploads:
        report['uploads']=audit_uploads(args.uploads)
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
