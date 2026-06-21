import re

with open('static/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. State
code = code.replace(
    'let clipboard = null;',
    'let clipboard = null;\n    let privatePassword = null;'
)

# 2. apiFetch wrapper
api_fetch_code = '''
    async function apiFetch(url, options = {}) {
        if (!options.headers) options.headers = {};
        if (privatePassword) {
            options.headers['X-Private-Password'] = privatePassword;
        }
        const res = await fetch(url, options);
        if (res.status === 403) {
            authModal.classList.add('show');
            throw new Error('AUTH_REQUIRED');
        }
        return res;
    }
'''
code = code.replace('// Fetch Data', '// Fetch Data\n' + api_fetch_code)

# Replace all fetch calls with apiFetch, EXCEPT the one in authForm
code = re.sub(r"fetch\(`/api/(items|breadcrumb|upload)(.*?)`", r"apiFetch(`/api/\1\2`", code)
code = re.sub(r"fetch\('/api/(items|upload)'", r"apiFetch('/api/\1'", code)

# 3. loadItems 403 handling
code = code.replace(
    '''            if (res.status === 403) {
                authModal.classList.add('show');
                return;
            }
            currentItems = await res.json();''',
    '''            currentItems = await res.json();'''
)
code = code.replace(
    "showToast('Error loading items', true);",
    "if (error.message !== 'AUTH_REQUIRED') showToast('Error loading items', true);"
)

# 4. Password reset on navigate
code = code.replace(
    '''                        currentParentId = id === 'null' ? null : id;
                        loadItems();''',
    '''                        currentParentId = id === 'null' ? null : id;
                        privatePassword = null;
                        loadItems();'''
)
code = code.replace(
    '''                        currentParentId = item.id;
                        searchInput.value = '';
                        loadItems();''',
    '''                        currentParentId = item.id;
                        searchInput.value = '';
                        privatePassword = null;
                        loadItems();'''
)

# 5. Add is_private to payload
code = code.replace(
    "name: document.getElementById('folderName').value,",
    "name: document.getElementById('folderName').value,\n                is_private: document.getElementById('folderIsPrivate').checked,"
)
code = code.replace(
    "document.getElementById('editNote').value = item.note || '';",
    "document.getElementById('editNote').value = item.note || '';\n        document.getElementById('editIsPrivate').checked = item.is_private || false;"
)
code = code.replace(
    "note: document.getElementById('editNote').value",
    "note: document.getElementById('editNote').value,\n            is_private: document.getElementById('editIsPrivate').checked"
)

# 6. Open / Download links
code = code.replace(
    "window.open(`/api/open/${id}`, '_blank');",
    "let url = `/api/open/${id}`;\n        if (privatePassword) url += `?pwd=${encodeURIComponent(privatePassword)}`;\n        window.open(url, '_blank');"
)
code = code.replace(
    "window.location.href = `/api/download/${item.id}`;",
    "window.location.href = privatePassword ? `/api/download/${item.id}?pwd=${encodeURIComponent(privatePassword)}` : `/api/download/${item.id}`;"
)

# 7. authForm replace
old_auth = '''    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pwd = document.getElementById('authPassword').value;
        try {
            const res = await fetch('/api/auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pwd })
            });
            if (res.ok) {
                authModal.classList.remove('show');
                authForm.reset();
                loadItems();
            } else {
                showToast('Invalid password', true);
            }
        } catch (error) {
            showToast('Error', true);
        }
    });'''

new_auth = '''    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pwd = document.getElementById('authPassword').value;
        const tempPwd = privatePassword;
        privatePassword = pwd;
        
        try {
            const params = new URLSearchParams();
            if (currentParentId) params.append('parent_id', currentParentId);
            const res = await fetch(`/api/items?${params.toString()}`, {
                headers: { 'X-Private-Password': pwd }
            });
            if (res.ok) {
                authModal.classList.remove('show');
                authForm.reset();
                loadItems();
            } else {
                privatePassword = tempPwd;
                showToast('Invalid password', true);
            }
        } catch (error) {
            privatePassword = tempPwd;
            showToast('Error', true);
        }
    });'''
code = code.replace(old_auth, new_auth)

with open('static/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print('Updated static/app.js')
