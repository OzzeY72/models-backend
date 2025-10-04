from http.client import HTTPException
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from database import get_db
from models import AgencySpa, AgencySpaApplication, Application, Master
from schemas import AgencySpaApplicationResponse, AgencySpaResponse, AllApplicationsResponse, ApplicationCreate, ApplicationResponse, ApplicationUpdate, MasterResponse
from services.application_service import create_agency_spa_application_service, create_application_service, get_agency_spa_applications_service, get_application, update_application, delete_application

router = APIRouter()

@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    application: ApplicationCreate = Depends(ApplicationCreate.as_form),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
):
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
    name: str = Form(...),
    phone: str = Form(...),
    address: Optional[str] = Form(None),
    is_agency: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    print(file, "654321")
    return await create_agency_spa_application_service(
        db=db,
        name=name,
        phone=phone,
        address=address,
        is_agency=is_agency,
        files=file,
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
def update_app(app_id: str, app_update: ApplicationUpdate, db: Session = Depends(get_db)):
    return update_application(db, app_id, app_update)

@router.delete("/applications/{app_id}")
def delete_app(app_id: str, db: Session = Depends(get_db)):
    return delete_application(db, app_id)

@router.post("/applications/{app_id}/approve")
async def approve_application(app_id: str, db: Session = Depends(get_db)):
    # пробуем найти в заявках модели
    app = db.query(Application).filter_by(id=app_id).first()
    if app:
        master = Master(
            **app
        )
        db.add(master)
        db.delete(app)
        db.commit()
        return {"status": "approved", "id": str(master.id), "type": "model"}

    # пробуем найти в заявках agency/spa
    spa_app = db.query(AgencySpaApplication).filter_by(id=app_id).first()
    if spa_app:
        agency = AgencySpa(
            **spa_app
        )
        db.add(agency)
        db.delete(spa_app)
        db.commit()
        return {"status": "approved", "id": str(agency.id), "type": "agency_spa"}

    raise HTTPException(404, "Application not found")

@router.post("/applications/{app_id}/decline")
async def decline_application(app_id: str, db: Session = Depends(get_db)):
    deleted = db.query(Application).filter_by(id=app_id).delete()
    if not deleted:
        deleted = db.query(AgencySpaApplication).filter_by(id=app_id).delete()
    if not deleted:
        raise HTTPException(404, "Application not found")
    db.commit()
    return {"status": "declined", "id": app_id}