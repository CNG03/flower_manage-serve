from sqlalchemy import Column, Integer, String, DateTime
from database.db import Base
from utils.datetime import get_utc7_now


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # hash sau
    role = Column(String(20), default="user")  # "root" | "user"

    created_at = Column(DateTime, default=get_utc7_now)