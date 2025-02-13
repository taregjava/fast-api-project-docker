from fastapi import UploadFile
import shutil
import os

UPLOAD_DIR = "static/uploads/"

def save_file(file: UploadFile):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path
