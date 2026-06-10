from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.db_service import supabase_client

router = APIRouter()

class CreateSessionRequest(BaseModel):
    course_id: str
    start_at: datetime
    end_at: datetime

class CreateCourseRequest(BaseModel):
    course_code: str
    course_name: str
    lecturer_name: str

def _ensure_datetime(value):
    if value is None:
        return None
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return value

@router.get("/courses")
async def get_courses():
    try:
        response = supabase_client.table('courses').select("*, course_sessions(*, attendance_logs(count))").order('created_at', foreign_table='course_sessions', desc=True).execute()
        courses = response.data
        for course in courses:
            for session in course.get("course_sessions", []):
                count_data = session.get("attendance_logs", [])
                session["attendance_count"] = count_data[0]["count"] if count_data else 0
                if "attendance_logs" in session:
                    del session["attendance_logs"]
        return {"status": "success", "data": courses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/courses")
async def create_course(request: CreateCourseRequest):
    try:
        response = supabase_client.table('courses').insert({
            "course_code": request.course_code,
            "course_name": request.course_name,
            "lecturer_name": request.lecturer_name
        }).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Gagal menambahkan mata kuliah baru")

        return {"status": "success", "data": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    try:
        response = supabase_client.table('course_sessions').delete().eq("id", session_id).execute()
        return {"status": "success", "message": "Riwayat absensi berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions")
async def create_session(request: CreateSessionRequest):
    try:
        if request.end_at <= request.start_at:
            raise HTTPException(status_code=400, detail="Waktu selesai harus lebih besar dari waktu mulai")

        response = supabase_client.table('course_sessions').insert({
            "course_id": request.course_id,
            "start_at": request.start_at.isoformat(),
            "end_at": request.end_at.isoformat(),
            "status": "active"
        }).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Gagal membuat sesi")

        session_id = response.data[0]['id']
        course_response = supabase_client.table('courses').select("*").eq("id", request.course_id).execute()
        course_name = course_response.data[0]['course_name'] if course_response.data else "Mata Kuliah"

        return {
            "status": "success",
            "data": response.data[0],
            "course_name": course_name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/close")
async def close_session(session_id: str):
    try:
        response = supabase_client.table('course_sessions').update({
            "status": "closed"
        }).eq("id", session_id).execute()
        return {"status": "success", "message": "Sesi berhasil ditutup"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/logs")
async def get_session_logs(session_id: str):
    try:
        session_res = supabase_client.table('course_sessions').select("*, courses(*)").eq("id", session_id).execute()
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Sesi tidak ditemukan")

        logs_res = supabase_client.table('attendance_logs').select("*, students(nim, name)").eq("session_id", session_id).order("timestamp", desc=True).execute()

        return {
            "status": "success",
            "session": session_res.data[0],
            "logs": logs_res.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))