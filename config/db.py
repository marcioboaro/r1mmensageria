from sqlalchemy import create_engine, MetaData

user = "rede1minuto"
passw = "k9X1wj2UEj5FD5G2H4pl"
port = 3306
base = "rede1minuto"
host = "dbprod.rede1minuto.com.br"
charset = "utf8"

str_conn = "mysql+pymysql://"+str(user)+":"+str(passw)+"@"+str(host)+":"+str(port)+"/"+str(base)+"?charset="+charset
engine = create_engine(str_conn, pool_size=20, max_overflow=100, execution_options={"no_parameters":True}, echo=False)

meta = MetaData()
conn = engine.connect()
