import datetime
from click import DateTime
from sqlalchemy import Column, Integer, String, Float, Enum, Boolean, ARRAY, ForeignKey
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import enum  

class BodyType(enum.Enum):
    Skinny = "Skinny"
    Slim = "Slim"
    Athletic = "Athletic"
    Curvy = "Curvy"

class WorkUser(Base):
    __tablename__ = "work_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(String, unique=True, nullable=False)
    phonenumber = Column(String, unique=True, nullable=False)
    otp_code = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    user_type = Column(String, nullable=True)
    linked_profile_id = Column(UUID(as_uuid=True), nullable=True)

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

    bodytype = Column(Enum(BodyType, name="bodytype_enum"), nullable=True)

    price_1h = Column(Float, nullable=True)
    price_2h = Column(Float, nullable=True)
    price_full_day = Column(Float, nullable=True)

    description = Column(String, nullable=True)
    photos = Column(ARRAY(String), default=[])

    is_top = Column(Boolean, default=False)

    agency_spa_id = Column(UUID(as_uuid=True), ForeignKey("agencies_spa.id"), nullable=True)

class AgencySpa(Base):
    __tablename__ = "agencies_spa"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=True)
    is_agency = Column(Boolean, default=False)
    model_count = Column(Integer, default=10)

    photos = Column(ARRAY(String), default=[])

    masters = relationship("Master", backref="agency_spa")

class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    phonenumber = Column(String, nullable=False)
    address = Column(String, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    cupsize = Column(Integer, nullable=True)

    bodytype = Column(Enum(BodyType, name="bodytype_enum"), nullable=True)

    price_1h = Column(Float, nullable=True)
    price_2h = Column(Float, nullable=True)
    price_full_day = Column(Float, nullable=True)

    description = Column(String, nullable=True)
    photos = Column(ARRAY(String), default=[])
    is_top = Column(Boolean, default=False)
    telegram_id = Column(String, nullable=True)

class AgencySpaApplication(Base):
    __tablename__ = "agency_spa_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=True)
    is_agency = Column(Boolean, default=False)
    model_count = Column(Integer, default=10)
    teleram_id = Column(String, nullable=True)

    photos = Column(String, nullable=False, default="")