from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from database import get_db
from services.agency_service import create_agency, create_master_in_agency, delete_agency, get_agencies, get_agencies_agency, get_agencies_spa, get_agency, update_agency
from schemas import AgencySpaCreate, AgencySpaResponse, AgencySpaUpdate, MasterCreate

router = APIRouter(prefix="/agencies", tags=["Agencies/SPA"])

@router.post("/", response_model=AgencySpaResponse)
def create_agency_route(
    agency: AgencySpaCreate = Depends(AgencySpaCreate.as_form),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
):
    return create_agency(db, agency_create=agency, files=files)

@router.post("/{agency_id}/masters/")
async def add_master_to_agency(
    agency_id: UUID,
    create_master: MasterCreate = Depends(MasterCreate.as_form),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
):
    master = await create_master_in_agency(
        db=db,
        agency_id=agency_id,
        create_master=create_master,
        files=files
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
