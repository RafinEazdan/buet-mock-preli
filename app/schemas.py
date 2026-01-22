from pydantic import BaseModel
from typing import Optional


class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = None

class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company_id: Optional[int] = None