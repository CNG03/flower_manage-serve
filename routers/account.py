from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from database.db import get_db
from models.user import User
from auth.deps import get_current_user, require_root
from auth.auth import hash_password, verify_password
from utils.template import render
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/account", response_class=HTMLResponse)
def account_page(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(require_root)
):

    users = db.query(User).all()

    msg = request.query_params.get("msg")
    msg_type = request.query_params.get("type", "info")

    return templates.TemplateResponse(
        "account.html",
        {
            "request": request,
            "user": user,
            "users": users,
            "msg": msg,
            "msg_type": msg_type,
        }
    )

@router.post("/account/change-root-password")
def change_root_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
    root = Depends(require_root)
):

    db_root = db.query(User).filter(User.id == root.id).first()

    if not verify_password(old_password, db_root.password):
        return RedirectResponse(
            "/account?msg=Sai+mật+khẩu+ROOT&type=error",
            status_code=303
        )

    db_root.password = hash_password(new_password)
    db.commit()

    return RedirectResponse(
        "/account?msg=Đổi+mật+khẩu+ROOT+thành+công&type=success",
        status_code=303
    )


@router.post("/account/reset-user-password")
def reset_user_password(
    user_id: int = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
    root = Depends(require_root)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return RedirectResponse(
            "/account?msg=User+không+tồn+tại&type=error",
            status_code=303
        )

    if user.role == "root":
        return RedirectResponse(
            "/account?msg=Không+thể+reset+ROOT&type=error",
            status_code=303
        )

    user.password = hash_password(new_password)
    db.commit()

    return RedirectResponse(
        "/account?msg=Reset+password+thành+công&type=success",
        status_code=303
    )