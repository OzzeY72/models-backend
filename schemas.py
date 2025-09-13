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

class MasterCreate(MasterBase):
    pass

class MasterUpdate(MasterBase):
    pass

class MasterResponse(MasterBase):
    id: UUID

    class Config:
        orm_mode = True
