from fastapi import APIRouter, Depends, Form, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from database import get_db
from middleware import auth_middleware, verify_token
from services.agency_service import create_agency, create_master_in_agency, delete_agency, get_agencies, get_agencies_agency, get_agencies_spa, get_agency, is_user_owner, update_agency
from schemas import AgencySpaCreate, AgencySpaResponse, AgencySpaUpdate, MasterCreate

router = APIRouter(prefix="/agencies", tags=["Agencies/SPA"])

@router.post("/", response_model=AgencySpaResponse)
def create_agency_route(
    agency: AgencySpaCreate = Depends(AgencySpaCreate.as_form),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    return create_agency(db, agency_create=agency, files=files)

@router.post("/{agency_id}/masters/")
async def add_master_to_agency(
    agency_id: UUID,
    create_master: MasterCreate = Depends(MasterCreate.as_form),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    auth=Depends(auth_middleware),
):
    if auth["type"] == "user":
        if not is_user_owner(db, auth["user"], agency_id):
            raise HTTPException(status_code=403, detail="You are not the owner of this agency/spa")
        
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
    agency_update: AgencySpaUpdate = Depends(AgencySpaUpdate.as_form),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    auth=Depends(auth_middleware),
):
    if auth["type"] == "user":
        if not is_user_owner(db, auth["user"], agency_id):
            raise HTTPException(status_code=403, detail="You are not the owner of this agency/spa")
        
    return update_agency(db, agency_id, agency_update, files=files)

# DELETE
@router.delete("/{agency_id}")
def delete_agency_route(agency_id: UUID, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return delete_agency(db, agency_id)
