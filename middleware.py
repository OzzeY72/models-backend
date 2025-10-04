

import os
from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

load_dotenv()
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

def verify_token(api_key: str = Security(api_key_header)):
  if api_key != SECRET_TOKEN:
    raise HTTPException(status_code=403, detail="Forbidden")
  return api_key
