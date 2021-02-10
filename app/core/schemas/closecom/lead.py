from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, AnyUrl, Schema

class SpreadSheetLeadCreate(BaseModel):
    name: str
    customer: str
    internal_status: str
    contacts: list
    lead_fields: Optional[dict] = None
