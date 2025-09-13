from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Security
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from dotenv import load_dotenv
from fastapi.security import APIKeyHeader

import os
import shutil

from models import Base, Master
from schemas import MasterCreate, MasterUpdate, MasterResponse
from database import SessionLocal, engine

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_token(api_key: str = Security(api_key_header)):
  if api_key != SECRET_TOKEN:
    raise HTTPException(status_code=403, detail="Forbidden")
  return api_key

load_dotenv()
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

# CREATE
@app.post("/masters/", response_model=MasterResponse)
def create_master(
  master: MasterCreate, 
  db: Session = Depends(get_db),
  token: str = Depends(verify_token)
):
  db_master = Master(**master.dict())
  db.add(db_master)
  db.commit()
  db.refresh(db_master)
  return db_master

# READ ALL
@app.get("/masters/", response_model=List[MasterResponse])
def read_masters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(verify_token)):
  return db.query(Master).offset(skip).limit(limit).all()

# READ ONE
@app.get("/masters/{master_id}", response_model=MasterResponse)
def read_master(master_id: UUID, db: Session = Depends(get_db), token: str = Depends(verify_token)):
  master = db.query(Master).filter(Master.id == master_id).first()
  if not master:
    raise HTTPException(status_code=404, detail="Master not found")
  return master

# UPDATE
@app.put("/masters/{master_id}", response_model=MasterResponse)
def update_master(master_id: UUID, master_update: MasterUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
  master = db.query(Master).filter(Master.id == master_id).first()
  if not master:
    raise HTTPException(status_code=404, detail="Master not found")
  for key, value in master_update.dict(exclude_unset=True).items():
    setattr(master, key, value)
  db.commit()
  db.refresh(master)
  return master

# DELETE
@app.delete("/masters/{master_id}")
def delete_master(master_id: UUID, db: Session = Depends(get_db), token: str = Depends(verify_token)):
  master = db.query(Master).filter(Master.id == master_id).first()
  if not master:
    raise HTTPException(status_code=404, detail="Master not found")
  db.delete(master)
  db.commit()
  return {"detail": "Master deleted"}

@app.post("/masters/{master_id}/upload_photo/")
def upload_photo(
    master_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
  master = db.query(Master).filter(Master.id == master_id).first()
  if not master:
    raise HTTPException(status_code=404, detail="Master not found")

  file_ext = os.path.splitext(file.filename)[1]  # например, ".jpg"
  file_name = f"{master_id}{file_ext}"
  file_path = os.path.join(UPLOAD_DIR, file_name)

  with open(file_path, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)

  # save path to db as main_photo
  master.main_photo = file_path
  db.commit()
  db.refresh(master)

  return {"filename": file_name, "url": f"/{file_path}"}
