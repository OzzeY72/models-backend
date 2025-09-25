from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from database import get_db
from services.agency_service import create_agency, create_master_in_agency, delete_agency, get_agencies, get_agencies_agency, get_agencies_spa, get_agency, update_agency
from schemas import AgencySpaCreate, AgencySpaResponse, AgencySpaUpdate

router = APIRouter(prefix="/agencies", tags=["Agencies/SPA"])

@router.post("/", response_model=AgencySpaResponse)
def create_agency_route(
    name: str = Form(...),
    phone: str = Form(...),
    address: str = Form(None),
    is_agency: bool = Form(...),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
):
    agency_create = AgencySpaCreate(
        name=name,
        phone=phone,
        address=address,
        is_agency=is_agency,
    )
    return create_agency(db, agency_create, files)


@router.post("/{agency_id}/masters/")
async def add_master_to_agency(
    agency_id: UUID,
    name: str = Form(...),
    age: int = Form(...),
    phonenumber: str = Form(...),
    address: str = Form(None),
    height: float = Form(None),
    weight: float = Form(None),
    cupsize: int = Form(None),
    clothsize: int = Form(None),
    price_1h: float = Form(None),
    price_2h: float = Form(None),
    price_full_day: float = Form(None),
    is_top: bool = Form(False),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    master = await create_master_in_agency(
        db=db,
        agency_id=agency_id,
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
        file=file
    )
    return master

@router.get("/", response_model=List[AgencySpaResponse])
def read_agencies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_agencies(db, skip=skip, limit=limit)

@router.get("/agencies/", response_model=List[AgencySpaResponse])
def read_only_agencies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_agencies_agency(db, skip=skip, limit=limit)

@router.get("/spa/", response_model=List[AgencySpaResponse])
def read_only_spa(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_agencies_spa(db, skip=skip, limit=limit)

# READ ONE
@router.get("/{agency_id}", response_model=AgencySpaResponse)
def read_agency(agency_id: UUID, db: Session = Depends(get_db)):
    return get_agency(db, agency_id)

# UPDATE
@router.put("/{agency_id}", response_model=AgencySpaResponse)
def update_agency_route(
    agency_id: UUID,
    agency_update: AgencySpaUpdate,
    db: Session = Depends(get_db),
):
    return update_agency(db, agency_id, agency_update)

# DELETE
@router.delete("/{agency_id}")
def delete_agency_route(agency_id: UUID, db: Session = Depends(get_db)):
    return delete_agency(db, agency_id)
