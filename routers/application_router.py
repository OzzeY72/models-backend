from http.client import HTTPException
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from database import get_db
from middleware import auth_middleware, verify_token
from models import AgencySpa, AgencySpaApplication, Application, Master, WorkUser
from schemas import AgencySpaApplicationCreate, AgencySpaApplicationResponse, AgencySpaResponse, AllApplicationsResponse, ApplicationCreate, ApplicationResponse, ApplicationUpdate, MasterResponse
from services.application_service import create_agency_spa_application_service, create_application_service, get_agency_spa_applications_service, get_application, update_application, delete_application

router = APIRouter()

@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    application: ApplicationCreate = Depends(ApplicationCreate.as_form),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    auth=Depends(auth_middleware)
):
    if auth["type"] == "user":
        existing_user = db.query(WorkUser).filter_by(phonenumber=auth["user"]["phonenumber"]).first()
        if existing_user and existing_user.linked_profile_id:
            raise HTTPException(400, "User already linked to a profile")
        
    return await create_application_service(
        db=db,
        create_application=application,
        files=files
    )

@router.get("/agency_spa_applications/", response_model=List[AgencySpaApplicationResponse])
async def get_agency_spa_applications(db: Session = Depends(get_db)):
    return await get_agency_spa_applications_service(db)

@router.post("/agency_spa_applications/", response_model=AgencySpaApplicationResponse)
async def create_agency_spa_application(
    agency_spa_application: AgencySpaApplicationCreate = Depends(AgencySpaApplicationCreate.as_form),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    auth=Depends(auth_middleware)
):
    if auth["type"] == "user":
        existing_user = db.query(WorkUser).filter_by(phonenumber=auth["user"]["phonenumber"]).first()
        if existing_user and existing_user.linked_profile_id:
            raise HTTPException(400, "User already linked to a profile")
        
    return await create_agency_spa_application_service(
        db=db,
        create_agency_application=agency_spa_application,
        files=files,
    )

@router.get("/applications", response_model=AllApplicationsResponse)
def read_all_applications(db: Session = Depends(get_db)):
    return {
        "models": db.query(Application).all(),
        "agencies_spa": db.query(AgencySpaApplication).offset(0).limit(100).all()
    }

@router.get("/applications/{app_id}", response_model=ApplicationResponse | AgencySpaApplicationResponse)
def read_application(app_id: str, db: Session = Depends(get_db)):
    return get_application(db, app_id)

@router.put("/applications/{app_id}", response_model=ApplicationResponse)
def update_app(
    app_id: str, 
    app_update: ApplicationUpdate = Depends(ApplicationUpdate.as_form),
    files: List[UploadFile] = File([]), 
    db: Session = Depends(get_db), 
    token: str = Depends(verify_token)
):
    return update_application(db, app_id, app_update, files=files)

@router.delete("/applications/{app_id}")
def delete_app(app_id: str, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return delete_application(db, app_id)

@router.post("/applications/{app_id}/approve")
async def approve_application(app_id: str, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    # пробуем найти в заявках модели
    app = db.query(Application).filter_by(id=app_id).first()
    if app:
        db.query(WorkUser).filter_by(telegram_id=app.telegram_id).update({"linked_profile_id": app.id})
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
        return {"status": "approved", "id": str(master.id), "type": "model"}

    # пробуем найти в заявках agency/spa
    spa_app = db.query(AgencySpaApplication).filter_by(id=app_id).first()
    if spa_app:
        db.query(WorkUser).filter_by(telegram_id=app.telegram_id).update({"linked_profile_id": spa_app.id})
        agency = AgencySpa(
            id = spa_app.id,
            name = spa_app.name,
            phone = spa_app.phone,
            address = spa_app.address,
            is_agency = spa_app.is_agency,
            model_count = spa_app.model_count,
            photos = spa_app.photos
        )
        db.add(agency)
        db.delete(spa_app)
        db.commit()
        return {"status": "approved", "id": str(agency.id), "type": "agency_spa"}

    raise HTTPException(404, "Application not found")

@router.post("/applications/{app_id}/decline")
async def decline_application(app_id: str, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    deleted = db.query(Application).filter_by(id=app_id).delete()
    if not deleted:
        deleted = db.query(AgencySpaApplication).filter_by(id=app_id).delete()
    if not deleted:
        raise HTTPException(404, "Application not found")
    db.commit()
    return {"status": "declined", "id": app_id}