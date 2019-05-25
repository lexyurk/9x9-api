from sqlalchemy import Boolean, Column, Integer, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Game(Base):
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean(), default=True)
    is_end = Column(Boolean(), default=False)
    active_users = Column(Integer)
    moves = relationship("Move",
                         back_populates="owner",
                         cascade="save-update, merge, delete",
                         order_by="Move.id"
                         )
    players = relationship("User")
    last_action = Column(DateTime, onupdate=func.now())
