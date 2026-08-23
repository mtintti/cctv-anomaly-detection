from pydantic import BaseModel, EmailStr, Field


class Login(BaseModel):
    email: EmailStr
    password: str= Field(..., min_length=5)