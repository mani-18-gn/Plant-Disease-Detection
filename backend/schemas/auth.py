from pydantic import BaseModel, Field
from datetime import datetime
from backend.db.models.core.user import UserRole


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6)
    full_name: str
    village: str | None = None
    taluk: str | None = None
    district: str | None = None
    state: str | None = None
    preferred_mandi: str | None = None
    preferred_language: str = "en"


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: UserRole
