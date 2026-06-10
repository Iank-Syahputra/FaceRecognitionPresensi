import base64
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from PIL import Image

from app.api.auth import get_current_user
from app.services.face_service import face_service
from app.services.db_service import supabase_client
from app.core.config import settings

router = APIRouter()

class RecognizeRequest(BaseModel):
    image: str # Base64 encoded image dari kamera kelas
    session_id: str

from datetime import datetime, timedelta, timezone

def _to_utc_aware(val):
    if isinstance(val, str):
        dt = datetime.fromisoformat(val.replace('Z', '+00:00'))
        return dt.astimezone(timezone.utc)
    if isinstance(val, datetime):
        return val if val.tzinfo is not None else val.replace(tzinfo=timezone.utc)
    return None

@router.post("/recognize")
async def recognize_student(request: RecognizeRequest, current_user: dict = Depends(get_current_user)):
    if not request.image or not request.session_id:
        raise HTTPException(status_code=400, detail="Image atau Session ID kosong")

    # 1. Cek Validitas Sesi dan jendela waktu
    session_res = supabase_client.table('course_sessions').select("status,start_time,end_time").eq("id", request.session_id).execute()
    if not session_res.data:
        raise HTTPException(status_code=400, detail="Sesi kelas tidak valid atau sudah ditutup")

    session_row = session_res.data[0]
    if session_row['status'] != 'active':
        raise HTTPException(status_code=400, detail="Sesi kelas tidak valid atau sudah ditutup")

    start_time = _to_utc_aware(session_row.get('start_time'))
    end_time = _to_utc_aware(session_row.get('end_time'))
    now = datetime.now(timezone.utc)
    if not (start_time and end_time and start_time <= now <= end_time):
        raise HTTPException(status_code=400, detail="Sesi kelas saat ini tidak berada dalam rentang waktu yang valid")

    # 2. Decode Base64 Image
    try:
        b64_frame = request.image
        if "," in b64_frame:
            b64_frame = b64_frame.split(",")[1]
        image_data = base64.b64decode(b64_frame)
        image = Image.open(BytesIO(image_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal memproses gambar: {str(e)}")

    # 3. Deteksi Bounding Box untuk UI
    detection = face_service.detect_face(image)
    if not detection:
        raise HTTPException(status_code=404, detail="Tidak ada wajah terdeteksi")

    # 4. Ekstraksi Vektor
    query_embedding = face_service.extract_embedding(image)
    if query_embedding is None:
        raise HTTPException(status_code=404, detail="Gagal mengekstrak fitur wajah")

    # 5. Vector Similarity Search
    try:
        response = supabase_client.rpc(
            'match_face',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.4, 
                'match_count': 1
            }
        ).execute()
        
        matches = response.data
        
        result = {
            "box": detection["box"],
            "match": False,
            "threshold": settings.SIMILARITY_THRESHOLD
        }

        if not matches:
            return result
            
        student_match = matches[0]
        similarity = student_match['similarity']
        
        result["student"] = {
            "nim": student_match['nim'],
            "name": student_match['name'],
            "similarity": similarity
        }

        if similarity >= settings.SIMILARITY_THRESHOLD:
            result["match"] = True
            student_id = student_match['id']

            try:
                # Logika Anti-Spam sekarang diserahkan pada CONSTRAINT UNIQUE di tabel database
                supabase_client.table('attendance_logs').insert({
                    "student_id": student_id,
                    "session_id": request.session_id,
                    "similarity_score": similarity
                }).execute()
                result["already_logged"] = False
            except Exception as insert_err:
                error_str = str(insert_err).lower()
                # Tangkap error duplikat dari PostgreSQL
                if "duplicate key value" in error_str or "violates unique constraint" in error_str or "23505" in error_str:
                    result["already_logged"] = True
                else:
                    raise insert_err
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
