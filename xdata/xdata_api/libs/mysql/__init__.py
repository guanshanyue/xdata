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
def mysql_conn(ip,user,password,port):
    db = pymysql.connect(host=ip,user=user,passwd=password,db=db,charset='utf8mb4',port=port)
    return db
