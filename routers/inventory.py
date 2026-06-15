from fastapi import APIRouter, Request, UploadFile, File, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates # <-- 2. THÊM dòng này vào
from sqlalchemy.orm import Session
from auth.deps import get_current_user, require_root

from database.db import get_db
from models.flower import Flower
from models.entity import Entity
from models.entity_flower import EntityFlower


templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/")
def inventory_page(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):

    entities = db.query(Entity).all()

    flowers = db.query(Flower).all()

    return templates.TemplateResponse(
        "inventory.html",
        {
            "request": request,
            "entities": entities,
            "flowers": flowers,
            "selected_entity": None,
            "owned_map": {},
            "user": user
        }
    )


@router.get("/{entity_id}")
def get_inventory(entity_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):

    records = db.query(EntityFlower).filter(
        EntityFlower.entity_id == entity_id
    ).all()

    return {
        "entity_id": entity_id,
        "owned": [
            {
                "flower_id": r.flower_id,
                "quantity": r.quantity
            }
            for r in records
        ]
    }


from fastapi import Body

@router.post("/save")
def save_inventory(
    entity_id: int = Body(...),
    flower_ids: list[int] = Body(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    # delete old
    db.query(EntityFlower).filter(
        EntityFlower.entity_id == entity_id
    ).delete()

    # insert new
    for fid in flower_ids:
        db.add(EntityFlower(
            entity_id=entity_id,
            flower_id=fid,
            quantity=1
        ))

    db.commit()

    return {
        "message": "Lưu thành công🌸"
    }