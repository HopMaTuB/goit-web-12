from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birth_date: date
    additional_data:str | None = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class Contact(ContactBase):
    id: int

    class Config:
        orm_mode = True
