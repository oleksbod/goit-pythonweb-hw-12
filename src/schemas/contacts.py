from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator

class ContactBase(BaseModel):
    first_name: str = Field(max_length=100, min_length=2)
    last_name: str = Field(max_length=100, min_length=2)
    email: EmailStr
    phone: str = Field(max_length=20, min_length=5)
    birthday: datetime
    description: Optional[str] = Field(max_length=200)

    @field_validator('birthday')
    def validate_birthday(cls, v):
        if isinstance(v, datetime):
            v = v.date()
        if v > date.today():
            raise ValueError('Birthday cannot be in the future')
        return v

class ContactResponse(ContactBase):
    id: int    
    created_at: datetime | None
    updated_at: Optional[datetime] | None   

    model_config = ConfigDict(from_attributes=True)

class ContactBirthdayRequest(BaseModel):    
    days: int = Field(ge=1, le=31)
