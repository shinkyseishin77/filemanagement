import os
import subprocess
import platform
import webbrowser
from flask import Flask, request, jsonify, render_template, redirect, send_from_directory
import storage

app = Flask(__name__)

STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'storage')
os.makedirs(STORAGE_DIR, exist_ok=True)

# Initialize JSON DB
storage.init_db()

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
        
    items = storage.get_items(search, category, sort_by, parent_id)
    return jsonify(items)

@app.route('/api/breadcrumb/<item_id>', methods=['GET'])
def get_breadcrumb(item_id):
    if item_id in ('null', '', 'None'):
        return jsonify([])
    return jsonify(storage.get_breadcrumb(item_id))

@app.route('/api/items', methods=['POST'])
def add_item_url_folder():
    # Used for adding URL, manual references, or folders
    data = request.json
    if not data:
        return jsonify({"error": "Invalid payload"}), 400
        
    parent_id = data.get("parent_id")
    if parent_id in ('null', '', 'None'):
        parent_id = None

    item = storage.add_item({
        "type": data.get("type", "url"),
        "name": data.get("name", "Untitled"),
        "path": data.get("url", ""),
        "category": data.get("category", ""),
        "tags": data.get("tags", []),
        "note": data.get("note", ""),
        "parent_id": parent_id
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
    
    uploaded_items = []
    
    for file in files:
        if file.filename == '':
            continue
            
        # Save the file
        filename = file.filename
        save_path = os.path.join(STORAGE_DIR, filename)
        
        # Handle filename collision
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(save_path):
            filename = f"{base}_{counter}{ext}"
            save_path = os.path.join(STORAGE_DIR, filename)
            counter += 1
            
        file.save(save_path)
        file_size = os.path.getsize(save_path)
        
        # Save to DB
        item = storage.add_item({
            "type": "file",
            "name": filename,
            "path": save_path,
            "category": category,
            "size": file_size,
            "note": note,
            "parent_id": parent_id
        })
        uploaded_items.append(item)
        
    return jsonify({"success": True, "items": uploaded_items}), 201

@app.route('/api/items/<item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    updated_item = storage.update_item(item_id, data)
    if updated_item:
        return jsonify(updated_item)
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    deleted_items = storage.delete_item(item_id)
    if deleted_items:
        # Remove physical files for any deleted items that are of type 'file'
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
