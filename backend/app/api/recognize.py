import base64
from datetime import datetime, timezone
from io import BytesIO

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from PIL import Image

from app.services.face_service import face_service
from app.services.db_service import supabase_client
from app.core.config import settings

router = APIRouter()

class RecognizeRequest(BaseModel):
    image: str
    session_id: str

def _ensure_datetime(value):
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value

@router.post("/recognize")
async def recognize_student(request: RecognizeRequest):
    if not request.image or not request.session_id:
        raise HTTPException(status_code=400, detail="Image atau Session ID kosong")

    # 1. Cek Validitas Sesi dan waktu
    session_res = supabase_client.table('course_sessions').select("status, start_at, end_at").eq("id", request.session_id).execute()
    if not session_res.data:
        raise HTTPException(status_code=400, detail="Sesi kelas tidak valid atau sudah ditutup")

    session_data = session_res.data[0]
    if session_data['status'] != 'active':
        raise HTTPException(status_code=400, detail="Sesi kelas tidak valid atau sudah ditutup")

    start_at = _ensure_datetime(session_data.get("start_at"))
    end_at = _ensure_datetime(session_data.get("end_at"))
    now = datetime.now(timezone.utc)

    if start_at and start_at.tzinfo is None:
        start_at = start_at.replace(tzinfo=timezone.utc)
    if end_at and end_at.tzinfo is None:
        end_at = end_at.replace(tzinfo=timezone.utc)

    if start_at and now < start_at:
        raise HTTPException(status_code=400, detail="Sesi belum dimulai")
    if end_at and now > end_at:
        raise HTTPException(status_code=400, detail="Sesi sudah berakhir")

    # 2. Decode Base64 Image
    try:
        b64_frame = request.image
        if "," in b64_frame:
            b64_frame = b64_frame.split(",")[1]
        image_data = base64.b64decode(b64_frame)
        image = Image.open(BytesIO(image_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal memproses gambar: {str(e)}")

    # 3. Deteksi wajah
    detection = face_service.detect_face(image)
    if not detection:
        raise HTTPException(status_code=404, detail="Tidak ada wajah terdeteksi")

    # 4. Ekstraksi embedding
    query_embedding = face_service.extract_embedding(image)
    if query_embedding is None:
        raise HTTPException(status_code=404, detail="Gagal mengekstrak fitur wajah")

    # 5. Pencarian kemiripan wajah
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
                supabase_client.table('attendance_logs').insert({
                    "student_id": student_id,
                    "session_id": request.session_id,
                    "similarity_score": similarity
                }).execute()
                result["already_logged"] = False
            except Exception as insert_err:
                error_str = str(insert_err).lower()
                if "duplicate key value" in error_str or "violates unique constraint" in error_str or "23505" in error_str:
                    result["already_logged"] = True
                else:
                    raise insert_err

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")