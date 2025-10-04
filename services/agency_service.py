from http.client import HTTPException
import os
from typing import List
from uuid import UUID, uuid4
from schemas import AgencySpaCreate, AgencySpaUpdate, MasterCreate
from sqlalchemy.orm import Session

from fastapi import UploadFile

from models import AgencySpa, Master
from utils import delete_files, save_files

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_agencies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AgencySpa).offset(skip).limit(limit).all()

def get_agencies_agency(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AgencySpa).filter(AgencySpa.is_agency == True).offset(skip).limit(limit).all()

def get_agencies_spa(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AgencySpa).filter(AgencySpa.is_agency == False).offset(skip).limit(limit).all()

def get_agency(db: Session, agency_id: UUID):
    agency = db.query(AgencySpa).filter(AgencySpa.id == agency_id).first()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency/SPA not found")
    return agency

async def create_master_in_agency(
    db: Session,
    agency_id: UUID,
    create_master: MasterCreate,
    files: List[UploadFile]
):
    saved_files = save_files(files)

    agency = db.query(AgencySpa).filter(AgencySpa.id == agency_id).first()
    if not agency:
        raise ValueError("Agency/Spa not found")

    master = Master(
        **create_master.model_dump(),
        agency_spa=agency,
        photos=saved_files
    )
    db.add(master)
    db.commit()
    db.refresh(master)
    return master

def create_agency(db: Session, agency_create: AgencySpaCreate, files: List[UploadFile] = []):
    saved_files = save_files(files)

    agency = AgencySpa(
        **agency_create.model_dump(),
        photos=saved_files,
    )
    db.add(agency)
    db.commit()
    db.refresh(agency)
    return agency

def update_agency(db: Session, agency_id: UUID, agency_update: AgencySpaUpdate):
    agency = get_agency(db, agency_id)
    for key, value in agency_update.model_dump(exclude_unset=True).items():
        setattr(agency, key, value)
    db.commit()
    db.refresh(agency)
    return agency

def delete_agency(db: Session, agency_id: UUID):
    agency = get_agency(db, agency_id)
    delete_files(agency.photos)

    db.delete(agency)
    db.commit()
    return {"detail": "Agency/SPA deleted"}