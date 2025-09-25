from http.client import HTTPException
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from database import get_db
from models import AgencySpa, AgencySpaApplication, Application, Master
from schemas import AgencySpaApplicationResponse, AgencySpaResponse, AllApplicationsResponse, ApplicationCreate, ApplicationResponse, ApplicationUpdate, MasterResponse
from services.application_service import approve_agency_spa_application_service, approve_application, create_agency_spa_application_service, create_application_service, decline_agency_spa_application_service, decline_application, get_agency_spa_applications_service, get_applications, get_application, update_application, delete_application, upload_application_photo

router = APIRouter()

@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
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
    file: Optional[UploadFile] = File(None),
    is_top: Optional[bool] = Form(None),
    db: Session = Depends(get_db),
):
    return await create_application_service(
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
        file=file,
        is_top=is_top
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

# @router.get("/agency_spa_applications/{application_id}/approve", response_model=AgencySpaResponse)
# async def approve_agency_spa_application(
#     application_id: UUID, db: Session = Depends(get_db)
# ):
#     return await approve_agency_spa_application_service(db, application_id)


# @router.get("/agency_spa_applications/{application_id}/decline")
# async def decline_agency_spa_application(
#     application_id: UUID, db: Session = Depends(get_db)
# ):
#     return await decline_agency_spa_application_service(db, application_id)

# @router.post("/applications/{application_id}/approve", response_model=MasterResponse)
# def approve_application_route(application_id: UUID, db: Session = Depends(get_db)):
#     try:
#         master = approve_application(db, application_id)
#         return master
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))

# @router.delete("/applications/{application_id}/decline")
# def decline_application_route(application_id: UUID, db: Session = Depends(get_db)):
#     try:
#         return decline_application(db, application_id)
#     except ValueError as e:
        # raise HTTPException(status_code=404, detail=str(e))

# @router.get("/applications/", response_model=List[ApplicationResponse])
# def read_applications(db: Session = Depends(get_db)):
#     # return get_applications(db)

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

@router.post("/applications/{app_id}/upload_photo/")
def upload_photo(app_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return upload_application_photo(db, app_id, file)

@router.post("/applications/{app_id}/approve")
async def approve_application(app_id: str, db: Session = Depends(get_db)):
    # пробуем найти в заявках модели
    app = db.query(Application).filter_by(id=app_id).first()
    if app:
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
        )
        db.add(master)
        db.delete(app)
        db.commit()
        return {"status": "approved", "id": str(master.id), "type": "model"}

    # пробуем найти в заявках agency/spa
    spa_app = db.query(AgencySpaApplication).filter_by(id=app_id).first()
    if spa_app:
        agency = AgencySpa(
            name=spa_app.name,
            phone=spa_app.phone,
            address=spa_app.address,
            is_agency=spa_app.is_agency,
            photos=spa_app.photos,
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