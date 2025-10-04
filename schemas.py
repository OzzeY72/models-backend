from fastapi import Form
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from models import BodyType

class MasterBase(BaseModel):
    name: str
    age: int
    phonenumber: str
    address: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    cupsize: Optional[int]

    bodytype: Optional[BodyType]

    price_1h: Optional[float]
    price_2h: Optional[float]
    price_full_day: Optional[float]

    description: Optional[str]

    is_top: Optional[bool] = False

class MasterSearch(BaseModel):
    age_from: Optional[int] = None
    age_to: Optional[int] = None

    height_from: Optional[float] = None
    height_to:   Optional[float] = None

    cupsize: Optional[int] = None
    bodytype: Optional[BodyType] = None

class MasterCreate(MasterBase):
    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        age: int = Form(...),
        phonenumber: str = Form(...),
        address: Optional[str] = Form(None),
        height: Optional[float] = Form(None),
        weight: Optional[float] = Form(None),
        cupsize: Optional[int] = Form(None),
        bodytype: Optional[BodyType] = Form(None),
        price_1h: Optional[float] = Form(None),
        price_2h: Optional[float] = Form(None),
        price_full_day: Optional[float] = Form(None),
        description: Optional[str] = Form(None),
        is_top: Optional[bool] = Form(False),
    ):
        return cls(
            name=name,
            age=age,
            phonenumber=phonenumber,
            address=address,
            height=height,
            weight=weight,
            cupsize=cupsize,
            bodytype=bodytype,
            price_1h=price_1h,
            price_2h=price_2h,
            price_full_day=price_full_day,
            description=description,
            is_top=is_top,
        )
    pass

class MasterUpdate(MasterCreate):
    pass

class MasterResponse(MasterBase):
    id: UUID
    photos: List[str] = []

    class Config:
        orm_mode = True

class AgencySpaBase(BaseModel):
    name: str
    phone: str
    address: Optional[str]
    is_agency: bool
    model_count: int

class AgencySpaCreate(AgencySpaBase):
    @classmethod
    def as_form(
        cls,
        name = Form(...),
        phone = Form(...),
        address = Form(None),
        is_agency = Form(...),
        model_count = Form(None)
    ):
        return cls(
            name=name,
            phone=phone,
            address=address,
            is_agency=is_agency,
            model_count=model_count
        )
    pass

class AgencySpaUpdate(AgencySpaCreate):
    pass

class AgencySpaResponse(AgencySpaBase):
    id: UUID
    photos: List[str] = []
    models: Optional[List["MasterResponse"]] = []

    class Config:
        from_attributes = True

class ApplicationBase(MasterBase):
    pass

class ApplicationCreate(MasterCreate):
    pass

class ApplicationUpdate(ApplicationCreate):
    pass

class ApplicationResponse(ApplicationBase):
    id: UUID
    photos: List[str] = [] 

    class Config:
        orm_mode = True

class AgencySpaApplicationBase(AgencySpaBase):
    pass

class AgencySpaApplicationCreate(AgencySpaCreate):
    pass

class AgencySpaApplicationUpdate(AgencySpaApplicationCreate):
    pass

class AgencySpaApplicationResponse(AgencySpaApplicationBase):
    id: UUID
    photos: List[str] = []

    class Config:
        from_attributes = True

class AllApplicationsResponse(BaseModel):
    models: List[ApplicationResponse]
    agencies_spa: List[AgencySpaApplicationResponse]

    class Config:
        from_attributes = True