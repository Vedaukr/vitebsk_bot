from .base import *
import os

BASE_DIR = "/app/data"
SQLALCHEMY_DATABASE_URI =  f'sqlite:///{os.path.join(BASE_DIR, DB_NAME)}'