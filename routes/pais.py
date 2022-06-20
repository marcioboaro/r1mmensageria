from fastapi import APIRouter, Depends, HTTPException
from config.db import conn
from schemas.pais import Paises
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select
from auth.auth import AuthHandler

from cryptography.fernet import Fernet

pais = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

@pais.get(
    "/pais/{idPais}",
    tags=["pais"],
    response_model=Paises,
    description="Carrega um pais a partir de sua sigla",
)
def get_pais(idPais: str, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        pais = conn.execute(
            select([func.pais_get(idPais)])
        ).fetchone()
        return pais
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
