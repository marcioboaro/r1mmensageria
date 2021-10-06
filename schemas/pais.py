from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Paises(BaseModel):
    idPais: Optional[str]
    PaisNome: str
    DateAt: Optional[datetime]
    DateUpdate: Optional[datetime]
