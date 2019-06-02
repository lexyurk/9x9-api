from sqlalchemy import Column, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Move(Base):
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("user.id"))
    game_id = Column(Integer, ForeignKey("game.id"))
    inner_field = ARRAY(Integer)
    outer_field = ARRAY(Integer)
