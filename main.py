from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import os

from models import Base
from database import engine

from routers.agencies_router import router as agencies_router 
from routers.application_router import router as application_router
from routers.model_router import router as model_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.include_router(agencies_router)
app.include_router(application_router)
app.include_router(model_router)

app.mount("/static", StaticFiles(directory="uploads"), name="static")

