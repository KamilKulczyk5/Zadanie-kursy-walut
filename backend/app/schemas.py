from pydantic import BaseModel, Field
from typing import List

class RateOut(BaseModel):
    code: str
    mid: float

class FetchRequest(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")

class FetchResponse(BaseModel):
    date: str
    inserted: int
    updated: int
    total: int

class RatesByDateResponse(BaseModel):
    date: str
    rates: List[RateOut]
