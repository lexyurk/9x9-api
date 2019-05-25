from sqlalchemy import Column, Integer, ARRAY
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Move(Base):
    id = Column(Integer, primary_key=True, index=True)
    user = relationship("User")
    outer_field = ARRAY(Integer)
    inner_field = ARRAY(Integer)