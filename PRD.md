# PRODUCT REQUIREMENTS DOCUMENT
# (PRD)

**Judul Proyek:** Implementasi Sistem Presensi Zero-Retraining Menggunakan Pipeline MTCNN dan FaceNet pada Lingkungan Akademik (SIAKAD)

## 1. Project Overview

*   **Deskripsi Proyek:** Sebuah sistem presensi kelas otomatis berbasis pengenalan wajah (*Face Recognition*) yang terintegrasi dengan logika Sistem Informasi Akademik (SIAKAD). Sistem ini mengadopsi pendekatan *Metric Learning*, di mana model AI bertindak murni sebagai pengekstraksi fitur (*Feature Extractor*).
*   **Tujuan Utama (Objective):** Membangun sistem berskala besar yang *Zero-Retraining*—mampu mengenali mahasiswa baru hanya dengan menyimpan *Face Embeddings* (vektor wajah) ke pangkalan data tanpa perlu melatih ulang (*retrain*) keseluruhan model Deep Learning.
*   **Target Pengguna:**
    *   **Mahasiswa:** Melakukan pemindaian wajah mandiri secara interaktif saat awal registrasi (Enrollment) dengan validasi pose *real-time*.
    *   **Dosen/Admin:** Mengelola Mata Kuliah, membuka/menutup Sesi Kelas harian, dan memonitor *log* kehadiran mahasiswa secara *real-time* maupun melihat rekap laporan kelas yang telah usai.

## 2. User Flow

Sistem ini dibagi menjadi dua alur pengguna (*User Flow*) utama yang berjalan secara independen:

### Flow A: Smart Enrollment (Pendaftaran Wajah Dinamis)
1.  Mahasiswa membuka halaman registrasi biometrik (`/enroll`) di *dashboard* web dan memberikan izin akses kamera.
2.  Pengguna memasukkan data diri dasar (Nama, NIM).
3.  Antarmuka web menampilkan *live feed* dengan *overlay* bingkai oval ala Face ID dan memberikan instruksi interaktif (Depan, Kanan, Kiri, Bawah).
4.  Di latar belakang, UI mengirimkan *frame* setiap 500ms ke backend untuk **dianalisis putaran kepalanya (Head Pose Estimation)** menggunakan rasio *Facial Landmarks*.
5.  Sistem HANYA akan mengambil foto jika pengguna benar-benar memutar kepala sesuai instruksi (bingkai oval berubah hijau).
6.  Setelah 4 angle terpenuhi, MTCNN memotong wajah, dan FaceNet mengekstraknya menjadi 4 vektor terpisah (Multi-Vector Architecture).
7.  Sistem menyimpan data Identitas dan ke-4 vektor asli ke dalam *database*.

### Flow B: Inference SIAKAD (Presensi Kelas)
1.  **Buka Kelas:** Dosen masuk ke Dashboard (`/dashboard`), memilih Mata Kuliah, dan menekan "Buat Sesi Kelas Hari Ini". Sistem mencatat ID Sesi baru.
2.  **Kios Aktif:** Layar berpindah ke mode Kiosk (`/scan`). Kamera presensi di ruang kelas aktif menampilkan *live video feed*.
3.  **Deteksi:** Mahasiswa berjalan melewati jangkauan kamera. Frontend menggambar *Bounding Box* hijau dan nama jika wajah dikenali.
4.  **Komparasi & Log:** *Backend* mengekstrak vektor, melakukan pencarian kemiripan (*Vector Similarity Search*) ke seluruh variasi pose di database. Jika lolos *threshold*, sistem mencatat kehadiran ke dalam `attendance_logs` yang terikat khusus pada ID Sesi kelas tersebut (dengan perlindungan anti-spam/cooldown).
5.  **Tutup Kelas:** Dosen menekan "Tutup Kelas". Kamera mati. Dosen dapat melihat laporan detail siapa saja yang hadir pada sesi tersebut di halaman Laporan (`/session/[id]`).

## 3. Core Feature

*   **Smart Multi-Angle Enrollment:** Alur pendaftaran mandiri dengan AI yang secara *real-time* memvalidasi kemiringan dan putaran leher pengguna menggunakan Rasio Koordinat Linear XY, memastikan data biometrik yang disimpan sangat berkualitas.
*   **Multi-Vector Scale-Ready Pipeline:** Menyimpan seluruh variasi pose asli secara terpisah (bukan agregasi/rata-rata) untuk mencegah *Vector Dilution*, memungkinkan penggunaan batas keamanan (*Threshold*) yang sangat tinggi (0.75 - 0.85) meskipun jumlah mahasiswa mencapai ribuan.
*   **Business Logic SIAKAD:** Implementasi relasional antara Mata Kuliah (`courses`) dan Sesi Harian (`course_sessions`) yang memungkinkan presensi terisolasi per mata kuliah dan per hari.
*   **Vector-based Similarity Search:** Mesin pencari komparasi matriks wajah berkecepatan tinggi yang ditanam langsung di level database (Supabase/PostgreSQL).
*   **Real-time Kiosk & Reporting:** Antarmuka web reaktif (*Svelte 5 Runes*) untuk memantau presensi kelas secara langsung (*live Bounding Box*) dan fitur pembuatan laporan absensi harian yang dapat dicetak.

## 4. Arsitektur

Arsitektur dirancang menggunakan pola *Client-Server* dengan pemisahan komponen yang jelas:

1.  **Client Interface (Frontend):** SvelteKit bertindak sebagai *Thin Client*. Menangani UI pendaftaran, *polling* kamera Kios, dan mem-parsing hasil deteksi (kotak wajah) ke atas video, tanpa melakukan komputasi AI apa pun di *browser*.
2.  **ML API Gateway (Backend):** FastAPI (Python) sebagai otak. Menjalankan *Deep Learning* (MTCNN + FaceNet), kalkulasi rasio putaran leher, logika *cooldown* absensi, dan validasi sesi.
3.  **Vector Database:** Supabase (PostgreSQL + pgvector). Menyimpan identitas relasional SIAKAD dan melakukan komparasi jarak Cosine secara *native*.

## 5. Database Schema (Supabase)

Struktur relasional untuk mendukung manajemen SIAKAD dan Multi-Vector.

### Tabel 1: courses (Mata Kuliah)
*   `id` UUID (Primary Key)
*   `course_code` VARCHAR (ex: CS101)
*   `course_name` VARCHAR (ex: Kecerdasan Buatan)
*   `lecturer_name` VARCHAR

### Tabel 2: course_sessions (Sesi Kelas Harian)
*   `id` UUID (Primary Key)
*   `course_id` UUID (Foreign Key ke courses.id)
*   `session_date` DATE
*   `status` VARCHAR ('active' atau 'closed')

### Tabel 3: students (Master Identitas Mahasiswa)
*   `id` UUID (Primary Key)
*   `nim` VARCHAR (Unique)
*   `name` VARCHAR

### Tabel 4: student_faces (Database Biometrik Multi-Pose)
*   `id` UUID (Primary Key)
*   `student_id` UUID (Foreign Key ke students.id)
*   `embedding` VECTOR(512) (Satu baris menyimpan 1 dari 4 pose pendaftaran)
*   *Index:* HNSW (vector_cosine_ops)

### Tabel 5: attendance_logs (Transaksi Presensi)
*   `id` UUID (Primary Key)
*   `student_id` UUID (Foreign Key ke students.id)
*   `session_id` UUID (Foreign Key ke course_sessions.id)
*   `similarity_score` FLOAT
*   `timestamp` TIMESTAMP
*   *Constraint:* UNIQUE(student_id, session_id) -> Mencegah duplikasi absen di kelas yang sama.

## 6. Model dan Algoritma

*   **Pendeteksian & Head Pose Estimation (MTCNN):** Selain memotong area wajah, AI mengekstrak 5 *Facial Landmarks*. Rasio jarak horizontal (Sumbu X hidung terhadap mata) digunakan untuk mendeteksi putaran kepala (Yaw), sedangkan rasio vertikal (Sumbu Y) digunakan untuk deteksi *Pitch* (mendongak/menunduk).
*   **Ekstraksi Fitur (FaceNet Inception-ResNet v1):** Model AI *pre-trained* pada dataset VGGFace2 yang memetakan area wajah menjadi ruang Euclidean 512-dimensi.
*   **Komparasi (Cosine Similarity):** Metrik kalkulasi yang mengukur kedekatan dua vektor dengan fokus pada orientasi vektor, mengabaikan besaran intensitas cahaya. Eksekusi dilakukan asali oleh fungsi `match_face()` RPC di PostgreSQL.

## 7. Tech Stack

*   **Frontend:** SvelteKit v2 (dengan Svelte 5 Runes Reactivity), Tailwind CSS v3, MediaDevices API (WebRTC).
*   **Backend:** FastAPI (Python), Uvicorn, PyTorch, modul `facenet-pytorch`.
*   **Database:** Supabase (PostgreSQL), Ekstensi `pgvector`.