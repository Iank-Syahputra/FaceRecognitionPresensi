from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import enroll, recognize, sessions

app = FastAPI(
    title="Face Recognition Attendance API",
    description="API for Zero-Retraining Face Recognition using MTCNN and FaceNet",
    version="1.0.0"
)

# Konfigurasi CORS agar frontend (SvelteKit) bisa mengakses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Ganti dengan URL frontend saat production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Face Recognition API. The server is running."}

# Menyambungkan (Include) endpoints ke aplikasi utama
app.include_router(enroll.router, prefix="/api")
app.include_router(recognize.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
