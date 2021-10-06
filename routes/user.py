from fastapi import APIRouter
from config.db import conn
from schemas.user import User
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select

from cryptography.fernet import Fernet

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
    command_sql = """SELECT `user`.`id`,
                            `user`.`public_id`,
                            `user`.`name`,
                            `user`.`email`,
                            `user`.`password`,
                            `user`.`DateAt`,
                            `user`.`DateUpdate`
                        FROM `user`;"""
    return conn.execute(command_sql).fetchall()
