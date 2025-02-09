import os
from services.llm.models.llm_message import LlmMessage
from settings import settings
from utils.singleton import Singleton
from utils.persistent_ttl_cache import PersistentTTLCache

MAX_CACHE_SIZE = 100
CACHE_TTL = 60 * 60 # 60 minutes
PERSISTENT_CACHE_PATH = settings.get('PERSISTENT_CACHE_PATH', './ctx_cache')
CACHE_PATH = os.path.join(PERSISTENT_CACHE_PATH, "llm_user_context.pickle")

class LlmUserContext(metaclass=Singleton):
    
    def __init__(self):
        self.context = PersistentTTLCache(
            maxsize=MAX_CACHE_SIZE, 
            ttl=CACHE_TTL, 
            filename=CACHE_PATH,
            save_interval=60
        )
    
    def get_user_context(self, user_id: str) -> list[LlmMessage]:
        ctx = self.context.get(user_id)
        if ctx is None:
            self.context[user_id] = ctx = []
        return ctx
    
    def update_user_context(self, user_id: str, updated_ctx: list[LlmMessage]):
        self.context[user_id] = updated_ctx
    
    def reset_user_context(self, user_id: str):
        if self.context.get(user_id) is not None:
            del self.context[user_id]