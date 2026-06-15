from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from database.db import get_db
from models.user import User

from auth.auth import verify_password, create_token

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# =========================
# LOGIN PAGE
# =========================
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# =========================
# HANDLE LOGIN
# =========================
@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": {},
                "error": "Sai tài khoản hoặc mật khẩu"
            },
            status_code=401
        )

    token = create_token({
        "id": user.id,
        "role": user.role
    })

    response = RedirectResponse(url="/", status_code=302)

    # lưu token vào cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True
    )

    return response


# =========================
# LOGOUT
# =========================
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response