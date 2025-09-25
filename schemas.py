from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class MasterBase(BaseModel):
    name: str
    age: int
    phonenumber: str
    address: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    cupsize: Optional[int]
    clothsize: Optional[int]
    price_1h: Optional[float]
    price_2h: Optional[float]
    price_full_day: Optional[float]
    main_photo: Optional[str]
    is_top: Optional[bool] = False

class MasterCreate(MasterBase):
    pass

class MasterUpdate(MasterBase):
    pass

class MasterResponse(MasterBase):
    id: UUID

    class Config:
        orm_mode = True

class AgencySpaBase(BaseModel):
    name: str
    phone: str
    address: Optional[str]
    is_agency: bool
    photos: Optional[List[str]] = []

class AgencySpaCreate(AgencySpaBase):
    pass

class AgencySpaUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_agency: Optional[bool] = None
    photos: Optional[List[str]] = None

class AgencySpaResponse(AgencySpaBase):
    id: UUID
    models: Optional[List["MasterResponse"]] = []

    class Config:
        from_attributes = True

class ApplicationBase(BaseModel):
    name: str
    age: int
    phonenumber: str
    address: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    cupsize: Optional[int]
    clothsize: Optional[int]
    price_1h: Optional[float]
    price_2h: Optional[float]
    price_full_day: Optional[float]
    main_photo: Optional[str]
    is_top: Optional[bool] = False

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    name: Optional[str]
    age: Optional[int]
    phonenumber: Optional[str]
    address: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    cupsize: Optional[int]
    clothsize: Optional[int]
    price_1h: Optional[float]
    price_2h: Optional[float]
    price_full_day: Optional[float]
    main_photo: Optional[str]
    is_top: Optional[bool] = False

class ApplicationResponse(ApplicationBase):
    id: UUID

    class Config:
        orm_mode = True

class AgencySpaApplicationBase(BaseModel):
    name: str
    phone: str
    address: Optional[str]
    is_agency: bool
    photos: Optional[str]

class AgencySpaApplicationCreate(AgencySpaApplicationBase):
    pass

class AgencySpaApplicationUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_agency: Optional[bool] = None
    photos: Optional[str] = None

class AgencySpaApplicationResponse(AgencySpaApplicationBase):
    id: UUID

    class Config:
        from_attributes = True

class AllApplicationsResponse(BaseModel):
    models: List[ApplicationResponse]
    agencies_spa: List[AgencySpaApplicationResponse]

    class Config:
        from_attributes = True