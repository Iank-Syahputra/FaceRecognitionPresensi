# 📝 Rencana Strategis Penyusunan Jurnal Ilmiah
**Judul Usulan:** Analisis Kinerja Arsitektur Multi-Vector dan Zero-Retraining pada Sistem Presensi Real-Time Menggunakan Pipeline MTCNN-FaceNet

---

## 1. Tahapan Penelitian (Research Roadmap)

Untuk menyusun jurnal yang kuat secara ilmiah, Anda perlu mengikuti alur kerja berikut:

### Fase A: Pendefinisian Masalah (Problem Statement)
*   **Fokus:** Mengapa metode klasifikasi wajah tradisional (menggunakan Softmax/SVM) tidak efisien untuk skala kampus? 
*   **Argumen:** Perlu adanya *retraining* setiap kali ada mahasiswa baru. Proyek ini menawarkan solusi **Metric Learning** yang hanya menyimpan vektor.

### Fase B: Eksperimen & Pengumpulan Data (Data Collection)
Anda harus melakukan pengujian sistematis untuk mendapatkan angka yang bisa ditulis di bab "Hasil dan Pembahasan":
1.  **Uji Akurasi (Confusion Matrix):** Lakukan 50-100 kali percobaan scan dengan berbagai kondisi (cahaya redup, pakai masker/kacamata, jarak jauh). Catat jumlah *True Positive* dan *False Positive*.
2.  **Uji Latensi (Performance):** Gunakan *Chrome DevTools* atau logging backend untuk mengukur berapa milidetik yang dibutuhkan mulai dari `capture frame` -> `inference AI` -> `database search`.
3.  **Uji Skalabilitas:** Masukkan 100-500 data wajah dummy ke database, lalu ukur apakah pencarian vektor menggunakan `pgvector` tetap stabil di bawah 100ms.

---

## 2. Struktur Penulisan Jurnal (IMRaD Style)

| Bab | Konten Utama |
| :--- | :--- |
| **Abstrak** | Ringkasan singkat: Masalah, Metode (MTCNN+FaceNet), Hasil (Akurasi %), dan Kesimpulan. |
| **Pendahuluan** | Latar belakang pentingnya absensi otomatis, kelemahan sistem manual, dan kontribusi penelitian ini pada efisiensi sistem *Zero-Retraining*. |
| **Tinjauan Pustaka** | Membahas penelitian terkait pengenalan wajah dan penggunaan PostgreSQL sebagai Vector Database. |
| **Metodologi** | Penjelasan detail arsitektur: Flow Smart Enrollment (Linear Ratio), Multi-Vector storage, dan alur integrasi SIAKAD. |
| **Hasil & Pembahasan** | Tampilkan grafik akurasi dan tabel perbandingan skor *Cosine Similarity* pada berbagai pose wajah. |
| **Kesimpulan** | Jawaban atas efektivitas sistem dan saran untuk pengembangan (misal: penambahan Liveness Detection). |

---

## 3. Strategi Literatur Review (Referensi Kunci)

Berikut adalah topik-topik jurnal yang wajib Anda kutip untuk mendukung argumen ilmiah Anda:

1.  **Deep Metric Learning (FaceNet):** 
    *   *Referensi Utama:* Schroff, F., Kalenichenko, D., & Philbin, J. (2015). "FaceNet: A Unified Embedding for Face Recognition and Clustering".
    *   *Poin Kutipan:* Bagaimana *Triplet Loss* digunakan untuk menciptakan ruang Euclidean yang memisahkan identitas wajah.

2.  **Facial Landmark Detection (MTCNN):**
    *   *Referensi Utama:* Zhang, K., et al. (2016). "Joint Face Detection and Alignment using Multi-task Cascaded Convolutional Networks".
    *   *Poin Kutipan:* Efisiensi MTCNN dalam mendeteksi wajah sekaligus melakukan alignment (*landmark*) secara bersamaan.

3.  **Vector Databases & Indexing (HNSW):**
    *   *Topik:* Analisis penggunaan ekstensi `pgvector` di PostgreSQL untuk pencarian tetangga terdekat (*Nearest Neighbor*).
    *   *Poin Kutipan:* Mengapa HNSW index lebih cepat daripada pencarian linear biasa pada data berdimensi 512.

4.  **Human-Computer Interaction (Smart Enrollment):**
    *   *Topik:* Pentingnya validasi pose wajah secara interaktif untuk meminimalisir kesalahan input data biometrik.

---

## 4. Metrik Kinerja yang Harus Ditampilkan (Data Ilmiah)

Jurnal yang baik harus menyajikan data angka. Pastikan Anda mencatat hal berikut:

1.  **Akurasi vs Pose:** Buat tabel tingkat keberhasilan pada pose Depan (%), Kanan (%), Kiri (%), dan Bawah (%).
2.  **Threshold Analysis:** Berikan analisis mengapa angka **0.75** dipilih sebagai ambang batas optimal (keseimbangan antara *Security* dan *Convenience*).
3.  **Resource Usage:** Penggunaan RAM dan CPU server saat meload model FaceNet (Inception-ResNet v1).

---

## 5. Metodologi Penelitian
3. Metodologi Penelitian (The "How" - Fokus Utama)Nah, bagian inilah yang sering membingungkan jika kamu berangkat dari kacamata pembuatan aplikasi (Software Engineering). Dalam penelitian ilmiah, Metodologi bukanlah cara kamu coding aplikasinya, melainkan bagaimana eksperimen tersebut dirancang, dijalankan, dan diukur.Di infografis, Metodologi ini bisa digambarkan sebagai Pipeline Eksperimen dengan 4 tahapan berikut:Tahap A: Akuisisi Data & Skenario Uji (Data Collection)Bukan sekadar mengumpulkan foto, tapi menyusun dataset terukur.Data Referensi (Anchor): 1 citra wajah frontal sempurna ($0^\circ$) per individu.Data Uji (Test Set): Citra wajah dengan variasi rotasi sumbu 3D, difokuskan pada Yaw (menoleh) dan Pitch (menunduk) pada interval derajat tertentu (misal: $\pm 15^\circ, \pm 30^\circ, \pm 45^\circ$).Tahap B: Prapemrosesan Spasial (Spatial Pre-processing)Tahap ini menjelaskan bagaimana mesin melihat gambar sebelum diolah. Di sinilah MTCNN masuk.MTCNN tidak hanya mencari kotak wajah, tapi melakukan Face Alignment (perataan wajah) berdasarkan 5 titik landmarks (mata, hidung, ujung bibir).Poin Ilmiah di Infografis: Tunjukkan visual wajah yang miring, lalu dideteksi titik landmarks-nya, dan diputar menjadi tegak lurus secara matriks.Tahap C: Ekstraksi Fitur & Proyeksi Ruang MetrikDi sinilah otak FaceNet bekerja. Ini adalah proses mengubah piksel menjadi angka.Alih-alih menebak "Ini wajah siapa?", FaceNet memproyeksikan citra wajah 2D ke dalam ruang metrik Euclidean berdimensi 512.Poin Ilmiah di Infografis: Gambarkan sebuah foto wajah yang masuk ke dalam blok "2D-CNN Inception-ResNet", lalu keluarannya berupa representasi vektor matriks: $[0.12, -0.45, 0.88, ...]_{512}$.Tahap D: Evaluasi Komparasi Vektor & Uji KetahananTahap akhir metodologi adalah menghitung hasil eksperimen.Vektor dari Tahap C tidak diklasifikasikan, melainkan dihitung jarak kemiripannya menggunakan metrik Cosine Similarity.Sertakan formula ini di infografis agar aura keilmiahannya sangat kuat:$$Cosine(A, B) = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$Pengukuran Performa (Metrics): Eksperimen diukur menggunakan matriks kebingungan (Confusion Matrix) untuk mencari batas toleransi (Threshold) yang menghasilkan FAR (False Acceptance Rate) dan FRR (False Rejection Rate) paling rendah saat dihadapkan pada variasi sudut wajah.Dengan membedah Metodologi menjadi 4 tahap eksperimen di atas, infografis kamu akan terlihat 100% seperti poster riset konferensi internasional yang menguji performa algoritma, bukan poster peluncuran aplikasi startup.Dari keempat tahapan Metodologi Penelitian di atas (Akuisisi Data, MTCNN, FaceNet, atau Evaluasi Metrik), bagian mana yang konsep visualisasinya masih terasa abu-abu untuk digambar ke dalam wireframe nanti?

## 6. Tips Publikasi
*   **Target Jurnal:** Carilah jurnal bertema *Information Systems*, *Computer Science*, atau *Artificial Intelligence* (SINTA 2-4 untuk skala nasional).
*   **Visualisasi:** Sertakan diagram arsitektur sistem (yang memisahkan Client, API, dan DB) serta *screenshot* UI responsif yang sudah kita buat tadi.

---
**Langkah Awal:** Mulailah dengan melakukan pengujian akurasi terhadap 5 orang teman Anda dengan masing-masing 10 kali percobaan. Data tersebut akan menjadi nyawa dari karya tulis ilmiah Anda.