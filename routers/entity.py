from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates # <-- 2. THÊM dòng này vào
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from auth.deps import get_current_user, require_root

from database.db import get_db
from models.entity import Entity
from models.entity_flower import EntityFlower
templates = Jinja2Templates(directory="templates")


router = APIRouter(prefix="/entities", tags=["Entities"])

# ===== PAGE =====
@router.get("/add", response_class=HTMLResponse)
def add_entity_page(request: Request, user=Depends(require_root)):

    return templates.TemplateResponse(
        "add_entity.html",
        {
            "request": request,
            "message": None,
            "error": None,
            "user": user
        }
    )


# ===== CREATE =====
@router.post("/create")
def create_entity(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_root)
):

    try:
        name = name.strip()

        if not name:
            return templates.TemplateResponse(
                "add_entity.html",
                {
                    "request": request,
                    "error": "Tên không được để trống",
                    "message": None,
                    "user": user
                }
            )

        entity = Entity(name=name)

        db.add(entity)
        db.commit()
        db.refresh(entity)

        # redirect về home sau khi thành công
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        return templates.TemplateResponse(
            "add_entity.html",
            {
                "request": request,
                "error": f"Lỗi hệ thống: {str(e)}",
                "message": None,
                "user": user
            }
        )


@router.get("/", response_class=HTMLResponse)
def get_all_entities(
    request: Request,
    q: str = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)

):

    query = (
        db.query(
            Entity,
            func.coalesce(
                func.sum(EntityFlower.quantity),
                0
            ).label("total_flowers")
        )
        .outerjoin(
            EntityFlower,
            Entity.id == EntityFlower.entity_id
        )
    )


    # search
    if q:
        query = query.filter(
            Entity.name.ilike(f"%{q}%")
        )


    results = (
        query
        .group_by(Entity.id)
        .order_by(Entity.id.desc())
        .all()
    )


    # convert về object để template dễ dùng
    entities = []

    for entity, total in results:

        entity.total_flowers = total

        entities.append(entity)



    return templates.TemplateResponse(
        "entity_list.html",
        {
            "request": request,
            "entities": entities,
            "q": q or "",
            "user": user
        }
    )


@router.get("/{entity_id}", response_class=HTMLResponse)
def entity_detail_page(
    request: Request,
    entity_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    entity = db.query(Entity).filter(Entity.id == entity_id).first()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return templates.TemplateResponse(
        "entity_detail.html",
        {
            "request": request,
            "entity": entity,
            "user": user
        }
    )

class EntityUpdate(BaseModel):
    name: str

@router.put("/{entity_id}")
def update_entity(
    entity_id: int,
    payload: EntityUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_root)
):

    entity = db.query(Entity).filter(Entity.id == entity_id).first()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    entity.name = payload.name
    db.commit()

    return {"message": "Entity updated successfully"}



@router.delete("/{entity_id}")
def delete_entity(entity_id: int, db: Session = Depends(get_db), user=Depends(require_root)):

    entity = db.query(Entity).filter(Entity.id == entity_id).first()

    if not entity:
        raise HTTPException(404, "Entity không tồn tại")

    # xóa quan hệ trước
    db.query(EntityFlower).filter(
        EntityFlower.entity_id == entity_id
    ).delete()

    # xóa entity
    db.delete(entity)
    db.commit()

    return {"message": "Xóa thành công"}


