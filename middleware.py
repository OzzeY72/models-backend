from datetime import timedelta, datetime
import datetime
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Security, Request
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

load_dotenv()
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        telegram_id: str = payload.get("telegram_id")
        phone: str = payload.get("phonenumber")
        if telegram_id is None or phone is None:
            raise JWTError()
        return {"telegram_id": telegram_id, "phonenumber": phone}
    except JWTError:
        return None

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def auth_middleware(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    """
    Универсальная проверка:
    - Если есть X-API-KEY и он совпадает с SECRET_TOKEN → пропускаем.
    - Иначе проверяем JWT в Authorization: Bearer <token>
    """
    # 🔐 1. Проверяем X-API-KEY
    api_key = request.headers.get("X-API-KEY")
    if api_key and api_key == SECRET_TOKEN:
        return {"type": "system"}

    # 🧾 2. Проверяем JWT Bearer токен
    if credentials:
        token = credentials.credentials
        try:
            user_data = verify_access_token(token)
            return {"type": "user", "user": {**user_data}}
        except JWTError:
            raise HTTPException(status_code=403, detail="Invalid or expired token")

    # ❌ Ни API-KEY, ни JWT не пришёл
    raise HTTPException(status_code=403, detail="Authorization required")

# def jwt_auth(credentials: HTTPAuthorizationCredentials = Security(security)):
#     token = credentials.credentials
#     user_data = verify_access_token(token)
#     if not user_data:
#         raise HTTPException(status_code=403, detail="Invalid or expired token")
#     return user_data

def verify_token(api_key: str = Security(api_key_header)):
  if api_key != SECRET_TOKEN:
    raise HTTPException(status_code=403, detail="Forbidden")
  return api_key
