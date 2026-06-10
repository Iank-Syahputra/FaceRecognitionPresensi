# Analisis Kinerja Arsitektur Multi-Vector dan Zero-Retraining pada Sistem Presensi Real-Time Menggunakan Pipeline MTCNN-FaceNet

## Ringkasan Eksekutif

Sistem ini adalah **sistem presensi berbasis pengenalan wajah** yang bekerja dalam **4 fase eksperimen** sesuai metodologi penelitian ilmiah. Arsitektur utamanya adalah **Zero-Retraining**: tidak perlu melatih ulang model saat ada subjek baru — cukup simpan embedding (vektor 512-d) sebagai referensi dan bandingkan dengan cosine similarity.

```
[Webcam] → [MTCNN] → [FaceNet] → [512-d Vector] → [Cosine Similarity] → [Match/No-Match]
```

---

## Alur Proses Logis (4 Fase)

### FASE A: Akuisisi Data & Skenario Uji

**Tujuan**: Mengumpulkan dataset wajah dengan variasi pose yang terukur.

**Cara Kerja**:
1. User memasukkan **nama subjek** (misal: "iank")
2. Sistem membuat folder `notebook/data/{nama_subjek}/`
3. `WebcamAcquisitor` (kelas berbasis `ipywidgets`) membuka kamera
4. 8 pose muncul satu per satu secara interaktif:

| Pose | Sudut | Frame | Fungsi |
|------|-------|-------|--------|
| `anchor` (depan) | Yaw 0°, Pitch 0° | 3 | Referensi biometrik utama |
| `kanan_15` | Yaw +15° | 5 | Uji rotasi horizontal ringan |
| `kanan_30` | Yaw +30° | 5 | Uji rotasi horizontal sedang |
| `kanan_45` | Yaw +45° | 5 | Uji rotasi horizontal ekstrem |
| `kiri_15` | Yaw -15° | 5 | Uji rotasi horizontal (kiri) |
| `kiri_30` | Yaw -30° | 5 | Uji rotasi horizontal (kiri) |
| `bawah_30` | Pitch +30° | 5 | Uji rotasi vertikal |

5. User mengklik **Capture** untuk menyimpan frame, **Next Pose** untuk lanjut

**Mengapa ini penting**: Variasi pose mensimulasikan kondisi nyata di mana orang tidak selalu menghadap lurus ke kamera. Anchor (frontal) menjadi `ground truth` untuk perbandingan.

---

### FASE B: Prapemrosesan Spasial (MTCNN)

**Tujuan**: Mendeteksi dan meluruskan wajah sebelum ekstraksi fitur.

**Cara Kerja**:
1. **MTCNN** (Multi-task Cascaded Convolutional Networks) memproses setiap gambar
2. Tiga jaringan CNN bertingkat: **P-Net → R-Net → O-Net**
3. Output: **Bounding box** + **5 landmarks** (mata kiri, mata kanan, hidung, mulut kiri, mulut kanan)
4. Wajah di-crop dan di-**align** (diluruskan) ke ukuran **160×160 piksel**
5. Jika wajah tidak terdeteksi → frame tersebut dilewati

**Output visual**:
- Gambar "Before vs After" menunjukkan crop MTCNN
- Detection rate per pose (anchor 100%, variasi sudut >90%)
- Landmarks divisualisasikan dengan warna berbeda

**Mengapa ini penting**: FaceNet membutuhkan input wajah yang sudah align. Tanpa alignment, embedding yang dihasilkan tidak akurat karena variasi geometri wajah.

---

### FASE C: Ekstraksi Fitur & Proyeksi Ruang Metrik (FaceNet)

**Tujuan**: Mengkonversi citra wajah 160×160 menjadi **vektor 512 dimensi**.

**Cara Kerja**:
1. **FaceNet** (InceptionResNetV1) — model pre-trained pada **VGGFace2** (3.3M gambar, 9.131 identitas)
2. Setiap wajah → `resnet(face_tensor)` → vektor 512-d
3. Vektor di-**L2 normalize** sehingga panjangnya = 1.0
4. Embedding disimpan dalam dictionary: `all_embeddings[subjek][pose] = array(n_frame, 512)`

**Proyeksi Dimensionality Reduction**:

| Metode | Tujuan |
|--------|--------|
| **PCA** | Menunjukkan embedding subjek yang sama mengelompok (clustering) |
| **t-SNE** | Visualisasi non-linear untuk melihat separasi antar subjek |

**Mengapa ini penting**: Embedding 512-d adalah representasi numerik unik dari wajah seseorang. Dalam ruang ini, wajah orang yang sama memiliki jarak yang dekat (cosine similarity tinggi), sedangkan orang berbeda berjauhan.

---

### FASE D: Evaluasi Komparasi Vektor & Uji Ketahanan

Ini adalah fase inti yang menjawab **apakah sistem bisa mendeteksi orang yang sama atau tidak**.

#### D.1 Cosine Similarity per Pose

**Rumus**:
```
similarity(A, B) = cos(θ) = (A · B) / (||A|| × ||B||)
```

Karena semua embedding sudah L2-normalized (||A|| = ||B|| = 1):
```
similarity(A, B) = A · B
```

Nilai: **+1** (identik) hingga **-1** (berlawanan). Dalam praktik, sesama orang biasanya >0.7, orang berbeda <0.5.

**Proses**:
1. Anchor vector dihitung sebagai **mean** dari semua frame anchor subjek tertentu
2. Setiap frame non-anchor dibandingkan dengan anchor menggunakan cosine similarity
3. Hasil: tabel mean, std, min, max similarity per pose

**Contoh hasil** (dari output notebook):
| Pose | Mean | Std |
|------|------|-----|
| anchor | 0.9874 | 0.0054 |
| kiri_15 | 0.8973 | 0.0104 |
| kanan_15 | 0.8612 | 0.0132 |
| kiri_30 | 0.8284 | 0.0201 |
| kanan_45 | 0.7353 | 0.0693 |
| bawah_30 | 0.5827 | 0.0396 |

**Interpretasi**: Semakin besar sudut yaw/pitch, semakin turun similarity-nya. Bawah_30 (Pitch +30°) paling sulit karena landmark wajah berubah signifikan.

#### D.2 Threshold Analysis (F1-Score Optimization)

Mencari **threshold (τ) optimal** untuk keputusan "dikenali / tidak dikenali".

**Proses**:
1. Hitung similarity **genuine** (sama subjek) vs **impostor** (beda subjek)
2. Untuk setiap τ ∈ [0.3, 0.95]:
   - Pred: similarity ≥ τ → positif (dikenali)
   - Hitung **TP, FP, FN, TN**
   - Hitung **Precision, Recall, F1-Score**
3. Pilih τ dengan **F1-Score tertinggi**

**Output**: Grafik Precision-Recall-F1 vs Threshold + distribusi genuine vs impostor.

**Contoh output**:
```
Optimal threshold: τ = 0.7586
Best F1-Score: 1.0000
```

#### D.3 Real-time Test (WebcamTester)

**Fitur baru**: Membuka kamera lagi untuk menguji secara langsung.

**Alur**:
1. Input **nama subjek** (GT) — kosongkan untuk orang asing
2. Klik **Capture & Test**:
   - Capture frame dari webcam
   - Deteksi wajah via MTCNN
   - Ekstrak embedding via FaceNet
   - Bandingkan dengan SEMUA anchor yang tersimpan
   - Cari similarity tertinggi
   - Jika `max_sim ≥ τ` → prediksi sebagai subjek X, jika tidak → `<unknown>`
3. Hasil per-test ditampilkan dalam tabel
4. **Finish & Evaluasi** → tampilkan confusion matrix dan metrik

**Metrik evaluasi**:
- **Accuracy**: (TP + TN) / Total
- **Precision per subjek**: TP / (TP + FP)
- **Recall per subjek**: TP / (TP + FN)
- **F1-Score per subjek**: 2 × (P × R) / (P + R)
- **Macro Average**: rata-rata metrik seluruh kelas

#### D.4 Latency Benchmarking

Mengukur kecepatan pipeline:

| Komponen | Latency | 
|----------|---------|
| MTCNN | ~250 ms |
| FaceNet | ~280 ms |
| **Total** | **~530 ms** |

---

## Mengapa Arsitektur Ini Bekerja

### 1. **Zero-Retraining**
Berbeda dengan deep learning klasik yang perlu `fit()` ulang setiap ada data baru, sistem ini hanya:
- Menyimpan embedding sebagai **array numpy** (file `.npy`)
- Menambahkan embedding baru ke dictionary
- Membandingkan dengan cosine similarity sederhana

Tidak ada gradient descent, tidak ada backpropagation, tidak ada GPU untuk training.

### 2. **FaceNet Menciptakan Ruang Metrik Universal**
FaceNet dilatih dengan **Triplet Loss**:
```
L = Σ [ ||f(x^a) - f(x^p)||² - ||f(x^a) - f(x^n)||² + α ]₊
```

- `x^a` = Anchor (wajah referensi)
- `x^p` = Positive (wajah sama)
- `x^n` = Negative (wajah beda)
- `α` = Margin

Hasilnya: embedding dari orang yang sama berdekatan, orang berbeda berjauhan — **tanpa fine-tuning**.

### 3. **Robust terhadap Variasi Pose**
MTCNN mendapatk bounding box dan landmarks, lalu **menormalkan geometri wajah** sebelum dikirim ke FaceNet. Ini membuat embedding relatif stabil meskipun pose bervariasi (terbukti dari similarity >0.7 bahkan pada yaw ±30°).

### 4. **Confusion Matrix sebagai Decision Boundary**
Threshold τ adalah parameter yang **bisa di-tune** sesuai kebutuhan:
- **Keamanan tinggi** (presensi karyawan) → τ tinggi (0.85+), kurangi false positive
- **Kenyamanan tinggi** (absen cepat) → τ rendah (0.7), kurangi false negative

---

## Visualisasi yang Dihasilkan

| File | Deskripsi |
|------|-----------|
| `deteksi_wajah.png` | Bounding box + 5 landmarks MTCNN |
| `face_alignment.png` | Before vs After crop MTCNN |
| `deteksi_rate.png` | Detection rate per pose (bar chart) |
| `sample_embedding.png` | Vektor 512-d (10 dimensi pertama + plot) |
| `pca_space.png` | PCA 2D — clustering per subjek & per pose |
| `tsne_space.png` | t-SNE 2D — separasi embedding |
| `similarity_dist.png` | Boxplot cosine similarity per pose |
| `threshold_analysis.png` | Precision-Recall-F1 vs Threshold + histogram |
| `realtime_cm.png` | Confusion matrix real-time test |
| `latency.png` | Distribusi latency pipeline |

---

## Kesimpulan

Aplikasi presensi ini bekerja karena memanfaatkan **3 pilar utama**:

1. **MTCNN** — deteksi dan alignment wajah yang robust terhadap pose dan pencahayaan
2. **FaceNet** — embedding 512-d yang sudah terlatih pada jutaan identitas, menciptakan ruang metrik universal
3. **Cosine Similarity + Threshold** — keputusan klasifikasi sederhana namun efektif tanpa perlu retraining

Arsitektur **Zero-Retraining** membuktikan bahwa sistem pengenalan wajah dapat dibangun tanpa model machine learning yang kompleks — cukup dengan memanfaatkan representasi vektor dari model pre-trained dan metrik jarak yang tepat.

---

*Notebook eksperimen — Sistem Presensi Multi-Vector + Zero-Retraining*
*Pipeline: MTCNN → FaceNet → Cosine Similarity → Decision*
