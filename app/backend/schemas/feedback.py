from pydantic import BaseModel, Field
from typing import Literal


class FeedbackRequest(BaseModel):
    session_id: str = Field(max_length=255)
    user_id: str = Field(default="anonymous", max_length=255)
    query: str = Field(max_length=1000)
    answer: str
    rating: Literal["positive", "negative"]


class FeedbackResponse(BaseModel):
    message: str
    id: str
