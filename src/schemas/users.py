from pydantic import BaseModel, Field, ConfigDict, EmailStr
from src.database.models import UserRole

# Схема користувача
class User(BaseModel):
    id: int
    username: str = Field(max_length=100, min_length=2)
    email: EmailStr
    avatar: str
    role: UserRole    

    model_config = ConfigDict(from_attributes=True)

# Схема для запиту реєстрації
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole

# Схема для токену
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class UserLogin(BaseModel):    
    email: str
    password: str

class RequestEmail(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str = Field(..., title="Токен скидання пароля")
    new_password: str = Field(..., min_length=8, title="Новий пароль")
