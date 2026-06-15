import os
import shutil
from sqlalchemy import func
# 1. XÓA dòng: from tempfile import template
from fastapi import APIRouter, Request, UploadFile, File, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates # <-- 2. THÊM dòng này vào
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, JSONResponse
from auth.deps import get_current_user, require_root

from database.db import get_db
from models.flower import Flower
from models.entity_flower import EntityFlower
from models.entity import Entity

router = APIRouter(prefix="/flowers", tags=["Flowers"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")

@router.get("/add", response_class=HTMLResponse)
async def home(request: Request, user=Depends(require_root)):
    return templates.TemplateResponse(
        "add_flower.html",
        {
            "request": request,
            "user": user
        }
    )

@router.post("/create")
async def create_flower(
    name: str = Form(...),
    rank: int = Form(1),
    image: UploadFile = File(None),   # 🔥 đổi file -> image cho khớp HTML
    db: Session = Depends(get_db),
    user=Depends(require_root)
):

    try:
        img_url = None

        # upload image
        if image:
            file_ext = image.filename.split(".")[-1]
            safe_name = name.replace(" ", "_")
            filename = f"{safe_name}_{image.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            img_url = f"/static/uploads/{filename}"

        flower = Flower(
            name=name,
            rank=rank,
            img=img_url
        )

        db.add(flower)
        db.commit()
        db.refresh(flower)

        return JSONResponse({
            "success": True,
            "message": "🌸 Thêm hoa thành công!  Quay về trang chủ!",
            "data": {
                "id": flower.id,
                "name": flower.name,
                "img": flower.img,
                "rank": flower.rank
            }
        })

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/")
def get_all_flowers(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):

    flowers = db.query(Flower).all()

    # lấy số lượng người sở hữu từng hoa
    ownership_counts = (
        db.query(
            EntityFlower.flower_id,
            func.count(EntityFlower.entity_id).label("total_users")
        )
        .group_by(EntityFlower.flower_id)
        .all()
    )

    # map ra dict {flower_id: count}
    count_map = {fc.flower_id: fc.total_users for fc in ownership_counts}

    return templates.TemplateResponse(
        "flower_list.html",
        {
            "request": request,
            "flowers": flowers,
            "count_map": count_map,
            "user": user
        }
    )


@router.get("/{flower_id}")
def get_flower(flower_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):

    flower = db.query(Flower).filter(Flower.id == flower_id).first()

    if not flower:
        raise HTTPException(status_code=404, detail="Flower not found")

    return flower


@router.put("/{flower_id}")
def update_flower(
    flower_id: int,
    name: str = Form(...),
    rank: int = Form(...),
    file: UploadFile = File(None, alias="image"),
    db: Session = Depends(get_db),
    user=Depends(require_root)
):

    flower = db.query(Flower).filter(
        Flower.id == flower_id
    ).first()

    if not flower:
        raise HTTPException(
            status_code=404,
            detail="Flower not found"
        )

    try:

        # =========================
        # 1. UPDATE BASIC INFO
        # =========================

        flower.name = name
        flower.rank = rank


        # =========================
        # 2. UPDATE IMAGE ONLY IF NEW IMAGE
        # =========================

        if file and file.filename:

            # lưu đường dẫn ảnh cũ
            old_image_path = None

            if flower.img:
                old_image_path = flower.img.lstrip("/")


            # tạo file mới
            file_ext = file.filename.split(".")[-1]

            filename = f"{flower_id}_{file.filename}"

            new_file_path = os.path.join(
                UPLOAD_DIR,
                filename
            )


            # save new image
            with open(new_file_path, "wb") as buffer:
                buffer.write(file.file.read())


            # update DB sau khi save thành công
            flower.img = f"/static/uploads/{filename}"


            # =========================
            # DELETE OLD IMAGE
            # =========================

            if old_image_path:

                try:

                    # tránh xóa nhầm nếu trùng file
                    if old_image_path != new_file_path:
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)

                except Exception as e:
                    print(
                        f"[WARN] Cannot delete old image: {e}"
                    )


        # =========================
        # 3. COMMIT
        # =========================

        db.commit()
        db.refresh(flower)


        return {
            "success": True,
            "message": "Cập nhật thành công !",
            "data": {
                "id": flower.id,
                "name": flower.name,
                "rank": flower.rank,
                "img": flower.img
            }
        }


    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/edit/{flower_id}")
def edit_flower_page(flower_id: int, request: Request, db: Session = Depends(get_db), user=Depends(require_root)):

    flower = db.query(Flower).filter(Flower.id == flower_id).first()

    if not flower:
        raise HTTPException(status_code=404, detail="Flower not found")

    return templates.TemplateResponse(
        "flower_edit.html",
        {
            "request": request,
            "flower": flower,
            "user": user
        }
    )


@router.delete("/{flower_id}")
def delete_flower(flower_id: int, db: Session = Depends(get_db), user=Depends(require_root)):

    flower = db.query(Flower).filter(Flower.id == flower_id).first()

    if not flower:
        raise HTTPException(status_code=404, detail="Flower not found")

    try:
        # ===============================
        # 1. XÓA ENTITY_FLOWER
        # ===============================
        db.query(EntityFlower).filter(
            EntityFlower.flower_id == flower_id
        ).delete(synchronize_session=False)

        # ===============================
        # 2. XÓA FILE ẢNH
        # ===============================
        if flower.img:
            try:
                # flower.img = "/static/uploads/xxx.jpg"
                file_path = flower.img.lstrip("/")  # bỏ slash đầu

                if os.path.exists(file_path):
                    os.remove(file_path)

            except Exception as file_err:
                # không crash hệ thống nếu file lỗi
                print(f"[WARN] Cannot delete image: {file_err}")

        # ===============================
        # 3. XÓA FLOWER
        # ===============================
        db.delete(flower)
        db.commit()

        return {
            "success": True,
            "message": "🌸 Deleted successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/owner/{flower_id}")
def flower_owner_detail(
    flower_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    flower = db.query(Flower).filter(Flower.id == flower_id).first()

    if not flower:
        raise HTTPException(status_code=404, detail="Flower not found")

    # lấy danh sách người sở hữu + quantity
    owners = (
        db.query(EntityFlower)
        .filter(EntityFlower.flower_id == flower_id)
        .all()
    )

    # load entity info
    result = []
    for o in owners:
        entity = db.query(Entity).filter(Entity.id == o.entity_id).first()

        result.append({
            "entity_id": entity.id,
            "name": entity.name,
            "avatar": entity.avatar if hasattr(entity, "avatar") else None,
            "quantity": o.quantity,
            "acquired_at": o.acquired_at
        })

    return templates.TemplateResponse(
        "flower_owner.html",
        {
            "request": request,
            "flower": flower,
            "owners": result,
            "user": user
        }
    )