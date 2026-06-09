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

## 5. Tips Publikasi
*   **Target Jurnal:** Carilah jurnal bertema *Information Systems*, *Computer Science*, atau *Artificial Intelligence* (SINTA 2-4 untuk skala nasional).
*   **Visualisasi:** Sertakan diagram arsitektur sistem (yang memisahkan Client, API, dan DB) serta *screenshot* UI responsif yang sudah kita buat tadi.

---
**Langkah Awal:** Mulailah dengan melakukan pengujian akurasi terhadap 5 orang teman Anda dengan masing-masing 10 kali percobaan. Data tersebut akan menjadi nyawa dari karya tulis ilmiah Anda.
