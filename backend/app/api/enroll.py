import base64
from io import BytesIO
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from PIL import Image

from app.services.face_service import face_service
from app.services.db_service import supabase_client

router = APIRouter()

class EnrollmentRequest(BaseModel):
    nim: str
    name: str
    frames: list[str] # List of base64 encoded images

class ValidateRequest(BaseModel):
    image: str
    expected_pose: str

@router.post("/validate")
async def validate_pose(request: ValidateRequest):
    if not request.image:
        return {"valid": False, "message": "Frame kosong"}
        
    try:
        b64_frame = request.image
        if "," in b64_frame:
            b64_frame = b64_frame.split(",")[1]
            
        image_data = base64.b64decode(b64_frame)
        image = Image.open(BytesIO(image_data))
        
        result = face_service.validate_face_pose(image, request.expected_pose)
        return result
    except Exception as e:
        return {"valid": False, "message": "Gagal memproses frame."}

@router.post("/enroll")
async def enroll_student(request: EnrollmentRequest):
    if not request.frames:
        raise HTTPException(status_code=400, detail="Tidak ada frame gambar yang diterima")

    embeddings = []
    
    # 1. Ekstraksi vektor untuk setiap frame (Multi-pose)
    for idx, b64_frame in enumerate(request.frames):
        try:
            if "," in b64_frame:
                b64_frame = b64_frame.split(",")[1]
            image_data = base64.b64decode(b64_frame)
            image = Image.open(BytesIO(image_data))
            
            embedding = face_service.extract_embedding(image)
            if embedding is not None:
                embeddings.append(embedding)
        except Exception as e:
            continue

    if not embeddings:
        raise HTTPException(status_code=400, detail="Wajah tidak terdeteksi pada frame pendaftaran.")

    try:
        # 2. Cek apakah NIM sudah ada atau buat record baru di tabel students
        student_response = supabase_client.table('students').select("id").eq("nim", request.nim).execute()
        
        if student_response.data:
            student_id = student_response.data[0]['id']
            # Opsional: Hapus wajah lama jika mahasiswa ini mendaftar ulang
            supabase_client.table('student_faces').delete().eq("student_id", student_id).execute()
        else:
            # Mahasiswa baru
            new_student = supabase_client.table('students').insert({
                "nim": request.nim,
                "name": request.name
            }).execute()
            student_id = new_student.data[0]['id']

        # 3. Simpan SEMUA vektor (Multi-Vector) ke tabel student_faces
        face_records = [{"student_id": student_id, "embedding": emb} for emb in embeddings]
        supabase_client.table('student_faces').insert(face_records).execute()
        
        return {"status": "success", "message": f"Berhasil mendaftarkan biometrik {request.name} dengan {len(embeddings)} titik identitas."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
