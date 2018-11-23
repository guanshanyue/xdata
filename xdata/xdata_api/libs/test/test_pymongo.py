from pymongo import MongoClient
class MongoConn(object):
    def __init__(self, ip=None, user=None, password=None, port=None, db=None):
        self.ip = ip
        self.user = user
        self.password = password
        self.db = db
        self.port = int(port)
        self.con = object

    def get_db(self):
    	   self.con = MongoClient(
          host=self.ip,
          port=self.port,
          username=self.user,
          password=self.password,
          authSource=self.db,
          authMechanism='SCRAM-SHA-1')
        return self.con
    # @staticmethod
    # def addDic(theIndex, word, value):
    #     theIndex.setdefault(word, []).append(value)

   #  def __enter__(self):
   #      self.con = MongoClient(
   #          host=self.ip,
   #          port=self.port,
   #          username=self.user,
			# password=self.password,
			# authSource=self.db,
			# authMechanism='SCRAM-SHA-1')
   #      return self

    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     self.con.close()

if __name__ == '__main__':
	db = MongoConn('192.168.1.91','root','123456',27017,'admin')
	client = db.get_db()
	# print(type(db))
	# TempleSpider = db['ows_anquandl']
	# temple_comment_collect_03 = TempleSpider['token_records']
	# temple_comment_collect_03.create_index('token')
	# temple_comment_collect_03.create_index('identityUid')
	# temple_comment_collect_03.create_index('createdDate')
	# uri = "mongodb://root:123456@192.168.1.91:27017/?authSource=admin&authMechanism=SCRAM-SHA-1"
	# db = MongoClient(uri)
	# db = MongoClient(
 #            host='192.168.1.91',
 #            port=27017,
 #            username='root',
	# 		password='123456',
	# 		authSource='admin',
	# 		authMechanism='SCRAM-SHA-1')
	TempleSpider = client['ows_anquandl']
	temple_comment_collect_03 = TempleSpider['token_records']
	temple_comment_collect_03.create_index('token')
	temple_comment_collect_03.create_index('identityUid')
	temple_comment_collect_03.create_index('createdDate')
# client = MongoClient('example.com',
#                       username='user',
#                       password='password',
#                       authSource='the_database',
#                       authMechanism='SCRAM-SHA-1')
