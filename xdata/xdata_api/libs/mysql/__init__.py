import pymysql
from libs.utils import MysqlClient


#验证mysql连接是否正常
def mysql_valid(ip,user,password,port):
    try:
        ip = ip
        user = user
        password = password
        port = port
    except Exception as e:
        return 'KeyError'
    else:
        try:
            with MysqlClient(ip=ip, user=user, password=password, port=port):
                return True
        except Exception as e:
            return False

#获取数据库连接对象
def mysql_conn(ip,user,password,port):
    try:
        with MysqlClient(ip=ip, user=user, password=password, port=port) as f:
            return f
        except Exception as e:
            return False

#数据库权限授权
def mysql_priv(ip,user,password,port,db,priv):
    try:
        with MysqlClient(ip=ip, user=user, password=password, port=port) as f:
            if priv == 0:
                sql1 = "create user '"+form.db_user+"'@'%' "+"identified by '"+form.db_password+"';"
                sql2 = "grant select on "+form.db_database+".* to '"+form.db_user+"'@'%';"
        except Exception as e:
            return False

