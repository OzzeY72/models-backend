from http.client import HTTPException
import os
import shutil
from typing import List
from uuid import UUID, uuid4
from schemas import AgencySpaCreate, AgencySpaUpdate
from sqlalchemy.orm import Session

from fastapi import UploadFile

from models import AgencySpa, Master

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
    name: str,
    age: int,
    phonenumber: str,
    address: str,
    height: float,
    weight: float,
    cupsize: int,
    clothsize: int,
    price_1h: float,
    price_2h: float,
    price_full_day: float,
    is_top: bool,
    file = None,
):
    file_name = None
    if file:
        ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    agency = db.query(AgencySpa).filter(AgencySpa.id == agency_id).first()
    if not agency:
        raise ValueError("Agency/Spa not found")

    master = Master(
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
        main_photo=file_name,
        agency_spa=agency
    )
    db.add(master)
    db.commit()
    db.refresh(master)
    return master

def create_agency(db: Session, agency_create: AgencySpaCreate, files: List[UploadFile] = []):
    photo_names = []
    for file in files:
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        file_name = f"{uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        photo_names.append(file_name)

    agency = AgencySpa(
        name=agency_create.name,
        phone=agency_create.phone,
        address=agency_create.address,
        is_agency=agency_create.is_agency,
        photos=photo_names,
    )
    db.add(agency)
    db.commit()
    db.refresh(agency)
    return agency

def update_agency(db: Session, agency_id: UUID, agency_update: AgencySpaUpdate):
    agency = get_agency(db, agency_id)
    for key, value in agency_update.dict(exclude_unset=True).items():
        setattr(agency, key, value)
    db.commit()
    db.refresh(agency)
    return agency

def delete_agency(db: Session, agency_id: UUID):
    agency = get_agency(db, agency_id)
    db.delete(agency)
    db.commit()
    return {"detail": "Agency/SPA deleted"}