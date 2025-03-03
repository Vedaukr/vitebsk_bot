import os
from sqlalchemy import create_engine
from database.models import Base
from settings import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True, pool_pre_ping=True)
Base.metadata.create_all(engine)