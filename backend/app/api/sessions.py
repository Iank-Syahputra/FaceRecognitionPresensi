from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.db_service import supabase_client
from app.api.auth import get_current_user, require_professor

router = APIRouter()

class CreateSessionRequest(BaseModel):
    course_id: str

class CreateCourseRequest(BaseModel):
    course_code: str
    course_name: str
    lecturer_name: str | None = None

@router.get("/courses")
async def get_courses(current_user: dict = Depends(get_current_user)):
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

@router.post("/courses")
async def create_course(request: CreateCourseRequest, current_user: dict = Depends(require_professor)):
    try:
        lecturer_name = request.lecturer_name or current_user.get('name')
        response = supabase_client.table('courses').insert({
            "course_code": request.course_code,
            "course_name": request.course_name,
            "lecturer_name": lecturer_name,
            "lecturer_id": current_user.get('id')
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Gagal menambahkan mata kuliah baru")
            
        return {"status": "success", "data": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, current_user: dict = Depends(require_professor)):
    try:
        session_res = supabase_client.table('course_sessions').select('*, courses(*)').eq('id', session_id).execute()
        if not session_res.data:
            raise HTTPException(status_code=404, detail='Sesi tidak ditemukan')

        course = session_res.data[0].get('courses', {})
        if course.get('lecturer_id') and course.get('lecturer_id') != current_user.get('id'):
            raise HTTPException(status_code=403, detail='Anda tidak memiliki izin untuk menghapus sesi ini')

        response = supabase_client.table('course_sessions').delete().eq("id", session_id).execute()
        return {"status": "success", "message": "Riwayat absensi berhasil dihapus"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions")
async def create_session(request: CreateSessionRequest, current_user: dict = Depends(require_professor)):
    try:
        course_response = supabase_client.table('courses').select("*").eq("id", request.course_id).execute()
        if not course_response.data:
            raise HTTPException(status_code=404, detail='Mata kuliah tidak ditemukan')
        course = course_response.data[0]
        if course.get('lecturer_id') and course.get('lecturer_id') != current_user.get('id'):
            raise HTTPException(status_code=403, detail='Anda tidak memiliki izin untuk membuat sesi untuk mata kuliah ini')

        response = supabase_client.table('course_sessions').insert({
            "course_id": request.course_id,
            "status": "active"
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Gagal membuat sesi")
            
        session_id = response.data[0]['id']
        course_name = course.get('course_name', 'Mata Kuliah')
            
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
async def close_session(session_id: str, current_user: dict = Depends(require_professor)):
    try:
        session_res = supabase_client.table('course_sessions').select('*, courses(*)').eq('id', session_id).execute()
        if not session_res.data:
            raise HTTPException(status_code=404, detail='Sesi tidak ditemukan')

        course = session_res.data[0].get('courses', {})
        if course.get('lecturer_id') and course.get('lecturer_id') != current_user.get('id'):
            raise HTTPException(status_code=403, detail='Anda tidak memiliki izin untuk menutup sesi ini')

        response = supabase_client.table('course_sessions').update({
            "status": "closed"
        }).eq("id", session_id).execute()
        return {"status": "success", "message": "Sesi berhasil ditutup"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/logs")
async def get_session_logs(session_id: str, current_user: dict = Depends(get_current_user)):
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
