# 📷 Sistem Presensi Biometrik Zero-Retraining
**Computer Vision & Deep Metric Learning untuk Sistem Informasi Akademik (SIAKAD)**

Proyek ini adalah implementasi sistem presensi kelas otomatis berbasis pengenalan wajah (*Face Recognition*). Sistem ini mengadopsi pendekatan *Zero-Retraining* melalui *Deep Metric Learning*, di mana model AI (MTCNN & FaceNet) mengekstrak wajah menjadi vektor 512-dimensi yang disimpan ke dalam *Vector Database* (Supabase `pgvector`).

Sistem ini memiliki dua fitur utama:
1.  **Smart Enrollment:** Registrasi wajah ala *Face ID* dengan validasi pose wajah (Yaw/Pitch) secara *real-time*.
2.  **Kios Presensi Akademik:** Layar *dashboard* Dosen untuk membuka sesi kelas, dan fitur *scan* kamera yang secara *real-time* menampilkan *bounding box*, nama, dan log kehadiran mahasiswa.

---

## 🛠️ Prasyarat Sistem

Sebelum Anda melakukan kloning dan menjalankan proyek ini di komputer lokal, pastikan Anda telah menginstal perangkat lunak berikut:

*   **Node.js** (v18 atau lebih baru) - Untuk menjalankan Frontend SvelteKit.
*   **Python** (v3.9 - v3.11) - Untuk menjalankan Backend FastAPI & PyTorch.
*   **Git** - Untuk mengkloning *repository*.
*   Akun **Supabase** - Untuk keperluan *database* PostgreSQL dan fitur pencarian vektor.

---

## 🚀 Langkah-langkah Instalasi

### Tahap 1: Setup Supabase Database
1. Buat proyek baru di [Supabase](https://supabase.com/).
2. Buka menu **SQL Editor** di *dashboard* Supabase Anda.
3. Salin seluruh isi kode dari file `database/supabase_schema.sql` yang ada di dalam *repository* ini.
4. Tempelkan ke dalam SQL Editor Supabase, lalu jalankan (**RUN**).
5. Buka menu **Project Settings -> API** untuk mendapatkan `Project URL` dan `anon/public key` (akan digunakan di Tahap 2).

### Tahap 2: Setup Backend (Machine Learning API)
Backend ini bertugas memproses gambar menggunakan AI (MTCNN untuk mendeteksi wajah, FaceNet untuk ekstraksi fitur).

1. Buka Terminal/Command Prompt, lalu arahkan ke folder `backend`:
   ```bash
   cd backend
   ```
2. Buat *Virtual Environment* (Sangat Direkomendasikan):
   ```bash
   python -m venv myvenv
   ```
3. Aktifkan *Virtual Environment*:
   * Windows (Command Prompt): `myvenv\Scripts\activate.bat`
   * Windows (PowerShell): `.\myvenv\Scripts\Activate.ps1`
   * Mac/Linux: `source myvenv/bin/activate`
4. Instal semua *requirements*:
   ```bash
   pip install -r requirements.txt
   ```
   *(Catatan: Mengunduh PyTorch memakan waktu yang cukup lama tergantung koneksi internet Anda).*
5. Buat file `.env` di dalam folder `backend/` dan isi dengan konfigurasi Supabase Anda (Tanpa tanda kutip):
   ```env
   SUPABASE_URL=https://[PROJECT-ID].supabase.co
   SUPABASE_KEY=ey...[YOUR-ANON-KEY]...
   SIMILARITY_THRESHOLD=0.75
   ```
6. Jalankan Server FastAPI:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *Saat pertama kali dijalankan, server mungkin agak lambat karena harus mengunduh file bobot (weights) pre-trained model FaceNet `vggface2`.*

### Tahap 3: Setup Frontend (SvelteKit UI)
Frontend ini merupakan *Thin Client* yang mengelola kamera (WebRTC) dan UI, lalu mengirimkan gambar *base64* ke backend.

1. Buka Terminal/Command Prompt baru, lalu arahkan ke folder `frontend`:
   ```bash
   cd frontend
   ```
2. Instal modul *dependencies* Node:
   ```bash
   npm install
   ```
3. Jalankan Server SvelteKit:
   ```bash
   npm run dev
   ```
4. Buka *browser* Anda dan arahkan ke: `http://localhost:5173`

---

## 👨‍🏫 Cara Penggunaan (User Flow)

1.  **Mendaftarkan Mahasiswa:**
    *   Buka aplikasi di `http://localhost:5173`.
    *   Pilih **Registrasi Wajah (Enrollment)**.
    *   Masukkan NIM dan Nama Lengkap.
    *   Tekan "Mulai Pendaftaran" dan ikuti panduan oval di layar (menatap ke depan, menoleh kanan, kiri, dan bawah) sampai muncul status berhasil.
2.  **Membuka Kelas & Absensi:**
    *   Kembali ke halaman utama, pilih **Akses Dosen & Admin**.
    *   Pilih salah satu mata kuliah yang tersedia (contoh: *Kecerdasan Buatan*), lalu tekan **Buat Sesi Kelas Hari Ini**.
    *   Layar Kios Kamera akan terbuka. Persilakan mahasiswa untuk lewat di depan kamera.
    *   Kotak hijau dan *pop-up* akan muncul saat wajah dikenali. Daftar kehadiran di panel kanan akan bertambah.
3.  **Melihat Laporan Kehadiran:**
    *   Klik **Tutup Kelas** berwarna merah jika kelas telah usai.
    *   Anda akan dikembalikan ke *Dashboard* Dosen.
    *   Pada kartu mata kuliah tersebut, cari riwayat sesi yang statusnya "Selesai", lalu klik **Lihat Detail**.
    *   Anda bisa melihat tabel presensi lengkap beserta tombol untuk mencetak laporan.

---

## 🧩 Arsitektur Proyek

*   **Pemisahan Tugas:** Tidak ada proses komputasi AI (TensorFlow/ONNX) di sisi *browser* (Frontend). SvelteKit murni bertugas menangkap gambar 2D dan merender DOM. Semua beban komputasi AI diserahkan ke FastAPI (Backend).
*   **Multi-Vector Concept:** Untuk mencegah efek penggabungan vektor yang "buram", setiap wajah (4 angle pose pendaftaran) disimpan secara terpisah di tabel `student_faces`. Saat *scan* kelas, RPC PostgreSQL akan menghitung skor kemiripan antara wajah di kamera dengan *semua* variasi wajah milik seluruh mahasiswa secara paralel di level *database*.

---

# 👥 Tim Pengembang

* Muhammad Ihram Syahputra
* Prasstyo Adhi Pangestu
* Jeremy Revaldo Latuperisa
* Siti Surti
* Nabila Auliya Bitu

---
