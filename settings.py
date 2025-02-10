import os
from dynaconf import Dynaconf

env = os.getenv("DYNACONF_ENVIRONMENT", "default")

settings = Dynaconf(
    environments=True,
    ENV_FOR_DYNACONF=env,
    ENVVAR_PREFIX_FOR_DYNACONF=False,
    settings_files=['settings.json', '.env']
)

SQLALCHEMY_DATABASE_URI =  settings['SQLALCHEMY_DATABASE_URI']