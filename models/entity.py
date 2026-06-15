from sqlalchemy import Column, Integer, String, DateTime
from database.db import Base
from utils.datetime import get_utc7_now


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    # 3. Truyền tên hàm get_utc7_now (không có dấu ngoặc tròn) vào default
    created_at = Column(DateTime, default=get_utc7_now)