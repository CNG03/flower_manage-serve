from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError

from database.db import SessionLocal
from models.user import User

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"


def get_current_user_web(request: Request):

    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse("/login")

    token = token.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("id")

        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()

        if not user:
            return RedirectResponse("/login")

        return user

    except JWTError:
        return RedirectResponse("/login")