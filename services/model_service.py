import os
import shutil 
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, UploadFile

from models import BodyType, Master
from schemas import MasterCreate, MasterResponse, MasterSearch, MasterUpdate
from utils import save_files

async def create_master_service(
    db: Session,
    create_master: MasterCreate,
    files: List[UploadFile],
):
    saved_files = save_files(files)
    master = Master(
        **create_master.model_dump(), photos=saved_files
    )
    db.add(master)
    db.commit()
    db.refresh(master)
    return master

def get_masters_by_spa(db: Session, spa_id: UUID) -> List[Master]:
    return db.query(Master).filter(Master.agency_spa_id == spa_id).all()

def get_masters(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Master).offset(skip).limit(limit).all()
def get_masters_top(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Master).filter(Master.agency_spa_id == None).filter(Master.is_top == True).offset(skip).limit(limit).all()

def get_masters_regular(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Master).filter(Master.agency_spa_id == None).filter(Master.is_top == False).offset(skip).limit(limit).all()

def search_masters(
    db: Session,
    search: MasterSearch,
    skip: int = 0,
    limit: int = 100
) -> List[MasterResponse]:
    query = db.query(Master)

    if search.age_from is not None:
        query = query.filter(Master.age >= search.age_from)
    if search.age_to is not None:
        query = query.filter(Master.age <= search.age_to)
    if search.height_from is not None:
        query = query.filter(Master.height >= search.height_from)
    if search.height_to is not None:
        query = query.filter(Master.height <= search.height_to)
    if search.cupsize is not None:
        query = query.filter(Master.cupsize == search.cupsize)
    if search.bodytype is not None:
        query = query.filter(Master.bodytype == search.bodytype)

    return query.offset(skip).limit(limit).all()

def get_master(db: Session, master_id: UUID):
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master not found")
    return master

def update_master(db: Session, master_id: UUID, master_update: MasterUpdate, files: List[UploadFile]):
    master = get_master(db, master_id)
    for key, value in master_update.model_dump(exclude_unset=True).items():
        setattr(master, key, value)

    saved_files = save_files(files)
    # master.photos = master.photos + saved_files
    # Temporary solution: replace all photos with new ones
    master.photos = saved_files
    
    db.commit()
    db.refresh(master)
    return master

def delete_master(db: Session, master_id: UUID):
    master = get_master(db, master_id)
    db.delete(master)
    db.commit()
    return {"detail": "Master deleted"}
