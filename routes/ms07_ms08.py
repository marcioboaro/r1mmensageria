# -*- coding: utf-8 -*-
from tkinter import E
from typing import Any
import sys
import uuid  # for public id
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from config.db import conn
from config.log import logger
from auth.auth import AuthHandler
from schemas.ms07 import MS07
from cryptography.fernet import Fernet
import random
import os
import json

ms07_ms08 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

# @ms07_ms08.post("/ms05", tags=["ms08"], response_model=MS08, description="Cancelamento de reserva")
@ms07_ms08.post("/msg/v01/lockers/cancellation", tags=["ms08"], description="Cancelamento de reserva")
def ms07(ms07: MS07, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("MS07 - Cancelamento de reserva")
        logger.info(ms07)
        logger.info(public_id)
        if ms07.ID_do_Solicitante is None:
            raise HTTPException(status_code=422, detail="M08006 - ID_do_Solicitante obrigatório")
        if len(ms07.ID_do_Solicitante) != 20: # 20 caracteres
            raise HTTPException(status_code=422, detail="M08006 - ID_do_Solicitante deve conter 20 caracteres")
        if ms07.ID_Rede_Lockers is None:
            raise HTTPException(status_code=422, detail="M08008 - ID_Rede_Lockers obrigatório")
        if ms07.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms07.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M08011 - ID_Rede_Lockers inválido")
        if ms07.Data_Hora_Solicitacao is None:
            ms07.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if ms07.ID_da_Estacao_do_Locker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{ms07.ID_da_Estacao_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M08023 - ID_da_Estacao_do_ Locker inválido")
        if ms07.URL_CALL_BACK is None:
            raise HTTPException(status_code=422, detail="M08046 - URL para Call Back é obrigatória")

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="MS07 - Cancelamento de reserva")
