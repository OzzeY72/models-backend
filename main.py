from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Security, Form, Query
import services.model_service as model_service
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from dotenv import load_dotenv
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles

import os
import shutil

from models import Base, Master
from schemas import MasterCreate, MasterUpdate, MasterResponse
from database import SessionLocal, engine, get_db

from routers.agencies_router import router as agencies_router 
from routers.application_router import router as application_router

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

load_dotenv()
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

def verify_token(api_key: str = Security(api_key_header)):
  if api_key != SECRET_TOKEN:
    raise HTTPException(status_code=403, detail="Forbidden")
  return api_key

Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/masters/by_spa/{spa_id}", response_model=List[MasterResponse])
def read_masters_by_spa(spa_id: str, db: Session = Depends(get_db)):
    try:
        masters = model_service.get_masters_by_spa(db, spa_id)
        return masters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/masters/", response_model=MasterResponse)
async def create_master(
    name: str = Form(...),
    age: int = Form(...),
    phonenumber: str = Form(...),
    address: Optional[str] = Form(None),
    height: Optional[float] = Form(None),
    weight: Optional[float] = Form(None),
    cupsize: Optional[int] = Form(None),
    clothsize: Optional[int] = Form(None),
    price_1h: Optional[float] = Form(None),
    price_2h: Optional[float] = Form(None),
    price_full_day: Optional[float] = Form(None),
    is_top: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
  return await model_service.create_master_service(
      db=db,
      name=name,
      age=age,
      phonenumber=phonenumber,
      address=address,
      height=height,
      weight=weight,
      cupsize=cupsize,
      clothsize=clothsize,
      price_1h=price_1h,
      price_2h=price_2h,
      price_full_day=price_full_day,
      is_top=is_top,
      file=file,
  )

@app.get("/masters/", response_model=List[MasterResponse])
def read_masters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return model_service.get_masters(db, skip, limit)

@app.get("/top/", response_model=List[MasterResponse])
def read_top_masters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return model_service.get_masters_top(db, skip, limit)

@app.get("/regular/", response_model=List[MasterResponse])
def read_regular_masters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return model_service.get_masters_regular(db, skip, limit)

@app.get("/masters/search", response_model=List[MasterResponse])
def search_masters_route(
    name: Optional[str] = Query(None),
    age: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    height: Optional[float] = Query(None),
    weight: Optional[float] = Query(None),
    cupsize: Optional[int] = Query(None),
    clothsize: Optional[int] = Query(None),
    price_1h: Optional[float] = Query(None),
    price_full_day: Optional[float] = Query(None),
    is_top: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return model_service.search_masters(
        db,
        name=name,
        age=age,
        city=city,
        height=height,
        weight=weight,
        cupsize=cupsize,
        clothsize=clothsize,
        price_1h=price_1h,
        price_full_day=price_full_day,
        is_top=is_top,
        skip=skip,
        limit=limit
    )

@app.get("/masters/{master_id}", response_model=MasterResponse)
def read_master(master_id: UUID, db: Session = Depends(get_db)):
    return model_service.get_master(db, master_id)

@app.put("/masters/{master_id}", response_model=MasterResponse)
def update_master(master_id: UUID, master_update: MasterUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return model_service.update_master(db, master_id, master_update)

@app.delete("/masters/{master_id}")
def delete_master(master_id: UUID, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return model_service.delete_master(db, master_id)

@app.post("/masters/{master_id}/upload_photo/")
def upload_photo(master_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return model_service.upload_photo(db, master_id, file)

app.include_router(agencies_router)
app.include_router(application_router)

app.mount("/static", StaticFiles(directory="uploads"), name="static")

