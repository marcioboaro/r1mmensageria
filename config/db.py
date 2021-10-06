from sqlalchemy import create_engine, MetaData

user = "remoteuser"
passw = "new_password"
port = 3306
base = "rede1minuto"
host = "rede1min.eastus2.cloudapp.azure.com"
charset = "utf8"

str_conn = "mysql+pymysql://"+str(user)+":"+str(passw)+"@"+str(host)+":"+str(port)+"/"+str(base)+"?charset="+charset
engine = create_engine(str_conn, pool_size=20, max_overflow=100, execution_options={"no_parameters":True}, echo=False)

meta = MetaData()
conn = engine.connect()
