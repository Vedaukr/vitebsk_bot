from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

class LlmMessageRole(Enum):
    USER = 1
    LLM = 2

class LlmMessageType(Enum):
    TEXT = 1
    IMG = 2

@dataclass
class LlmMessage:
    role: LlmMessageRole
    type: LlmMessageType
    content: str
    metadata: Optional[dict[str, Any]] = None