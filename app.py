from http.client import OK
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
from routes.lc07_lc07 import lc07_lc07
from routes.lc11_lc11 import lc11_lc11
from routes.lc13_lc13 import lc13_lc13
from routes.lc16_lc16 import lc16_lc16
from routes.lc18_lc18 import lc18_lc18
from routes.lc51_lc51 import lc51_lc51
from routes.lc53_lc53 import lc53_lc53
from routes.lc55_lc55 import lc55_lc55
from routes.lc57_lc57 import lc57_lc57
from routes.lc59_lc59 import lc59_lc59
from routes.lc61_lc61 import lc61_lc61
from routes.lc63_lc63 import lc63_lc63
from routes.lc65_lc65 import lc65_lc65
from routes.lc67_lc67 import lc67_lc67
from routes.lc69_lc69 import lc69_lc69
import uuid  
from config.db import conn, engine
from config.log import logger
from auth.auth import AuthHandler
from schemas.auth import AuthDetails
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import re
import sys
from fastapi.middleware.cors import CORSMiddleware
from auth.auth import AuthHandler
from schemas.password_change import ChangePassword

app = FastAPI(
    title="Users API",
    description="a REST API using python and mysql",
    version="1.0.1",
)

origins = [
"http://localhost",
"http://localhost:8080",
"http://localhost:*",
"*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_handler = AuthHandler()

@app.get("/")
def raiz():
    return OK

@app.post("/password-change", status_code=201)
def passwordChange(change_password: ChangePassword, public_id=Depends(auth_handler.auth_wrapper)):
    try:

        if change_password.new_password is not None and change_password.new_password_verify is not None:
            command_sql = f'''SELECT * from `AuthDetails` WHERE `AuthDetails`.`email` = "{change_password.email}";'''
            row = conn.execute(command_sql).fetchone()

            if row is None:
                return {"status_code": 203, "detail": "Usuário não encontrado"}

        if change_password.new_password != change_password.new_password_verify:
            return {"status_code": 400, "detail": "As senhas não conferem"}

        hashed_password = auth_handler.get_password_hash(change_password.new_password)

        command_sql = f'''UPDATE `AuthDetails` SET password="{hashed_password}" WHERE email="{change_password.email}";'''
        row = conn.execute(command_sql)
        return {"status_code": 200, "detail": "Success"}
        
    except:
        logger.error(sys.exc_info())
        result = dict()
        if command_sql is not None:
            result["command_sql"] = command_sql
        result['Error register'] = sys.exc_info()
        return result

@app.post('/signup', status_code=201)
def register(auth_details: AuthDetails):
    try:
        command_sql = None
        if auth_details.username is None or auth_details.password is None:
            return {"status_code":400, "detail":"Username ou Password não informado"}
        if not re.match(r"[^@]+@[^@]+\.[^@]+", auth_details.email):
            return {"status_code":203, "detail":"Por favor entre com um endereço de e-mail valido."}

        if auth_details.idmarketplace != 8:
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
        if auth_details.idmarketplace != 8:
            idSolicitante = auth_details.cnpj + str(auth_details.rede).zfill(3) + str(auth_details.idmarketplace).zfill(3) 
        else:
            idSolicitante = auth_details.cnpj 


            # checando se já usuário cadastrado
            command_sql = f'''SELECT `AuthDetails`.`public_id`,
                                    `AuthDetails`.`username`,
                                    `AuthDetails`.`email`,
                                    `AuthDetails`.`password`,
                                    `AuthDetails`.`DateAt`,
                                    `AuthDetails`.`DateUpdate`
                                FROM `AuthDetails`
                                where `AuthDetails`.`email` = "{auth_details.email}"
                                and `AuthDetails`.`idRede`= "{auth_details.rede}"
                                and `AuthDetails`.`idMarketPlace`= "{auth_details.idmarketplace}";'''                      
            
            row = conn.execute(command_sql).fetchone()        # checando se já usuário cadastrado
            # checando se o usuário cadastrado está na lista de participantes
            if row is not None:
                return {"status_code":203, "detail":"Usuário já cadastrado."}
            command_sql = f'''SELECT `participantes`.`idParticipanteCNPJ`,
                                    `participantes`.`idRede`,
                                    `participantes`.`idMarketPlace`
                                        FROM `participantes`
                                        where `participantes`.`idParticipanteCNPJ` = "{auth_details.cnpj}"
                                        and `participantes`.`idRede`= "{auth_details.rede}"
                                        and `participantes`.`idMarketPlace`= "{auth_details.idmarketplace}";'''
            row = conn.execute(command_sql).fetchone()
            if row is None and auth_details.idmarketplace != 8:
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
async def login(auth_details: AuthDetails):
    try:
        print("started login")
        command_sql = f'''SELECT    `AuthDetails`.`public_id`,
                                    `AuthDetails`.`idRede`,
                                    `AuthDetails`.`idMarketPlace`,
                                    `AuthDetails`.`idParticipanteCNPJ`,
                                    `AuthDetails`.`password`
                            FROM    `AuthDetails`
                            where   `AuthDetails`.`email` = "{auth_details.email}";'''
        print("before sql command exec")
        row = conn.execute(command_sql).fetchone()
        print("after sql command exec: ")
        print(row)
        if (row is None) or (not auth_handler.verify_password(auth_details.password, row['password'])):
            print("case error before returning")
            return {'status_code':401, 'detail':'Invalid username and/or password'}
        ID_do_Solicitante = row[3] + str(row[1]).zfill(3) + str(row[2]).zfill(3)
        print("before encoding token")
        token = auth_handler.encode_token(row['public_id'])
        print("after encoding token | before returning result")
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
app.include_router(lc07_lc07)
app.include_router(lc11_lc11)
app.include_router(lc13_lc13)
app.include_router(lc16_lc16)
app.include_router(lc18_lc18)
app.include_router(lc51_lc51)
app.include_router(lc53_lc53)
app.include_router(lc55_lc55)
app.include_router(lc57_lc57)
app.include_router(lc59_lc59)
app.include_router(lc61_lc61)
app.include_router(lc63_lc63)
app.include_router(lc65_lc65)
app.include_router(lc67_lc67)
app.include_router(lc69_lc69)
