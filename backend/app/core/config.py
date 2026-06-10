import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
    SECRET_KEY = os.environ.get("SECRET_KEY", "replace-with-a-secure-key")
    ACCESS_TOKEN_EXPIRE_SECONDS = int(os.environ.get("ACCESS_TOKEN_EXPIRE_SECONDS", "3600"))
    
    # Threshold kemiripan (0-1). Semakin tinggi, semakin ketat
    SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD", "0.85"))

settings = Settings()
