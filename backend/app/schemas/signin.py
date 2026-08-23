
from pydantic import BaseModel, EmailStr, Field


class Signup(BaseModel):
    username: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=5)