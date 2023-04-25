import os
from sqlalchemy import create_engine

# local
# basedir = os.path.abspath(os.path.dirname(__file__))
# fly.io
basedir = "/app/data"

DB_NAME = "app.db"
SQLALCHEMY_DATABASE_URI =  'sqlite:///' + os.path.join(basedir, DB_NAME)
SQLALCHEMY_TRACK_MODIFICATIONS = True

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
