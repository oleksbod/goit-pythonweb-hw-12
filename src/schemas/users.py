from pydantic import BaseModel, Field, ConfigDict, EmailStr

# Схема користувача
class User(BaseModel):
    id: int
    username: str = Field(max_length=100, min_length=2)
    email: EmailStr
    avatar: str

    model_config = ConfigDict(from_attributes=True)

# Схема для запиту реєстрації
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Схема для токену
class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):    
    email: str
    password: str

class RequestEmail(BaseModel):
    email: EmailStr
