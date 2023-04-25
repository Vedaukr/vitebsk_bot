import os

from .base import *

if 'APP_ENVIRONMENT' in os.environ and os.environ['APP_ENVIRONMENT'] == 'Production':
   from .prod import *
else:
   from .dev import *