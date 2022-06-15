from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time


class ChangePassword(BaseModel):
    new_password : str
    new_password_verify: str
    email : str
