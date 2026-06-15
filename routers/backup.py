import os
import shutil
import zipfile
from fastapi import Request, Depends
import time
from fastapi.templating import Jinja2Templates
from auth.deps import get_current_user, require_root
from fastapi import (
    APIRouter,
    Request,
    UploadFile,
    File
)

from fastapi.responses import (
    HTMLResponse,
    FileResponse,
    RedirectResponse
)

templates = Jinja2Templates(directory="templates")


router = APIRouter()


DB_PATH = "database/app_data.db"

UPLOAD_DIR = "static/uploads"

BACKUP_DIR = "backup"


os.makedirs(BACKUP_DIR, exist_ok=True)



# =====================
# PAGE
# =====================

@router.get("/backup",
            response_class=HTMLResponse)
def backup_page(request: Request, user=Depends(get_current_user)):

    return templates.TemplateResponse(
        "backup.html",
        {
            "request": request,
            "user": user
        }
    )



# =====================
# EXPORT
# =====================

@router.get("/backup/export")
def export_database(user=Depends(get_current_user)):

    filename = (
        f"lac_ha_backup_{int(time.time())}.zip"
    )

    zip_path = os.path.join(
        BACKUP_DIR,
        filename
    )


    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:


        # database
        zipf.write(
            DB_PATH,
            arcname="app_data.db"
        )


        # images
        if os.path.exists(UPLOAD_DIR):

            for root, dirs, files in os.walk(
                UPLOAD_DIR
            ):

                for file in files:

                    full_path = os.path.join(
                        root,
                        file
                    )

                    zipf.write(
                        full_path,
                        arcname=os.path.relpath(
                            full_path,
                            "static"
                        )
                    )


    return FileResponse(
        zip_path,
        filename=filename
    )



# =====================
# IMPORT
# =====================

# @router.post("/backup/import")
# def import_database(
#     file: UploadFile = File(...),
#     user=Depends(require_root)
# ):

#     temp_zip = "backup/import.zip"

#     with open(temp_zip, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     if not zipfile.is_zipfile(temp_zip):
#         return {"error": "Invalid zip file"}

#     extract_dir = "backup/imported"

#     if os.path.exists(extract_dir):
#         shutil.rmtree(extract_dir)

#     os.makedirs(extract_dir)

#     with zipfile.ZipFile(temp_zip, "r") as zipf:
#         zipf.extractall(extract_dir)

#     # DB
#     new_db = os.path.join(extract_dir, "app_data.db")

#     if os.path.exists(new_db):
#         shutil.copy2(new_db, DB_PATH)

#     # FIX PATH HERE
#     imported_upload = os.path.join(extract_dir, "uploads")

#     if os.path.exists(imported_upload):
#         if os.path.exists(UPLOAD_DIR):
#             shutil.rmtree(UPLOAD_DIR)

#         shutil.copytree(imported_upload, UPLOAD_DIR)

#     return RedirectResponse("/backup", status_code=303)