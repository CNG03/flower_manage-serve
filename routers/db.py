import os
import shutil
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(prefix="/db", tags=["Database"])

DB_PATH = "database/app_data.db"


# 📤 EXPORT DB
@router.get("/export")
def export_db():
    if not os.path.exists(DB_PATH):
        return JSONResponse(
            status_code=404,
            content={"message": "Database not found"}
        )

    return FileResponse(
        path=DB_PATH,
        filename="app_data.db",
        media_type="application/octet-stream"
    )


# 📥 IMPORT DB
@router.post("/import")
async def import_db(file: UploadFile = File(...)):

    if not file.filename.endswith(".db"):
        return JSONResponse(
            status_code=400,
            content={"message": "Only .db file allowed"}
        )

    # backup DB cũ
    if os.path.exists(DB_PATH):
        backup_path = "database/app_data_backup.db"
        shutil.copy(DB_PATH, backup_path)

    # ghi đè DB mới
    with open(DB_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Import database success 🚀",
        "backup": "database/app_data_backup.db"
    }