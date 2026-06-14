from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class HistoryMessage(BaseModel):
    role: str
    content: str
    intent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[HistoryMessage]
    total: int
