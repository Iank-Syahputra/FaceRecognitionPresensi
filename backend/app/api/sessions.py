from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.db_service import supabase_client

router = APIRouter()

class CreateSessionRequest(BaseModel):
    course_id: str

@router.get("/courses")
async def get_courses():
    try:
        # Mengambil mata kuliah beserta sesi dan jumlah absennya, diurutkan berdasarkan waktu pembuatan sesi terbaru
        response = supabase_client.table('courses').select("*, course_sessions(*, attendance_logs(count))").order('created_at', foreign_table='course_sessions', desc=True).execute()
        
        # Merapikan hasil data agar mudah dibaca oleh frontend
        courses = response.data
        for course in courses:
            for session in course.get("course_sessions", []):
                # Ekstrak nilai count dari array [{'count': X}]
                count_data = session.get("attendance_logs", [])
                session["attendance_count"] = count_data[0]["count"] if count_data else 0
                # Hapus array log mentah untuk menghemat bandwidth
                if "attendance_logs" in session:
                    del session["attendance_logs"]
                    
        return {"status": "success", "data": courses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    try:
        # Menghapus sesi akan otomatis menghapus log absensi di dalamnya karena CASCADE di database
        response = supabase_client.table('course_sessions').delete().eq("id", session_id).execute()
        return {"status": "success", "message": "Riwayat absensi berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions")
async def create_session(request: CreateSessionRequest):
    try:
        response = supabase_client.table('course_sessions').insert({
            "course_id": request.course_id,
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
        # Mengambil informasi sesi dan mata kuliah
        session_res = supabase_client.table('course_sessions').select("*, courses(*)").eq("id", session_id).execute()
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Sesi tidak ditemukan")
            
        # Mengambil data log absensi beserta relasi data mahasiswa
        logs_res = supabase_client.table('attendance_logs').select("*, students(nim, name)").eq("session_id", session_id).order("timestamp", desc=True).execute()
        
        return {
            "status": "success",
            "session": session_res.data[0],
            "logs": logs_res.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
