from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: Optional[int]
    public_id: str
    name: Optional[str]
    email: str
    password: str
    DateAt: Optional[datetime]
    DateUpdate: Optional[datetime]

class UserCount(BaseModel):
    total: int