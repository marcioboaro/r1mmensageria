from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuthDetails(BaseModel):
    public_id: Optional[str]
    username: str
    cnpj:  Optional[str]
    rede: Optional[int]
    idmarketplace:  Optional[int]
    email: str
    password: str
    DateAt: Optional[datetime]
    DateUpdate: Optional[datetime]
