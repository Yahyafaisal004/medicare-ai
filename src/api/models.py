from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    role: str
    password: Optional[str] = None
    subject_id: Optional[int] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class QueryRequest(BaseModel):
    query: str