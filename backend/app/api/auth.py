from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.db_service import supabase_client
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.core.config import settings

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: dict


def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    user_response = supabase_client.table('users').select('id,email,name,role').eq('id', payload.get('sub')).execute()
    if not user_response.data:
        raise HTTPException(status_code=401, detail="User not found")

    return user_response.data[0]


def require_professor(current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'professor':
        raise HTTPException(status_code=403, detail='Akses terbatas untuk dosen saja')
    return current_user


@router.post('/auth/register', response_model=TokenResponse)
async def register_user(request: RegisterRequest):
    role = request.role.strip().lower()
    if role not in ['student', 'professor']:
        raise HTTPException(status_code=400, detail='Role harus berupa student atau professor')

    existing = supabase_client.table('users').select('id').eq('email', request.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail='Email sudah terdaftar')

    password_hash = hash_password(request.password)
    response = supabase_client.table('users').insert({
        'email': request.email,
        'name': request.name,
        'password_hash': password_hash,
        'role': role
    }).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail='Gagal membuat akun pengguna')

    user = response.data[0]
    access_token = create_access_token({'sub': user['id'], 'role': user['role']}, settings.ACCESS_TOKEN_EXPIRE_SECONDS)

    return {'access_token': access_token, 'user': {'id': user['id'], 'email': user['email'], 'name': user['name'], 'role': user['role']}}


@router.post('/auth/login', response_model=TokenResponse)
async def login_user(request: LoginRequest):
    response = supabase_client.table('users').select('id,email,name,role,password_hash').eq('email', request.email).execute()
    if not response.data:
        raise HTTPException(status_code=401, detail='Email atau password salah')

    user = response.data[0]
    if not verify_password(request.password, user['password_hash']):
        raise HTTPException(status_code=401, detail='Email atau password salah')

    access_token = create_access_token({'sub': user['id'], 'role': user['role']}, settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    return {'access_token': access_token, 'user': {'id': user['id'], 'email': user['email'], 'name': user['name'], 'role': user['role']}}


@router.get('/auth/me')
async def me(current_user: dict = Depends(get_current_user)):
    return {'status': 'success', 'user': current_user}
