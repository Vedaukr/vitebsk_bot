from dataclasses import dataclass
from typing import Optional, TypedDict

class LlmMetadata(TypedDict):
    total_tokens: Optional[int]
    reasoning: Optional[str]

@dataclass
class LlmResponse:
    content: str
    metadata: Optional[LlmMetadata]