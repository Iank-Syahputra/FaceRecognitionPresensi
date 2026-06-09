# PRODUCT REQUIREMENTS DOCUMENT

# (PRD)

**Judul Proyek:** Implementasi Sistem Presensi Zero-Retraining Menggunakan Pipeline MTCNN
dan FaceNet pada Lingkungan Akademik

## 1. Project Overview

```
● Deskripsi Proyek: Sebuah sistem presensi kelas otomatis berbasis pengenalan wajah
( Face Recognition ) yang memecahkan masalah inefisiensi arsitektur klasifikasi tradisional.
Sistem ini mengadopsi pendekatan Metric Learning , di mana model AI bertindak murni
sebagai pengekstraksi fitur ( Feature Extractor ).
● Tujuan Utama (Objective): Membangun sistem yang Zero-Retraining —mampu mengenali
mahasiswa baru hanya dengan menyimpan Face Embeddings (vektor wajah) ke
pangkalan data tanpa perlu melatih ulang ( retrain ) keseluruhan model Deep Learning.
● Target Pengguna:
○ Mahasiswa: Melakukan pemindaian wajah mandiri saat awal registrasi (Enrollment)
dan melakukan presensi harian saat masuk kelas.
○ Admin/Dosen: Memantau sistem, memvalidasi data registrasi, dan mengelola log
kehadiran harian di dashboard.
```
## 2. User Flow

Sistem ini dibagi menjadi dua alur pengguna ( _User Flow_ ) utama yang berjalan secara
independen:

### Flow A: Enrollment (Pendaftaran Wajah Dinamis)

1. Mahasiswa (atau Admin) membuka halaman registrasi biometrik di _dashboard_ web dan
    memberikan izin akses kamera.
2. Pengguna memasukkan data diri dasar (Nama, NIM).
3. Antarmuka web menampilkan _live feed_ dan memberikan instruksi interaktif:
    ○ "Tatap lurus ke depan."
    ○ "Tolehkan kepala sedikit ke kanan."
    ○ "Tolehkan kepala sedikit ke kiri."
    ○ "Tundukkan kepala sedikit."
4. Di latar belakang, sistem menangkap _frame_ terbaik dari berbagai sudut tersebut secara
    otomatis.
5. _Frame_ dikirim ke _backend_. MTCNN mendeteksi wajah, lalu FaceNet mengekstraknya
    menjadi beberapa vektor. Vektor-vektor ini dirata-ratakan menjadi satu **Vektor Agregat**
    yang merepresentasikan wajah mahasiswa dari berbagai sisi.
6. Sistem menyimpan Nama, NIM, dan Vektor Agregat ke dalam _database_.


### Flow B: Inference (Presensi Real-Time di Kelas)

1. Kamera presensi di ruang kelas aktif menampilkan _live video feed_.
2. Mahasiswa berjalan melewati jangkauan kamera.
3. _Backend_ menangkap _frame_ , menjalankan MTCNN untuk memotong wajah, dan
    menggunakan FaceNet untuk mengekstrak vektor sementaranya secara _real-time_.
4. Sistem melakukan pencarian kemiripan ( _Vector Similarity Search_ ) antara vektor sementara
    ini dengan seluruh vektor di _database_.
5. Jika skor _Cosine Similarity_ melebihi ambang batas ( _threshold_ ), UI akan memunculkan
    nama mahasiswa dan sistem secara otomatis mencatat _timestamp_ kehadiran di _database_.

## 3. Core Feature

```
● Multi-Angle Live Enrollment: Alur pendaftaran mandiri interaktif yang menginstruksikan
pengguna untuk menggerakkan kepala, memastikan sistem menangkap variasi pose (Yaw
dan Pitch) untuk tingkat ketahanan ( robustness ) yang tinggi.
● Zero-Retraining Pipeline: Skalabilitas penuh. Menambah identitas mahasiswa baru dalam
hitungan detik tanpa membebani server dengan proses pelatihan ( training ) ulang model AI.
● Vector-based Similarity Search: Mesin pencari komparasi matriks wajah berkecepatan
tinggi yang ditanam langsung di level database (Supabase/PostgreSQL).
● Attendance Dashboard: Antarmuka web terpusat bagi dosen/admin untuk melihat metrik
kehadiran, log harian, dan mengekspor rekapitulasi data presensi.
```
## 4. Architektur

Arsitektur dirancang menggunakan pola _Client-Server_ dengan pemisahan komponen yang
jelas:

1. **Client Interface (Frontend):** Berjalan di peramban web ( _browser_ ). Menangani UI
    pendaftaran interaktif, menangkap _stream_ kamera web kelas, dan mengirimkan _frame_
    gambar ke _backend_ via HTTP/WebSocket.
2. **ML API Gateway (Backend):** Mesin utama _server-side_. Menerima gambar, mengeksekusi
    proses inferensi (MTCNN + FaceNet), dan mengalkulasi logika presensi berdasarkan
    respons pangkalan data.
3. **Vector Database:** Pangkalan data relasional yang diperluas ( _extended_ ) kemampuannya
    untuk menyimpan dan mengalkulasi kedekatan jarak antar array numerik berdimensi tinggi
    secara asali ( _native_ ).

## 5. Database Schema

Pangkalan data akan menggunakan ekstensi pgvector pada PostgreSQL (via Supabase) agar
operasi komparasi vektor dapat berjalan secepat kueri SQL biasa.

### Tabel 1: students (Tabel Master Identitas)


```
Kolom Tipe Data Keterangan
id UUID Primary Key
nim VARCHAR Nomor Induk Mahasiswa
(Unique Constraint)
name VARCHAR Nama Lengkap Mahasiswa
face_embedding VECTOR(512) Array 512-dimensi mewakili
Vektor Agregat dari
FaceNet
created_at TIMESTAMP Waktu data wajah
diregistrasi
```
### Tabel 2: attendance_logs (Tabel Transaksi Presensi)

```
Kolom Tipe Data Keterangan
id UUID Primary Key
student_id UUID
Foreign Key students.id
similarity_score FLOAT Tingkat keyakinan sistem
saat scan (contoh: 0.87)
timestamp TIMESTAMP Waktu detail kehadiran
dicatat oleh sistem
```
## 6. Model dan Algoritma

```
● Pendeteksian (MTCNN - Multi-task Cascaded Convolutional Networks): Model ringan
yang secara presisi mendeteksi area wajah dari gambar mentah dan melacak titik facial
landmarks (seperti mata dan hidung). Titik ini krusial untuk proses Face Alignment
(memutar gambar agar posisi wajah tegak/proporsional) sebelum diekstraksi.
● Ekstraksi Fitur (FaceNet dengan Inception-ResNet v1): Model AI pre-trained yang murni
berfungsi memetakan area wajah menjadi ruang Euclidean 512-dimensi. Pendekatan ini
dikenal sebagai Deep Metric Learning.
● Komparasi (Cosine Similarity): Metrik kalkulasi yang mengukur sudut kosinus antara dua
vektor di ruang multi-dimensi. Cocok untuk perbandingan wajah karena fokus pada
```

```
orientasi vektor, bukan besaran intensitas warna pikselnya. Formula:
```
## 7. Tech Stack

Pilihan teknologi untuk memastikan latensi sistem tetap rendah saat pemrosesan gambar
secara _real-time_ :
**● Frontend (Thin Client & Camera Capture):**
○ **Framework:** SvelteKit. Bertindak sebagai _thin client_ yang beroperasi tanpa
_Virtual DOM_. Menjamin kompilasi ukuran _bundle_ JavaScript yang sangat kecil,
meminimalisir _overhead_ memori _browser_ , dan memberikan reaktivitas DOM
seketika ( _native-like_ ) yang krusial untuk mencegah _stuttering_ saat antarmuka
memproses instruksi _live enrollment_ secara cepat.
○ **Styling:** Tailwind CSS. Digunakan untuk merancang antarmuka _dashboard_ yang
bersih dan responsif, yang mana utilitas kelasnya akan dikompilasi secara efisien
oleh Svelte.
○ **Camera API:** WebRTC atau MediaDevices API. Akses _hardware_ kamera dikelola
langsung melalui sistem reaktivitas reaktif bawaan Svelte (tanpa siklus _hooks_
yang rumit) untuk memastikan perekaman _stream_ yang stabil dan memitigasi
risiko kebocoran memori ( _memory leak_ ).
**● Backend (Machine Learning API):**
○ **Framework:** FastAPI (Python). Dipilih karena dukungan komputasi asinkron
( _async_ ) yang sangat baik untuk melayani inferensi model berat.
○ **Library Eksekusi AI:** PyTorch dan modul facenet-pytorch.
**● Database & Storage:**
● **Sistem:** Supabase (mengelola PostgreSQL dan API BaaS).
○ **Fitur Spesifik:** Modul ekstensi pgvector untuk optimasi penyimpanan dan
komputasi metrik pada kolom face_embedding.


