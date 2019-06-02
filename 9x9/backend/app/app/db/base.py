# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.db_models.user import User  # noqa
from app.db_models.item import Item  # noqa
from app.db_models.move import Move  # noqa
from app.db_models.game import user_game_table  # noqa
from app.db_models.game import Game  # noqa
