from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ApprovalListItem(BaseModel):
    id: str
    session_id: str
    query: str
    answer: str
    confidence: float
    status: str
    created_at: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None


class ApprovalListResponse(BaseModel):
    items: List[ApprovalListItem]
    total: int


class ApprovalActionRequest(BaseModel):
    approval_id: str
    session_id: str
    status: Literal["approved", "rejected"]
    reviewed_by: str = Field(default="admin", max_length=255)


class ApprovalActionResponse(BaseModel):
    message: str
    answer: Optional[str] = None
