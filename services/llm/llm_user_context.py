import cachetools
from services.llm.models.llm_message import LlmMessage
from utils.singleton import Singleton

MAX_CACHE_SIZE = 100
CACHE_TTL = 60 * 60 # 60 minutes

class LlmUserContext(metaclass=Singleton):
    
    def __init__(self):
        self.context = cachetools.TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL)
    
    def get_user_context(self, user_id: str) -> list[LlmMessage]:
        ctx = self.context.get(user_id)
        if ctx is None:
            self.context[user_id] = ctx = []
        return ctx
    
    def reset_user_context(self, user_id: str):
        if self.context.get(user_id) is not None:
            del self.context[user_id]