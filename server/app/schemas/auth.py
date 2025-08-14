from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str  = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)
    phone_number: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class CustomerOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True
