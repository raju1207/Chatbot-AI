from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class RegisterRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=80,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr


class AuthResponse(BaseModel):
    access_token: str

    token_type: str = "bearer"

    user: UserResponse


class LogoutResponse(BaseModel):
    message: str