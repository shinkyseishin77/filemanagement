# File Manager Pro

File Manager Pro adalah aplikasi web manajer dokumen dan *link* URL berbasis Python Flask. Aplikasi ini berjalan di lingkungan lokal (*personal server*) tanpa memerlukan instalasi database tambahan karena memanfaatkan `database.json` sebagai tempat penyimpanannya. 

Aplikasi ini dilengkapi dengan fitur manajemen folder hierarkis, drag & drop, fitur keamanan privasi ketat (strict privacy), serta dukungan *Dark Mode* yang modern.

## Fitur Utama
- 📁 **Sistem Folder:** Organisasikan file dan link layaknya *File Explorer* sistem operasi.
- 🔒 **Strict Privacy (Kunci Keamanan):** Kunci folder apa pun dengan password. Password dikonfirmasi setiap kali Anda membuka folder, dan sistem akan langsung menguncinya kembali begitu Anda keluar dari folder tersebut (tanpa session).
- ☁️ **Upload & Drag and Drop:** Pindahkan file antar folder cukup dengan *drag-and-drop*, atau gunakan opsi **Cut & Paste**.
- ⬇️ **Download File Langsung:** Unduh file yang Anda upload langsung ke komputer Anda dengan menekan ikon unduhan.
- 🔗 **Manajemen URL:** Simpan *bookmark* URL atau tautan penting beserta catatan tambahan.
- 🌗 **Premium UI/UX:** Antarmuka bergaya *glassmorphism* modern dengan *Dark Mode*, animasi mulus, dan *breadcrumbs navigation*.

---

## 🛠️ Tutorial Pemasangan Aplikasi

### 1. Prasyarat Instalasi
- Pastikan Anda telah menginstal **Python 3.7+**. Unduh dari [python.org](https://www.python.org/downloads/) jika belum memiliki.

### 2. Persiapan Folder & Lingkungan Virtual
1. **Unduh atau Clone repositori ini** ke dalam komputer Anda.
2. **Buka Terminal / Command Prompt** lalu arahkan ke folder ini:
   ```bash
   cd /path/to/file_manager_pro
   ```
3. *(Sangat Disarankan)* **Buat Virtual Environment:**
   ```bash
   # Windows:
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```
4. **Instal Flask** (Satu-satunya library eksternal yang dibutuhkan):
   ```bash
   pip install flask
   ```

### 3. Menjalankan Aplikasi
Ketikkan perintah berikut di terminal Anda:
```bash
python app.py
```
Aplikasi akan mulai berjalan. Buka browser Anda dan kunjungi URL: **[http://localhost:5000](http://localhost:5000)**

---

## ⚙️ Tutorial Konfigurasi (`config.json`)

Saat Anda menjalankan aplikasi pertama kali, sistem akan secara otomatis membaca (atau membuat jika belum ada) file bernama `config.json`. File ini berfungsi untuk menyimpan semua pengaturan vital aplikasi.

**Contoh isi `config.json`:**
```json
{
  "storage_dir": "storage",
  "db_file": "database.json",
  "private_folder_name": "Private",
  "private_folder_password": "admin",
  "secret_key": "your_super_secret_flask_key_here"
}
```

### Penjelasan Field:
- `storage_dir`: Nama folder fisik tempat file yang diupload akan disimpan. (Default: `"storage"`)
- `db_file`: Nama file database JSON penyimpan struktur item. (Default: `"database.json"`)
- `private_folder_password`: **Password utama untuk membuka folder privat**. Ubah password "admin" ini dengan password rahasia Anda sendiri.
- `private_folder_name`: Nama default untuk folder privat bawaan. (Default: `"Private"`)
- `secret_key`: Kunci rahasia internal aplikasi. Ganti dengan teks acak apa saja agar lebih aman.

*(Catatan: Setelah Anda mengubah isi `config.json`, pastikan Anda merestart terminal/server Flask Anda agar perubahan diterapkan).*

---

## 🔒 Tutorial Penggunaan Folder Privat

Fitur privasi di File Manager Pro bersifat *strict* (ketat). Cara kerjanya:
1. **Membuat Folder Privat Baru:**
   - Klik tombol **+ Add New** di kanan atas.
   - Pilih tab **New Folder**.
   - Masukkan nama folder, lalu centang kotak **"Make this folder Private"**.
   - (Anda juga bisa mengubah file/folder yang sudah ada menjadi privat dengan mengeklik tombol edit (✏️) lalu mencentang opsi Private).
   
2. **Membuka Folder Privat:**
   - Klik pada folder yang terkunci (ikonnya memiliki tanda 🔒).
   - Sebuah modal pop-up akan muncul menanyakan password.
   - Masukkan password Anda (disetel dari `config.json` -> `private_folder_password`).

3. **Keamanan Otomatis (Auto-Lock):**
   - Setelah masuk, Anda bebas menghapus, memindah, atau men-download file di dalamnya.
   - **Namun**, begitu Anda berpindah keluar dari folder tersebut (misalnya menekan tombol "🏠 Home"), akses akan **langsung ditutup total**.
   - Jika Anda mencoba masuk kembali satu detik kemudian, sistem akan memaksa Anda memasukkan password ulang. Sistem tidak pernah menyimpan password Anda di session permanen!

## Struktur Folder Bawaan
- `app.py`: Backend pengelola sistem dan File Routing.
- `storage.py`: Engine database flat-file.
- `static/app.js`: Logika Javascript klien (drag and drop, auth handling).
- `config.json`: File pengaturan (Jangan dikomit ke public git).
