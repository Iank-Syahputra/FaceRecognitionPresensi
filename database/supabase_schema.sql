-- 1. Mengaktifkan ekstensi pgvector (wajib untuk tipe data vektor)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Membuat tabel Master Identitas (students)
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nim VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    -- Menyimpan vektor ekstraksi FaceNet berukuran 512 dimensi
    face_embedding VECTOR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Membuat Index untuk mempercepat pencarian (Vector Similarity Search)
-- Menggunakan HNSW (Hierarchical Navigable Small World) index yang direkomendasikan pgvector untuk performa dan akurasi tinggi.
-- `vector_cosine_ops` digunakan karena kita akan mengukur jarak dengan Cosine Similarity.
CREATE INDEX IF NOT EXISTS students_face_embedding_idx ON students USING hnsw (face_embedding vector_cosine_ops);

-- 4. Membuat tabel Transaksi Presensi (attendance_logs)
CREATE TABLE IF NOT EXISTS attendance_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Membuat Fungsi RPC (Remote Procedure Call) untuk pencarian wajah
-- Fungsi ini akan dipanggil oleh backend FastAPI untuk membandingkan vektor dari kamera dengan database.
CREATE OR REPLACE FUNCTION match_face(
    query_embedding VECTOR(512), -- Vektor hasil ekstraksi dari kamera saat presensi
    match_threshold FLOAT,       -- Batas minimal kemiripan (misal: 0.85)
    match_count INT              -- Jumlah hasil maksimal yang dikembalikan (biasanya 1 untuk presensi)
)
RETURNS TABLE (
    id UUID,
    nim VARCHAR,
    name VARCHAR,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        students.id,
        students.nim,
        students.name,
        -- Kalkulasi Cosine Similarity:
        -- Operator <=> mengembalikan "Cosine Distance" (Jarak Kosinus).
        -- Cosine Similarity = 1 - Cosine Distance.
        1 - (students.face_embedding <=> query_embedding) AS similarity
    FROM
        students
    WHERE
        -- Hanya kembalikan yang nilai similarity-nya di atas ambang batas (threshold)
        1 - (students.face_embedding <=> query_embedding) > match_threshold
    ORDER BY
        -- Urutkan berdasarkan jarak terdekat (paling mirip)
        students.face_embedding <=> query_embedding
    LIMIT
        match_count;
END;
$$;
