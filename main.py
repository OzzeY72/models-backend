from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os

from models import Base
from database import engine

from routers.agencies_router import router as agencies_router 
from routers.application_router import router as application_router
from routers.model_router import router as model_router
from routers.auth_router import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agencies_router)
app.include_router(application_router)
app.include_router(model_router)
app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="uploads"), name="static")

@app.get("/masters_view/{master_id}", response_class=HTMLResponse)
async def get_master_page(master_id: str):
    template_path = os.path.join("templates", "master.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{MASTER_ID}}", master_id)
    return HTMLResponse(content=html)

@app.get("/agencies_view/{agency_id}", response_class=HTMLResponse)
async def get_master_page(agency_id: str):
    template_path = os.path.join("templates", "agency.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{MASTER_ID}}", agency_id)
    return HTMLResponse(content=html)