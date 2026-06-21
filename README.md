# File Manager Pro

File Manager Pro adalah aplikasi web manajer dokumen dan *link* URL berbasis Python Flask. Aplikasi ini berjalan di lingkungan lokal (*personal server*) tanpa memerlukan instalasi database tambahan karena memanfaatkan `database.json` sebagai tempat penyimpanannya. 

Aplikasi ini dilengkapi dengan fitur manajemen folder hierarkis (membuat folder, berpindah folder, pencarian global), upload multiple file, integrasi *Dark Mode*, serta fitur membuka dokumen dan website langsung dari tab browser.

## Fitur Utama
- 📁 **Sistem Folder:** Organisasikan file dan link Anda dengan mudah layaknya *File Explorer* sistem operasi.
- ☁️ **Upload & Drag and Drop:** Unggah banyak file sekaligus menggunakan tombol upload maupun *drag-and-drop*.
- 🔗 **Manajemen URL:** Simpan *bookmark* URL atau tautan penting beserta catatan tambahan.
- 👁️ **Buka Langsung:** Pratinjau atau buka langsung dokumen serta URL di tab browser Anda.
- 🌗 **Premium UI/UX:** Antarmuka bergaya *glassmorphism* modern dengan *Dark Mode*, animasi mulus, dan *breadcrumbs navigation*.
- 🔍 **Pencarian Real-time:** Cari nama file, link, kategori, atau catatan secara seketika (*debounce search*).

## Prasyarat Instalasi
- Pastikan Anda telah menginstal **Python 3.7+**. Jika belum, Anda dapat mengunduhnya dari [python.org](https://www.python.org/downloads/).

## Cara Instalasi & Menjalankan

1. **Unduh atau Clone repositori ini** ke dalam komputer Anda.
2. **Buka Terminal / Command Prompt** dan arahkan direktori ke folder tempat kode ini berada:
   ```bash
   cd /path/to/file_manager_pro
   ```
3. *(Opsional tapi disarankan)* **Buat Virtual Environment:**
   ```bash
   python -m venv venv
   
   # Untuk Windows:
   venv\Scripts\activate
   
   # Untuk macOS/Linux:
   source venv/bin/activate
   ```
4. **Instal Flask:** Aplikasi ini hanya membutuhkan Flask dari pustaka eksternal.
   ```bash
   pip install flask
   ```
5. **Jalankan Aplikasi:**
   ```bash
   python app.py
   ```
6. **Buka Aplikasi:**
   Buka browser Anda dan kunjungi URL berikut:
   **[http://localhost:5000](http://localhost:5000)**

## Struktur Folder

- `app.py`: Backend Flask untuk mengelola HTTP Request/API.
- `storage.py`: Logika pengontrolan *flat-file database* (membaca/menulis JSON).
- `templates/`: Menyimpan file `index.html` (kerangka antarmuka aplikasi).
- `static/`: Menyimpan `app.js` (logika Javascript klien) dan `style.css` (Visual/UI styling).
- `storage/`: (Otomatis dibuat) Direktori tempat menyimpan secara fisik file-file hasil *upload*.
- `database.json`: (Otomatis dibuat) Menyimpan keseluruhan data beserta *metadata* item (di-*ignore* dari Git).

## Peringatan
Aplikasi ini dirancang sebagai *Personal App* yang dijalankan untuk kepentingan jaringan lokal/pribadi. Pengaturan server bawaan Flask (*development server*) tidak ditujukan untuk skala *Production* berskala besar atau dipublikasikan secara eksternal karena masalah keamanan standar (tidak ada autentikasi). Jika Anda ingin menjalankannya secara *online*, harap gunakan *WSGI server* (seperti `gunicorn`) dan tambahkan proteksi *login/authentication*.
