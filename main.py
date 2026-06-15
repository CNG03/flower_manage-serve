from fastapi import FastAPI
from jose import JWTError, jwt
from database.db import Base, engine
from fastapi.staticfiles import StaticFiles
from routers import entity, flower, inventory, backup, auth, account
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

# import models để tạo bảng
from models.entity import Entity
from models.flower import Flower
from models.entity_flower import EntityFlower

# import routers
from routers import db as db_router
from routers import web as web_router
from auth.deps import get_current_user


app = FastAPI(
    debug=False
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# tạo bảng
Base.metadata.create_all(bind=engine)

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

@app.middleware("http")
async def auth_middleware(request, call_next):

    path = request.url.path

    # bỏ qua login + static
    if path.startswith("/login") or path.startswith("/static"):
        return await call_next(request)

    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse("/login")

    try:
        token = token.replace("Bearer ", "")
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except JWTError:
        return RedirectResponse("/login")

    return await call_next(request)


app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=True,
    same_site="strict"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://athemi.site"
    ],
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)

# gắn router
app.include_router(auth.router)
app.include_router(db_router.router)
app.include_router(web_router.router)
app.include_router(entity.router)
app.include_router(flower.router)
app.include_router(inventory.router)
app.include_router(backup.router)
app.include_router(account.router)