from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class CitationSchema(BaseModel):
    source: str
    page: int
    chunk_id: str


class QueryRequest(BaseModel):
    user_id: str = Field(default="anonymous", max_length=255)
    session_id: str = Field(max_length=255)
    query: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def strip_query(self):
        self.query = self.query.strip()
        return self


class QueryResponse(BaseModel):
    session_id: str
    answer: str
    citations: List[CitationSchema]
    confidence: float
    intent: str
    needs_human_approval: bool
    approval_id: Optional[str] = None
    latency_ms: float
