from sqlalchemy import create_engine, MetaData
from config.config import ConfigServer

config = ConfigServer()

database_config = config.get_database_config()

user = database_config["USER"]
passw = database_config["PASSWORD"]
port = database_config["PORT"]
base = database_config["BASE"]
host = database_config["HOST"]
charset = "utf8"

str_conn = "mysql+pymysql://"+str(user)+":"+str(passw)+"@"+str(host)+":"+str(port)+"/"+str(base)+"?charset="+charset
engine = create_engine(str_conn, pool_size=20, max_overflow=100, execution_options={"no_parameters":True}, echo=False)

meta = MetaData()
conn = engine.connect()
