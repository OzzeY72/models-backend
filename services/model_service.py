import os
import shutil 
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from models import Master
from schemas import MasterCreate, MasterResponse, MasterUpdate

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def create_master_service(
    db: Session,
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
    file,
):
    file_name = None
    if file:
        ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

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
    name: Optional[str] = None,
    age: Optional[int] = None,
    city: Optional[str] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    cupsize: Optional[int] = None,
    clothsize: Optional[int] = None,
    price_1h: Optional[float] = None,
    price_full_day: Optional[float] = None,
    is_top: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[MasterResponse]:
    query = db.query(Master)

    if name:
        query = query.filter(Master.name.ilike(f"%{name}%"))
    if age is not None:
        query = query.filter(Master.age == age)
    if city:
        query = query.filter(Master.address.ilike(f"%{city}%"))
    if height is not None:
        query = query.filter(Master.height == height)
    if weight is not None:
        query = query.filter(Master.weight == weight)
    if cupsize is not None:
        query = query.filter(Master.cupsize == cupsize)
    if clothsize is not None:
        query = query.filter(Master.clothsize == clothsize)
    if price_1h is not None:
        query = query.filter(Master.price_1h == price_1h)
    if price_full_day is not None:
        query = query.filter(Master.price_full_day == price_full_day)
    if is_top is not None:
        query = query.filter(Master.is_top == is_top)

    return query.offset(skip).limit(limit).all()

def get_master(db: Session, master_id: UUID):
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master not found")
    return master


def update_master(db: Session, master_id: UUID, master_update: MasterUpdate):
    master = get_master(db, master_id)
    for key, value in master_update.dict(exclude_unset=True).items():
        setattr(master, key, value)
    db.commit()
    db.refresh(master)
    return master


def delete_master(db: Session, master_id: UUID):
    master = get_master(db, master_id)
    db.delete(master)
    db.commit()
    return {"detail": "Master deleted"}


def upload_photo(db: Session, master_id: UUID, file: UploadFile):
    master = get_master(db, master_id)

    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    file_name = f"{master_id}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    master.main_photo = file_name
    db.commit()
    db.refresh(master)

    return {"filename": file_name, "url": f"/{file_path}"}
