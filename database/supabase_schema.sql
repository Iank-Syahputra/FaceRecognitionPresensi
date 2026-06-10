-- ==============================================================================
-- SKEMA DATABASE: PRESENSI COMPUTER VISION (MULTI-VECTOR ARCHITECTURE)
-- ==============================================================================

-- 1. MENGAKTIFKAN EKSTENSI PANGKALAN DATA
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. TABEL PENGGUNA / ROLES
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR NOT NULL DEFAULT 'student',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Data contoh pengguna (password contoh: admin123 / student123)
INSERT INTO users (email, name, password_hash, role) VALUES
('admin@kampus.ac.id', 'Admin Dosen', '32ffbef62097cdb80579659c20f2cde7$raG2+2fTWrb2KYgkUyilicLI7Cz7Jx5lal5VMBbjNho=', 'professor'),
('student@kampus.ac.id', 'Mahasiswa Demo', '37b1e221ca4968816501faf30d260494$xMkjyhXW02gcC/2lILX1/NwCcdhmvAerFnhwaE0Fu3Y=', 'student');

-- 3. TABEL MATA KULIAH (COURSES)
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code VARCHAR NOT NULL,
    course_name VARCHAR NOT NULL,
    lecturer_name VARCHAR NOT NULL,
    lecturer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Jika skema sudah pernah dibuat, pastikan kolom lecturer_id juga ada
ALTER TABLE IF EXISTS public.courses
ADD COLUMN IF NOT EXISTS lecturer_id UUID REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE IF EXISTS public.course_sessions
ADD COLUMN IF NOT EXISTS start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now());

ALTER TABLE IF EXISTS public.course_sessions
ADD COLUMN IF NOT EXISTS end_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now() + interval '1 hour');

-- Masukkan Data Contoh (Dummy Data)
INSERT INTO courses (course_code, course_name, lecturer_name) VALUES 
('CS101', 'Algoritma & Pemrograman', 'Budi Santoso, M.Kom'),
('CS202', 'Kecerdasan Buatan', 'Dr. Dina Amelia');

-- 4. TABEL SESI KELAS (COURSE SESSIONS)
CREATE TABLE IF NOT EXISTS course_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    session_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR DEFAULT 'active', -- 'active' atau 'closed'
    start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now()),
    end_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now() + interval '1 hour'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. TABEL IDENTITAS MAHASISWA (STUDENTS)
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nim VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. TABEL BIOMETRIK WAJAH MAHASISWA (STUDENT FACES - MULTI VECTOR)
CREATE TABLE IF NOT EXISTS student_faces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    embedding VECTOR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Membuat Index HNSW untuk pencarian vektor berkecepatan tinggi
CREATE INDEX IF NOT EXISTS student_faces_embedding_idx ON student_faces USING hnsw (embedding vector_cosine_ops);

-- 6. TABEL LOG KEHADIRAN (ATTENDANCE LOGS)
CREATE TABLE IF NOT EXISTS attendance_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    session_id UUID REFERENCES course_sessions(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(student_id, session_id) -- Mencegah 1 mahasiswa diabsen 2 kali di sesi yang sama
);

-- 7. FUNGSI PENCARIAN KEMIRIPAN WAJAH (RPC)
CREATE OR REPLACE FUNCTION match_face(
    query_embedding VECTOR(512),
    match_threshold FLOAT,
    match_count INT
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
        s.id,
        s.nim,
        s.name,
        1 - (sf.embedding <=> query_embedding) AS similarity
    FROM
        student_faces sf
    JOIN
        students s ON s.id = sf.student_id
    WHERE
        1 - (sf.embedding <=> query_embedding) > match_threshold
    ORDER BY
        sf.embedding <=> query_embedding
    LIMIT
        match_count;
END;
$$;

-- 8. MEMATIKAN ROW LEVEL SECURITY (UNTUK KEPERLUAN DEVELOPMENT)
ALTER TABLE public.courses DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.course_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.students DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.student_faces DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.attendance_logs DISABLE ROW LEVEL SECURITY;
