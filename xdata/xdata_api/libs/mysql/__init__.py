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
if __name__ == "__main__":
    print(mysql_valid('127.0.0.1','root','111111',3306))
