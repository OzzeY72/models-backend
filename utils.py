import os
import shutil
from typing import List
from fastapi import UploadFile
from uuid import UUID, uuid4

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_files(files: List[UploadFile]):
    saved_files = []

    if files:
        for file in files:
            ext = os.path.splitext(file.filename)[1]
            file_name = f"{uuid4()}{ext}"
            file_path = os.path.join(UPLOAD_DIR, file_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_files.append(file_name)

    return saved_files

def delete_file(file_name):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

def delete_files(files):
    for file in files:
        delete_file(file)