from re import S
import os, shutil
from uuid import UUID, uuid4
from fastapi import UploadFile, HTTPException
from typing import Optional, List

from sqlalchemy import Boolean
from schemas import AgencySpaApplicationCreate, ApplicationCreate, ApplicationUpdate
from sqlalchemy.orm import Session
from models import AgencySpa, AgencySpaApplication, Application, Master
import redis 
import json
from dotenv import load_dotenv

from utils import delete_file, delete_files, save_files

load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

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
    create_application: ApplicationCreate,
    files: Optional[UploadFile],
):
    saved_files = save_files(files)

    app = Application(
        **create_application.model_dump(),
        photos=saved_files,
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

    delete_files(app.photos)

    db.delete(app)
    db.commit()
    return {"detail": "Application declined and deleted"}

def approve_application(db: Session, application_id: UUID):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise ValueError("Application not found")

    # Создаём модель в Master
    master = Master(
        id = app.id,
        name = app.name,
        age = app.age,
        phonenumber = app.phonenumber,
        address = app.address,
        height = app.height,
        weight = app.weight,
        cupsize = app.cupsize,
        bodytype = app.bodytype,
        price_1h = app.price_1h,
        price_2h = app.price_2h,
        price_full_day = app.price_full_day,
        description = app.description,
        photos = app.photos,
        is_top = app.is_top
    )
    db.add(master)
    db.delete(app)
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

def update_application(db: Session, app_id, app_update: ApplicationUpdate, files: List[UploadFile] = []):
    app = get_application(db, app_id)
    for key, value in app_update.model_dump(exclude_unset=True).items():
        setattr(app, key, value)
        
    saved_files = save_files(files)
    app.photos = app.photos + saved_files
    
    db.commit()
    db.refresh(app)
    return app

def delete_application(db: Session, app_id):
    app = get_application(db, app_id)
    db.delete(app)
    db.commit()
    return {"detail": "Application deleted"}

async def get_agency_spa_applications_service(db: Session):
    return db.query(AgencySpaApplication).all()

async def create_agency_spa_application_service(
    db: Session,
    create_agency_application: AgencySpaApplicationCreate,
    files: List[UploadFile] = []
):
    saved_files = save_files(files)
    
    app = AgencySpaApplication(
        **create_agency_application.model_dump(),
        photos=saved_files,
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
