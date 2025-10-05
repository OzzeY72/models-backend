from fastapi import APIRouter, FastAPI, HTTPException, Depends, UploadFile, File, Query
from middleware import verify_token
import services.model_service as model_service
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from schemas import MasterBase, MasterCreate, MasterSearch, MasterUpdate, MasterResponse
from database import get_db

router = APIRouter()

@router.get("/masters/by_spa/{spa_id}", response_model=List[MasterResponse])
def read_masters_by_spa(spa_id: str, db: Session = Depends(get_db)):
    try:
        masters = model_service.get_masters_by_spa(db, spa_id)
        return masters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/masters/", response_model=MasterResponse)
async def create_master(
    master: MasterCreate = Depends(MasterCreate.as_form),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
  return await model_service.create_master_service(
      db=db,
      create_master=master,
      files=files
  )

@router.get("/masters/", response_model=List[MasterResponse])
def read_masters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return model_service.get_masters(db, skip, limit)

@router.get("/top/", response_model=List[MasterResponse])
def read_top_masters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return model_service.get_masters_top(db, skip, limit)

@router.get("/regular/", response_model=List[MasterResponse])
def read_regular_masters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return model_service.get_masters_regular(db, skip, limit)

@router.get("/masters/search", response_model=List[MasterResponse])
def search_masters_route(
    search: MasterSearch = Depends(),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return model_service.search_masters(
        db,
        search=search,
        skip=skip,
        limit=limit
    )

@router.get("/masters/{master_id}", response_model=MasterResponse)
def read_master(master_id: UUID, db: Session = Depends(get_db)):
    return model_service.get_master(db, master_id)

@router.put("/masters/{master_id}", response_model=MasterResponse)
def update_master(
    master_id: UUID, 
    master_update: MasterUpdate = Depends(MasterUpdate.as_form), 
    files: List[UploadFile] = File([]), 
    db: Session = Depends(get_db), 
    token: str = Depends(verify_token)
):
    return model_service.update_master(db, master_id, master_update, files)

@router.delete("/masters/{master_id}")
def delete_master(master_id: UUID, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return model_service.delete_master(db, master_id)

