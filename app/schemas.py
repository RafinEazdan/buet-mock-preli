from pydantic import BaseModel
from typing import Optional

from pyparsing import Opt


class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = None

class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company_id: Optional[int] = None

class ParseRequest(BaseModel):
    text: str
    llm: Optional[str] = "gpt-4o-mini"

class ParseResponse(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    found_in_database: bool
    company: Optional[str] = None