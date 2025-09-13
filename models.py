from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class Master(Base):
    __tablename__ = "masters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    phonenumber = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    cupsize = Column(Integer, nullable=True)
    clothsize = Column(Integer, nullable=True)
    price_1h = Column(Float, nullable=True)
    price_2h = Column(Float, nullable=True)
    price_full_day = Column(Float, nullable=True)
    main_photo = Column(String, nullable=True)
