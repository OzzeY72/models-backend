import os, shutil
from uuid import UUID, uuid4
from fastapi import UploadFile, HTTPException
from typing import Optional, List

from sqlalchemy import Boolean
from schemas import ApplicationCreate, ApplicationUpdate
from sqlalchemy.orm import Session
from models import AgencySpa, AgencySpaApplication, Application, Master
import redis 
import json
from dotenv import load_dotenv

load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
)

async def notify_new_application(app_type: str, app_id: str, db: Session):
    model_apps_count = db.query(Application).count()
    agency_apps_count = db.query(AgencySpaApplication).count()
    total = model_apps_count + agency_apps_count

    payload = {
        "type": app_type,
        "id": str(app_id),
        "total": total,
    }
    r.publish("applications_channel", json.dumps(payload))

async def create_application_service(
    db: Session,
    name: str,
    age: int,
    phonenumber: str,
    address: Optional[str],
    height: Optional[float],
    weight: Optional[float],
    cupsize: Optional[int],
    clothsize: Optional[int],
    price_1h: Optional[float],
    price_2h: Optional[float],
    price_full_day: Optional[float],
    file: Optional[UploadFile],
    is_top: Optional[Boolean]
):
    file_name = None
    if file:
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        file_name = f"{uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    app = Application(
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
        main_photo=file_name,
        is_top=is_top
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    await notify_new_application("model", app.id, db)

    return app

def decline_application(db: Session, application_id: UUID):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise ValueError("Application not found")

    # Удаляем файл фото, если есть
    if app.main_photo:
        file_path = os.path.join(UPLOAD_DIR, app.main_photo)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.delete(app)
    db.commit()
    return {"detail": "Application declined and deleted"}

def approve_application(db: Session, application_id: UUID):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise ValueError("Application not found")

    # Создаём модель в Master
    master = Master(
        name=app.name,
        age=app.age,
        phonenumber=app.phonenumber,
        address=app.address,
        height=app.height,
        weight=app.weight,
        cupsize=app.cupsize,
        clothsize=app.clothsize,
        price_1h=app.price_1h,
        price_2h=app.price_2h,
        price_full_day=app.price_full_day,
        main_photo=app.main_photo,
        is_top=False
    )
    db.add(master)
    db.delete(app)  # удаляем анкету
    db.commit()
    db.refresh(master)
    return master

def get_applications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Application).offset(skip).limit(limit).all()

def get_application(db: Session, app_id):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        app = db.query(AgencySpaApplication).filter(AgencySpaApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

def update_application(db: Session, app_id, app_update: ApplicationUpdate):
    app = get_application(db, app_id)
    for key, value in app_update.dict(exclude_unset=True).items():
        setattr(app, key, value)
    db.commit()
    db.refresh(app)
    return app

def delete_application(db: Session, app_id):
    app = get_application(db, app_id)
    db.delete(app)
    db.commit()
    return {"detail": "Application deleted"}

def upload_application_photo(db: Session, app_id, file: UploadFile):
    app = get_application(db, app_id)
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    file_name = f"{app_id}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    app.main_photo = file_name
    db.commit()
    db.refresh(app)
    return {"filename": file_name, "url": f"/{file_path}"}

async def get_agency_spa_applications_service(db: Session):
    return db.query(AgencySpaApplication).all()

async def create_agency_spa_application_service(
    db: Session,
    name: str,
    phone: str,
    address: Optional[str],
    is_agency: bool,
    files,
):
    print(files, "54321")
    file_name = None
    if files:
        ext = os.path.splitext(files.filename)[1]
        file_name = f"{uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(files.file, buffer)

    print(file_name, "4321")

    app = AgencySpaApplication(
        name=name,
        phone=phone,
        address=address,
        is_agency=is_agency,
        photos=file_name,
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    await notify_new_application("agency", app.id, db)
    return app

async def approve_agency_spa_application_service(db: Session, application_id: UUID):
    app = db.query(AgencySpaApplication).filter(AgencySpaApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # переносим в рабочую таблицу AgencySpa
    agency_spa = AgencySpa(
        name=app.name,
        phone=app.phone,
        address=app.address,
        is_agency=app.is_agency,
        photos=app.photos,
    )
    db.add(agency_spa)
    db.delete(app)  # удаляем заявку после approve
    db.commit()
    db.refresh(agency_spa)
    return agency_spa


async def decline_agency_spa_application_service(db: Session, application_id: UUID):
    app = db.query(AgencySpaApplication).filter(AgencySpaApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(app)
    db.commit()
    return {"detail": "Application declined and removed"}
