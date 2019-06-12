from sqlalchemy import Column, Integer, Enum, DateTime, func, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.game import GameStatus

user_game_table = Table('user_game_association', Base.metadata,
                        Column('game_id', Integer, ForeignKey('game.id')),
                        Column('user_id', Integer, ForeignKey('user.id'))
                        )


class Game(Base):
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(GameStatus, index=True))
    # moves = relationship("Move", back_populates="game_id")
    players = relationship("User", secondary=user_game_table, back_populates="games")
    last_update = Column(DateTime, onupdate=func.now())
