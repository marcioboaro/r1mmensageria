from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuthDetails(BaseModel):
    public_id: Optional[str]
    username: str
    cnpj:  Optional[str]
    rede: Optional[str]
    idmarketplace:  Optional[str]
    email: str
    password: str
    DateAt: Optional[datetime]
    DateUpdate: Optional[datetime]
