import json
import os
import uuid
from datetime import datetime

DB_FILE = 'database.json'

def init_db():
    if not os.path.exists(DB_FILE):
        save_db({"items": []})

def load_db():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"items": []}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_items(search=None, category=None, sort_by=None, parent_id=None):
    db = load_db()
    items = db.get("items", [])
    
    if search:
        search = search.lower()
        items = [i for i in items if search in i.get('name', '').lower() or search in i.get('note', '').lower() or search in ','.join(i.get('tags', [])).lower()]
    else:
        # Only filter by parent_id if we are not doing a global search
        items = [i for i in items if i.get('parent_id') == parent_id]
        
    if category:
        items = [i for i in items if i.get('category') == category]
        
    if sort_by:
        if sort_by == 'name':
            items.sort(key=lambda x: x.get('name', '').lower())
        elif sort_by == 'date_asc':
            items.sort(key=lambda x: x.get('added_at', ''))
        elif sort_by == 'date_desc':
            items.sort(key=lambda x: x.get('added_at', ''), reverse=True)
        elif sort_by == 'size_asc':
            items.sort(key=lambda x: x.get('size', 0))
        elif sort_by == 'size_desc':
            items.sort(key=lambda x: x.get('size', 0), reverse=True)
            
    return items

def get_item(item_id):
    db = load_db()
    for item in db.get("items", []):
        if item.get("id") == item_id:
            return item
    return None

def add_item(item_data):
    db = load_db()
    
    item = {
        "id": str(uuid.uuid4()),
        "type": item_data.get("type", "file"), # file | url | folder
        "name": item_data.get("name", ""),
        "path": item_data.get("path", ""),
        "category": item_data.get("category", ""),
        "tags": item_data.get("tags", []),
        "added_at": datetime.now().isoformat(),
        "size": item_data.get("size", 0),
        "note": item_data.get("note", ""),
        "parent_id": item_data.get("parent_id")
    }
    
    db.setdefault("items", []).append(item)
    save_db(db)
    return item

def update_item(item_id, item_data):
    db = load_db()
    for item in db.get("items", []):
        if item.get("id") == item_id:
            # Update fields
            for key in ["name", "category", "tags", "note"]:
                if key in item_data:
                    item[key] = item_data[key]
            save_db(db)
            return item
    return None

def delete_item(item_id):
    db = load_db()
    items = db.get("items", [])
    deleted_items = []
    
    def collect_and_delete(target_id):
        nonlocal items
        item = next((i for i in items if i.get("id") == target_id), None)
        if not item: return
        
        if item.get("type") == "folder":
            children = [i.get("id") for i in items if i.get("parent_id") == target_id]
            for child_id in children:
                collect_and_delete(child_id)
                
        items = [i for i in items if i.get("id") != target_id]
        deleted_items.append(item)

    collect_and_delete(item_id)
    
    if deleted_items:
        db["items"] = items
        save_db(db)
        
    return deleted_items

def get_breadcrumb(item_id):
    db = load_db()
    items = db.get("items", [])
    breadcrumb = []
    current_id = item_id
    
    while current_id:
        item = next((i for i in items if i.get("id") == current_id), None)
        if item:
            breadcrumb.insert(0, {"id": item["id"], "name": item["name"]})
            current_id = item.get("parent_id")
        else:
            break
            
    return breadcrumb
