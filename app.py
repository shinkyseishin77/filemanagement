import os
import json
from flask import Flask, request, jsonify, render_template, redirect, send_from_directory
import storage

app = Flask(__name__)

config = storage.config
app.secret_key = config.get("secret_key", "default_secret_key")
STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__name__)), config.get("storage_dir", "storage"))
os.makedirs(STORAGE_DIR, exist_ok=True)

# Initialize JSON DB
storage.init_db()

def check_auth(item_id):
    if storage.is_in_private_folder(item_id):
        pwd = request.headers.get('X-Private-Password') or request.args.get('pwd')
        if pwd != config.get("private_folder_password", "admin"):
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/api/items', methods=['GET'])
def get_items():
    search = request.args.get('search')
    category = request.args.get('category')
    sort_by = request.args.get('sort')
    parent_id = request.args.get('parent_id')
    
    if parent_id in ('null', '', 'None'):
        parent_id = None
        
    if not check_auth(parent_id):
        return jsonify({"error": "Unauthorized", "locked": True}), 403
        
    items = storage.get_items(search, category, sort_by, parent_id)
    
    # Mark the private folder if not authenticated
    for item in items:
        if item.get("is_private"):
            pwd = request.headers.get('X-Private-Password') or request.args.get('pwd')
            item["is_locked"] = (pwd != config.get("private_folder_password", "admin"))
            
    return jsonify(items)

@app.route('/api/breadcrumb/<item_id>', methods=['GET'])
def get_breadcrumb(item_id):
    if item_id in ('null', '', 'None'):
        return jsonify([])
    if not check_auth(item_id):
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(storage.get_breadcrumb(item_id))

@app.route('/api/items', methods=['POST'])
def add_item_url_folder():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid payload"}), 400
        
    parent_id = data.get("parent_id")
    if parent_id in ('null', '', 'None'):
        parent_id = None

    if not check_auth(parent_id):
        return jsonify({"error": "Unauthorized"}), 403

    item = storage.add_item({
        "type": data.get("type", "url"),
        "name": data.get("name", "Untitled"),
        "path": data.get("url", ""),
        "category": data.get("category", ""),
        "tags": data.get("tags", []),
        "note": data.get("note", ""),
        "parent_id": parent_id,
        "is_private": data.get("is_private", False)
    })
    return jsonify(item), 201

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    files = request.files.getlist('file')
    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "No selected files"}), 400
        
    category = request.form.get('category', '')
    note = request.form.get('note', '')
    parent_id = request.form.get('parent_id')
    if parent_id in ('null', '', 'None'):
        parent_id = None
        
    if not check_auth(parent_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    uploaded_items = []
    
    for file in files:
        if file.filename == '':
            continue
            
        filename = file.filename
        save_path = os.path.join(STORAGE_DIR, filename)
        
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(save_path):
            filename = f"{base}_{counter}{ext}"
            save_path = os.path.join(STORAGE_DIR, filename)
            counter += 1
            
        file.save(save_path)
        file_size = os.path.getsize(save_path)
        
        item = storage.add_item({
            "type": "file",
            "name": filename,
            "path": save_path,
            "category": category,
            "size": file_size,
            "note": note,
            "parent_id": parent_id,
            "is_private": False
        })
        uploaded_items.append(item)
        
    return jsonify({"success": True, "items": uploaded_items}), 201

@app.route('/api/items/<item_id>', methods=['PUT'])
def update_item(item_id):
    if not check_auth(item_id):
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    updated_item = storage.update_item(item_id, data)
    if updated_item:
        return jsonify(updated_item)
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/items/<item_id>/move', methods=['PUT'])
def move_item(item_id):
    data = request.json
    if not data or "parent_id" not in data:
        return jsonify({"error": "Invalid payload"}), 400
        
    new_parent_id = data.get("parent_id")
    if new_parent_id in ('null', '', 'None'):
        new_parent_id = None
        
    if not check_auth(item_id) or not check_auth(new_parent_id):
        return jsonify({"error": "Unauthorized"}), 403
        
    updated_item = storage.update_item(item_id, {"parent_id": new_parent_id})
    if updated_item:
        return jsonify({"success": True, "item": updated_item})
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not check_auth(item_id):
        return jsonify({"error": "Unauthorized"}), 403
        
    deleted_items = storage.delete_item(item_id)
    if deleted_items:
        for item in deleted_items:
            if item.get("type") == "file":
                file_path = item.get("path")
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing file: {e}")
        return jsonify({"success": True, "deleted_count": len(deleted_items)})
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/open/<item_id>', methods=['GET'])
def open_item(item_id):
    if not check_auth(item_id):
        return "Unauthorized", 403
        
    item = storage.get_item(item_id)
    if not item:
        return "Item not found", 404
        
    item_type = item.get("type")
    path = item.get("path")
    
    if item_type == "url":
        if not path.startswith("http"):
            path = "https://" + path
        return redirect(path)
        
    elif item_type == "file":
        if not os.path.exists(path):
            return "File is missing on the server", 404
        return send_from_directory(STORAGE_DIR, item.get('name'))

    return "Unknown item type", 400

@app.route('/api/download/<item_id>', methods=['GET'])
def download_item(item_id):
    if not check_auth(item_id):
        return "Unauthorized", 403
        
    item = storage.get_item(item_id)
    if not item or item.get("type") != "file":
        return "File not found", 404
        
    path = item.get("path")
    if not os.path.exists(path):
        return "File is missing on the server", 404
        
    return send_from_directory(STORAGE_DIR, item.get('name'), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
