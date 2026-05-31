from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str =  Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9]+$")
    password: str = Field(..., min_length=6, max_length=20)

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer")
    expires_in: int

class UserRegisterResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    username: str
    created_at: str

class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    username: str
    is_active: bool
    memory_count: int
    book_count: int
    created_at: str

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=20)

class MessageResponse(BaseModel):
    message: str
