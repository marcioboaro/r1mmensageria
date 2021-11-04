from fastapi import APIRouter
from config.db import conn
from config.log import logger
from schemas.user import User
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select
from schemas.user import User
from cryptography.fernet import Fernet
import sys

user = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)


@user.get(
    "/users",
    tags=["users"],
    response_model=List[User],
    description="Get a list of all users",
)
def get_users():
    try:
        users = conn.execute(
            select([
                func.user_id.label("id"),
                func.user_name.label("name"),
                func.user_email.label("email"),
                func.user_password.label("password"),
                func.user_role.label("role"),
            ])
        ).fetchall()
        return users
    except Exception as e:
        logger.error(e)
        result = dict()
        result['Error get_users'] = e
        return result      
