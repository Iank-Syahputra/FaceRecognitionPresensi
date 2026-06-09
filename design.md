# DESIGN GUIDELINES & UI ARCHITECTURE
**Proyek:** Sistem Presensi Zero-Retraining Berbasis 2D End-to-End Deep Learning
**Lingkungan:** Kampus / Akademik
**Tech Stack UI:** SvelteKit + Tailwind CSS

---

## 1. Color Palette (Design Tokens)
Sistem menggunakan palet warna bernuansa *Deep Blue* hingga *Ice Blue* untuk menciptakan kesan antarmuka yang bersih, futuristik, dan fokus pada data. Warna-warna ini diambil langsung dari referensi desain utama.

| Peran | Hex Code | Penggunaan Utama pada Komponen SvelteKit |
| :--- | :--- | :--- |
| **Navy Black** | `#011025` | Teks utama (heading/body), *sidebar background* (opsi *dark mode*), ikon navigasi aktif. |
| **Deep Blue** | `#052659` | *Primary brand color*. Digunakan untuk *Header/Navbar*, tombol utama (*Primary Button*), dan teks penekanan. |
| **Steel Blue** | `#5482B4` | *Secondary action*. Warna untuk *bounding box* kamera saat mendeteksi wajah, *hover state* pada tombol, dan elemen grafik/chart. |
| **Muted Blue** | `#7EA0C5` | Teks sekunder, *borders* pada tabel data mahasiswa, garis pemisah (*divider*), dan *placeholder* input form. |
| **Ice Blue** | `#C2E8FF` | *Background* utama aplikasi (*Light mode*), latar belakang kartu (*Card bg*), dan efek *highlight* baris tabel saat di-hover. |

*(Catatan Semantic: Tambahkan warna utilitas standar Tailwind seperti `emerald-500` untuk notifikasi "Kehadiran Berhasil" dan `rose-500` untuk "Wajah Tidak Dikenali").*

---

## 2. Tailwind Configuration (`tailwind.config.js`)
Implementasi palet warna ke dalam konfigurasi Tailwind CSS agar siap digunakan di seluruh komponen Svelte.

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'campus-navy': '#011025',
        'campus-primary': '#052659',
        'campus-secondary': '#5482B4',
        'campus-muted': '#7EA0C5',
        'campus-surface': '#C2E8FF',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'], // Tipografi yang bersih dan mudah dibaca di layar
        mono: ['Fira Code', 'monospace'], // Untuk menampilkan data log/NIM
      }
    }
  },
  plugins: []
};