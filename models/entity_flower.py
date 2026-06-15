from sqlalchemy import Column, Integer, DateTime, ForeignKey
from database.db import Base
from utils.datetime import get_utc7_now


class EntityFlower(Base):
    __tablename__ = "entity_flowers"

    id = Column(Integer, primary_key=True, index=True)

    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    flower_id = Column(Integer, ForeignKey("flowers.id"), nullable=False)

    quantity = Column(Integer, default=1)
    
    # 3. Thay thế datetime.utcnow bằng get_utc7_now
    acquired_at = Column(DateTime, default=get_utc7_now)