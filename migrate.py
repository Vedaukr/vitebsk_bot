from database.models import Base
from database.db_config import engine

Base.metadata.create_all(engine)