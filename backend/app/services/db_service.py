from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    # Memastikan URL dan Key tidak kosong sebelum inisialisasi
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL dan SUPABASE_KEY harus di-set di file .env")
        
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Instance global
supabase_client = get_supabase_client()
