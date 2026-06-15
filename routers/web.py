from sqlalchemy import func
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates # <-- 2. THÊM dòng này vào
from sqlalchemy.orm import Session
from database.db import get_db
from models.flower import Flower;
from models.entity_flower import EntityFlower
from auth.deps import get_current_user
from auth.web_deps import get_current_user_web

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)   # 👈 THÊM DÒNG NÀY
):

    flowers = db.query(Flower).all()

    ownership_counts = (
        db.query(
            EntityFlower.flower_id,
            func.count(EntityFlower.entity_id).label("total_users")
        )
        .group_by(EntityFlower.flower_id)
        .all()
    )

    count_map = {f.flower_id: f.total_users for f in ownership_counts}

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "flowers": flowers,
            "count_map": count_map,
            "user": user   # 👈 optional nhưng rất nên thêm
        }
    )