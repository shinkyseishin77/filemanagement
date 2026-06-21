document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const itemContainer = document.getElementById('itemContainer');
    const searchInput = document.getElementById('searchInput');
    const filterCategory = document.getElementById('filterCategory');
    const sortSelect = document.getElementById('sortSelect');

    const themeToggle = document.getElementById('themeToggle');
    const gridViewBtn = document.getElementById('gridViewBtn');
    const listViewBtn = document.getElementById('listViewBtn');

    const dropZone = document.getElementById('dropZone');
    const fileInputHidden = document.getElementById('fileInputHidden');

    // Modals
    const addModal = document.getElementById('addModal');
    const editModal = document.getElementById('editModal');
    const btnAdd = document.getElementById('btnAdd');
    const closeAddModal = document.getElementById('closeAddModal');
    const closeEditModal = document.getElementById('closeEditModal');

    // Forms
    const uploadForm = document.getElementById('uploadForm');
    const urlForm = document.getElementById('urlForm');
    const editForm = document.getElementById('editForm');

    // State
    let currentItems = [];
    let isGridView = true;
    let currentParentId = null;

    const breadcrumbContainer = document.getElementById('breadcrumbContainer');
    const folderForm = document.getElementById('folderForm');

    // Initialize Theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon();

    // Theme Toggle
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon();
    });

    function updateThemeIcon() {
        const theme = document.documentElement.getAttribute('data-theme');
        themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }

    // View Toggles
    gridViewBtn.addEventListener('click', () => {
        isGridView = true;
        gridViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
        itemContainer.className = 'item-grid';
    });

    listViewBtn.addEventListener('click', () => {
        isGridView = false;
        listViewBtn.classList.add('active');
        gridViewBtn.classList.remove('active');
        itemContainer.className = 'item-list';
    });

    // Modals Logic
    btnAdd.addEventListener('click', () => addModal.classList.add('show'));
    closeAddModal.addEventListener('click', () => addModal.classList.remove('show'));
    closeEditModal.addEventListener('click', () => editModal.classList.remove('show'));

    window.addEventListener('click', (e) => {
        if (e.target === addModal) addModal.classList.remove('show');
        if (e.target === editModal) editModal.classList.remove('show');
    });

    // Tabs in Add Modal
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            e.target.classList.add('active');
            document.getElementById(e.target.dataset.tab).classList.add('active');
        });
    });

    // Fetch Data
    async function loadItems() {
        const search = searchInput.value;
        const category = filterCategory.value;
        const sort = sortSelect.value;

        const params = new URLSearchParams();
        if (search) {
            params.append('search', search);
        } else {
            if (currentParentId) params.append('parent_id', currentParentId);
            else params.append('parent_id', 'null');
        }

        if (category) params.append('category', category);
        if (sort) params.append('sort', sort);

        try {
            const res = await fetch(`/api/items?${params.toString()}`);
            currentItems = await res.json();
            renderItems();
            loadBreadcrumbs();
        } catch (error) {
            showToast('Error loading items', true);
        }
    }

    async function loadBreadcrumbs() {
        try {
            const res = await fetch(`/api/breadcrumb/${currentParentId || 'null'}`);
            const breadcrumbs = await res.json();

            breadcrumbContainer.innerHTML = '<span class="breadcrumb-item" data-id="null">🏠 Home</span>';
            breadcrumbs.forEach(bc => {
                breadcrumbContainer.innerHTML += '<span class="breadcrumb-separator">/</span>';
                breadcrumbContainer.innerHTML += `<span class="breadcrumb-item" data-id="${bc.id}">${bc.name}</span>`;
            });

            // Highlight current
            const items = breadcrumbContainer.querySelectorAll('.breadcrumb-item');
            if (items.length > 0) items[items.length - 1].classList.add('active');

            // Add listeners
            breadcrumbContainer.querySelectorAll('.breadcrumb-item').forEach(item => {
                item.addEventListener('click', () => {
                    const id = item.getAttribute('data-id');
                    if (id !== currentParentId) {
                        currentParentId = id === 'null' ? null : id;
                        loadItems();
                    }
                });
            });
        } catch (error) {
            console.error(error);
        }
    }

    // Render Items
    function renderItems() {
        itemContainer.innerHTML = '';
        if (currentItems.length === 0) {
            itemContainer.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--text-secondary)">No items found.</div>';
            return;
        }

        currentItems.forEach(item => {
            const card = document.createElement('div');
            card.className = 'item-card';

            const icon = getFileIcon(item);
            const sizeStr = item.size ? formatBytes(item.size) : '';
            const dateStr = new Date(item.added_at).toLocaleDateString();

            card.innerHTML = `
                <div class="card-icon">${icon}</div>
                <div class="card-content">
                    <div class="card-title" title="${item.name}">${item.name}</div>
                    <div class="card-meta">
                        <span>${dateStr}</span>
                        ${sizeStr ? `<span>• ${sizeStr}</span>` : ''}
                    </div>
                    ${item.category ? `<span class="card-tag">${item.category}</span>` : ''}
                </div>
                <div class="card-actions">
                    <button class="action-btn edit-btn" data-id="${item.id}" title="Edit">✏️</button>
                    <button class="action-btn delete-btn" data-id="${item.id}" title="Delete">🗑️</button>
                </div>
            `;

            // Click to open
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.card-actions')) {
                    if (item.type === 'folder') {
                        currentParentId = item.id;
                        searchInput.value = '';
                        loadItems();
                    } else {
                        openItem(item.id);
                    }
                }
            });

            // Edit
            card.querySelector('.edit-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                openEditModal(item);
            });

            // Delete
            card.querySelector('.delete-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm(`Delete "${item.name}"?`)) {
                    deleteItem(item.id);
                }
            });

            itemContainer.appendChild(card);
        });
    }

    function getFileIcon(item) {
        if (item.type === 'folder') return '📁';
        if (item.type === 'url') return '🔗';
        const ext = item.name.split('.').pop().toLowerCase();
        const icons = {
            'pdf': '📕',
            'doc': '📘', 'docx': '📘',
            'xls': '📗', 'xlsx': '📗',
            'ppt': '📙', 'pptx': '📙',
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
            'mp4': '🎬', 'avi': '🎬', 'mkv': '🎬',
            'mp3': '🎵', 'wav': '🎵',
            'zip': '📦', 'rar': '📦',
            'txt': '📄'
        };
        return icons[ext] || '📄';
    }

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Debounce Search
    let timeout = null;
    searchInput.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(loadItems, 300);
    });

    filterCategory.addEventListener('change', loadItems);
    sortSelect.addEventListener('change', loadItems);

    // API Calls
    function openItem(id) {
        window.open(`/api/open/${id}`, '_blank');
    }

    async function deleteItem(id) {
        try {
            const res = await fetch(`/api/items/${id}`, { method: 'DELETE' });
            if (!res.ok) throw new Error('Failed to delete');
            showToast('Item deleted');
            loadItems();
        } catch (error) {
            showToast(error.message, true);
        }
    }

    // Add URL
    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            name: document.getElementById('urlTitle').value,
            url: document.getElementById('urlLink').value,
            category: document.getElementById('urlCategory').value,
            note: document.getElementById('urlNote').value,
            parent_id: currentParentId
        };

        try {
            const res = await fetch('/api/items', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error('Failed to add URL');

            showToast('URL added successfully');
            addModal.classList.remove('show');
            urlForm.reset();
            loadItems();
        } catch (error) {
            showToast(error.message, true);
        }
    });

    // Add Folder
    if (folderForm) {
        folderForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                type: 'folder',
                name: document.getElementById('folderName').value,
                parent_id: currentParentId
            };

            try {
                const res = await fetch('/api/items', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!res.ok) throw new Error('Failed to create folder');

                showToast('Folder created successfully');
                addModal.classList.remove('show');
                folderForm.reset();
                loadItems();
            } catch (error) {
                showToast(error.message, true);
            }
        });
    }

    // Upload File
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const files = document.getElementById('fileUpload').files;
        if (files.length === 0) return;

        await handleFileUpload(files, {
            category: document.getElementById('uploadCategory').value,
            note: document.getElementById('uploadNote').value
        });

        uploadForm.reset();
        addModal.classList.remove('show');
    });

    async function handleFileUpload(files, extraData = {}) {
        const formData = new FormData();

        if (files instanceof FileList || Array.isArray(files)) {
            for (let i = 0; i < files.length; i++) {
                formData.append('file', files[i]);
            }
        } else {
            formData.append('file', files);
        }

        if (extraData.category) formData.append('category', extraData.category);
        if (extraData.note) formData.append('note', extraData.note);
        if (currentParentId) formData.append('parent_id', currentParentId);

        try {
            showToast('Uploading...');
            const res = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Upload failed');

            showToast('File(s) uploaded successfully');
            loadItems();
        } catch (error) {
            showToast(error.message, true);
        }
    }

    // Drag and Drop Logic
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileUpload(files, { category: 'Other' });
        }
    });

    dropZone.addEventListener('click', () => {
        fileInputHidden.click();
    });

    fileInputHidden.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files, { category: 'Other' });
        }
    });

    // Edit Logic
    function openEditModal(item) {
        document.getElementById('editId').value = item.id;
        document.getElementById('editName').value = item.name;
        document.getElementById('editCategory').value = item.category || 'Other';
        document.getElementById('editNote').value = item.note || '';
        editModal.classList.add('show');
    }

    editForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('editId').value;
        const payload = {
            name: document.getElementById('editName').value,
            category: document.getElementById('editCategory').value,
            note: document.getElementById('editNote').value
        };

        try {
            const res = await fetch(`/api/items/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error('Failed to update');

            showToast('Updated successfully');
            editModal.classList.remove('show');
            loadItems();
        } catch (error) {
            showToast(error.message, true);
        }
    });

    // Toast Notification
    const toast = document.getElementById('toast');
    let toastTimeout;
    function showToast(message, isError = false) {
        toast.textContent = message;
        toast.className = `toast show ${isError ? 'error' : ''}`;

        clearTimeout(toastTimeout);
        toastTimeout = setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // Initial Load
    loadItems();
});
