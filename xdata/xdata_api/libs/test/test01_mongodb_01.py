from pymongo import MongoClient
class MongoDBClient(object):
    def __init__(self, ip=None, user=None, password=None, port=None, db=None):
        self.ip = ip
        self.user = user
        self.password = password
        self.db = db
        self.port = int(port)
        # self.con = object
        self.con = MongoClient(
	    host=self.ip,
	    port=self.port,
	    username=self.user,
	    password=self.password,
	    authSource=self.db,
	    authMechanism='SCRAM-SHA-1')

    @staticmethod
    def addDic(theIndex, word, value):
        theIndex.setdefault(word, []).append(value)

    def __enter__(self):
        self.con = MongoClient.connect(
        host=self.ip,
        port=self.port,
        username=self.user,
        password=self.password,
        authSource=self.db,
        authMechanism='SCRAM-SHA-1')
        return self.con

    # def get_db(self):
    #     conn = MongoClient(
	   #  host=self.ip,
	   #  port=self.port,
	   #  username=self.user,
	   #  password=self.password,
	   #  authSource=self.db,
	   #  authMechanism='SCRAM-SHA-1')
    #     return conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()
        return self.con

    def list_collections(self, database=None):
    	with self.con as cursor:
            coll = cursor[database]
            result = coll.list_collection_names(session=None)
            return result

    def drop(self, database=None, collections=None):
    	with self.con as cursor:
            coll = cursor[database]
            result = coll[collections].drop()
            return result

    def create_index(self, database=None, collections=None, index=None):
    	with self.con as cursor:
            coll = cursor[database]
            result = coll[collections].create_index(index)
            return result



if __name__ == '__main__':
    db = MongoDBClient('192.168.1.91','root','123456',27017,'admin')
    # if db.list_collections('admin'):
    #     print('sucess')
    # else:
    #     print('error')
    # try:
    #     db = MongoDBClient('192.168.1.91','root','1234567',27017,'admin')
    #     if db.list_collections('admin'):
    #         print('sucess')
    # except Exception as e:
    #     print('error')
    #client = MongoConn('192.168.1.91','root','123456',27017,'admin')
    # client = db.get_db()
    # print(client)
    # TempleSpider = client['ows_anquandl']
    # temple_comment_collect_03 = TempleSpider['token_records']
    # temple_comment_collect_03.create_index('token')
    # temple_comment_collect_03.create_index('identityUid')
    # temple_comment_collect_03.create_index('createdDate')
    # #temple_comment_collect_04 = TempleSpider['token_records_01']
    # #temple_comment_collect_04.create_index('token')
    # #db.drop('ows_anquandl','token_records')
    # db.create_index('ows_anquandl','token_records_01','identityUid')
    print(db.list_collections('admin'))
