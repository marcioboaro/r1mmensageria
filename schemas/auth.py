from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuthDetails(BaseModel):
    public_id: Optional[str]
    username: str
    email: str
    password: str
    DateAt: Optional[datetime]
    DateUpdate: Optional[datetime]
