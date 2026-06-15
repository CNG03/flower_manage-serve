from fastapi import Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from database.db import SessionLocal
from models.user import User

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")

    return token.replace("Bearer ", "")


def get_current_user(
    token: str = Depends(get_token_from_cookie)
):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("id")

        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()

        if not user:
            raise HTTPException(status_code=401)

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

def require_root(user = Depends(get_current_user)):
    if user.role != "root":
        raise HTTPException(403, "Root only")
    return user