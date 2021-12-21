from fastapi import FastAPI, Depends
from routes.pais import pais
from routes.user import user
from routes.ms01_ms02 import ms01_ms02
from routes.ms03_ms04 import ms03_ms04
from routes.ms05_ms06 import ms05_ms06
from routes.ms07_ms08 import ms07_ms08
from routes.ms09_ms10 import ms09_ms10
from routes.ms11_ms11 import ms11_ms11
from routes.ms12_ms12 import ms12_ms12
from routes.ms14_ms15 import ms14_ms15
from routes.ms16_ms17 import ms16_ms17
from routes.ms18_ms19 import ms18_ms19
from routes.ms20_ms21 import ms20_ms21
from routes.lc16_lc16 import lc16_lc16
import uuid  
from config.db import conn
from config.log import logger
from auth.auth import AuthHandler
from schemas.auth import AuthDetails
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import re
import sys

app = FastAPI(
    title="Users API",
    description="a REST API using python and mysql",
    version="0.0.1",
)

auth_handler = AuthHandler()

@app.post('/signup', status_code=201)
def register(auth_details: AuthDetails):
    try:
        command_sql = None
        if auth_details.username is None or auth_details.password is None:
            return {"status_code":400, "detail":"Username ou Password não informado"}
        if not re.match(r"[^@]+@[^@]+\.[^@]+", auth_details.email):
            return {"status_code":203, "detail":"Por favor entre com um endereço de e-mail valido."}

        pass_ret = password_check(auth_details.password)
        if not pass_ret["password_ok"]:
            if pass_ret["length_error"]:
                pass_msg = "Por favor a senha deve ter pelo menos 12 posições."
            elif pass_ret["digit_error"]:
                pass_msg = "Por favor a senha deve ter pelo menos 1 posição númerica."
            elif pass_ret["uppercase_error"]:
                pass_msg = "Por favor a senha deve ter pelo menos 1 posição maiúscula."
            elif pass_ret["lowercase_error"]:
                pass_msg = "Por favor a senha deve ter pelo menos 1 posição minúscula."
            elif pass_ret["symbol_error"]:
                pass_msg = "Por favor a senha deve ter pelo menos 1 posição caracter especial."
            return {"status_code":203, "detail":pass_msg}
        # montando a chave idSolicitante
        idSolicitante = auth_details.cnpj + str(auth_details.rede).zfill(3) + str(auth_details.idmarketplace).zfill(3)

        # checando se já usuário cadastrado
        command_sql = f'''SELECT `AuthDetails`.`public_id`,
                                 `AuthDetails`.`username`,
                                 `AuthDetails`.`email`,
                                 `AuthDetails`.`password`,
                                 `AuthDetails`.`DateAt`,
                                 `AuthDetails`.`DateUpdate`
                            FROM `AuthDetails`
                            where `AuthDetails`.`email` = "{auth_details.email}";'''
        row = conn.execute(command_sql).fetchone()

        # checando se o usuário cadastrado está na lista de participantes
        if row is not None:
            return {"status_code":203, "detail":"Usuário já cadastrado"}

        command_sql = f'''SELECT `participantes`.`idParticipanteCNPJ`,
                                `participantes`.`idRede`,
                                `participantes`.`idMarketPlace`
                                    FROM `participantes`
                                    where `participantes`.`idParticipanteCNPJ` = "{auth_details.cnpj}"
                                    and `participantes`.`idRede`= "{auth_details.rede}"
                                    and `participantes`.`idMarketPlace`= "{auth_details.idmarketplace}";'''
        row = conn.execute(command_sql).fetchone()
        if row is None:
            return {"status_code": 400, "detail": "Usuário não é um participante cadastrado"}

        hashed_password = auth_handler.get_password_hash(auth_details.password)
        public_id = str(uuid.uuid4())

        # se está na lista de participantes então inserir usuário no banco
        command_sql = f'''INSERT INTO `AuthDetails`
                                    (`public_id`,
                                    `idRede`,
                                    `idMarketPlace`,
                                    `idParticipanteCNPJ`,
                                    `username`,
                                    `email`,
                                    `password`)
                                VALUES
                                    ('{public_id}',
                                    '{auth_details.rede}',
                                    '{auth_details.idmarketplace}',
                                    '{auth_details.cnpj}',
                                    '{auth_details.username}',
                                    '{auth_details.email}',
                                    '{hashed_password}');'''
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        row = conn.execute(command_sql)

        return { 'idSolicitante': idSolicitante }

    except:
        logger.error(sys.exc_info())
        result = dict()
        if command_sql is not None:
            result["command_sql"] = command_sql
        result['Error register'] = sys.exc_info()
        return result

@app.post('/login')
def login(auth_details: AuthDetails):
    try:
        command_sql = f'''SELECT    `AuthDetails`.`public_id`,
                                    `AuthDetails`.`idRede`,
                                    `AuthDetails`.`idMarketPlace`,
                                    `AuthDetails`.`idParticipanteCNPJ`,
                                    `AuthDetails`.`password`
                            FROM    `AuthDetails`
                            where   `AuthDetails`.`email` = "{auth_details.email}";'''
        row = conn.execute(command_sql).fetchone()
        ID_do_Solicitante = row[3] + str(row[1]).zfill(3) + str(row[2]).zfill(3)
        if (row is None) or (not auth_handler.verify_password(auth_details.password, row['password'])):
            return {'status_code':401, detail:'Invalid username and/or password'}
        token = auth_handler.encode_token(row['public_id'])
        return { 'token': token, 'ID_do_Solicitante': ID_do_Solicitante }
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error login'] = sys.exc_info()
        return result

@app.get('/protected')
def protected(public_id=Depends(auth_handler.auth_wrapper)):
    return { 'public_id': public_id }

def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        12 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    try:
        length_error = len(password) < 12
        digit_error = re.search(r"\d", password) is None
        uppercase_error = re.search(r"[A-Z]", password) is None
        lowercase_error = re.search(r"[a-z]", password) is None
        symbol_error = re.search(r"\W", password) is None
        password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)
        return {
            "password_ok": password_ok,
            "length_error": length_error,
            "digit_error": digit_error,
            "uppercase_error": uppercase_error,
            "lowercase_error": lowercase_error,
            "symbol_error": symbol_error
        }
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error password_check'] = sys.exc_info()
        return result

app.include_router(user)
app.include_router(pais)
app.include_router(ms01_ms02)
app.include_router(ms03_ms04)
app.include_router(ms05_ms06)
app.include_router(ms07_ms08)
app.include_router(ms09_ms10)
app.include_router(ms11_ms11)
app.include_router(ms12_ms12)
app.include_router(ms12_ms12)
app.include_router(ms14_ms15)
app.include_router(ms16_ms17)
app.include_router(ms18_ms19)
app.include_router(ms20_ms21)
app.include_router(lc16_lc16)
