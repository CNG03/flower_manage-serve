from sqlalchemy import Column, Integer, String, DateTime
from database.db import Base
from utils.datetime import get_utc7_now


class Flower(Base):
    __tablename__ = "flowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    img = Column(String, nullable=True)
    rank = Column(Integer, default=1)

    # 3. Thay thế datetime.utcnow bằng get_utc7_now (không có dấu ngoặc tròn)
    created_at = Column(DateTime, default=get_utc7_now)