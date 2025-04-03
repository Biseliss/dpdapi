from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

BASE_DIR = "uploads"

# роут получения файла из хранилища
@router.get("/{filename}")
def get_file(filename: str):
    file_path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, media_type="application/octet-stream")
