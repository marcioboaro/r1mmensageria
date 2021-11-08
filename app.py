from fastapi import FastAPI, Depends, HTTPException
from routes.pais import pais
from routes.user import user
from routes.ms01_ms02 import ms01_ms02
from routes.ms03_ms04 import ms03_ms04
from routes.ms05_ms06 import ms05_ms06
import uuid  
from config.db import conn
from config.log import logger
from auth.auth import AuthHandler
from schemas.auth import AuthDetails
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
        if auth_handler.check_user_exists(auth_details.username):
            raise HTTPException(status_code=400, detail="Username já existe")
        if auth_handler.check_user_exists(auth_details.cnpj):
            raise HTTPException(status_code=400, detail="CNPJ já existe")
        if auth_handler.check_email_exists(auth_details.email):
            raise HTTPException(status_code=400, detail="Email já existe")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", auth_details.email):
            raise HTTPException(status_code=203, detail="Por favor entre com um endereço de e-mail valido.")

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
            raise HTTPException(status_code=203, detail=pass_msg)

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
        if row is None:
            command_sql = f'''SELECT `participantes`.`idParticipanteCNPJ`,
                                    `participantes`.`idRede`,
                                    `participantes`.`idMarketPlace`
                                        FROM `participantes`
                                        where `participantes`.`idParticipanteCNPJ` = "{auth_details.cnpj}"
                                        and `participantes`.`idRede`= "{auth_details.rede}
                                        and `participantes`.`idMarketPlace`= "{auth_details.idmarketplace};'''
            row = conn.execute(command_sql).fetchone()

            # se está na lista de participantes então inserir usuário no banco
            if row is not None:
                hashed_password = auth_handler.get_password_hash(auth_details.password)
                public_id = str(uuid.uuid4())
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
                                            '{auth_details,idmarketplace}',
                                            '{auth_details.cnpj}',
                                            '{auth_details.username}',
                                            '{auth_details.email}',
                                            '{hashed_password}');'''
                command_sql = command_sql.replace("'None'", "Null")
                row = conn.execute(command_sql)

        else:
            raise HTTPException(status_code=400, detail='O nome de usuário já está em uso')
        return { 'idSolicitante': idSolicitante }
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error register'] = sys.exc_info()
        return result

@app.post('/login')
def login(auth_details: AuthDetails):
    try:
        command_sql = f'''SELECT    `AuthDetails`.`public_id`,
                                    `AuthDetails`.`password`
                            FROM    `AuthDetails`
                            where   `AuthDetails`.`email` = "{auth_details.email}";'''
        row = conn.execute(command_sql).fetchone()
        if (row is None) or (not auth_handler.verify_password(auth_details.password, row['password'])):
            raise HTTPException(status_code=401, detail='Invalid username and/or password')
        token = auth_handler.encode_token(row['public_id'])
        return { 'token': token }
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
