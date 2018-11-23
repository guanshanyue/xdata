from public import app
from libs.tools import AttrDict
from docker import APIClient
from docker.errors import APIError, DockerException
import json
import requests
import os
import subprocess
import datetime
import base64
import uuid
import pymysql
from pymongo import MongoClient

class DockerClient(object):
    def __init__(self, base_url):
        self.client = APIClient(base_url=base_url, version='auto', timeout=30)
        self.auth_config = {
            'username': app.config['DOCKER_REGISTRY_AUTH'].get('username'),
            'password': app.config['DOCKER_REGISTRY_AUTH'].get('password')
        }

    def __repr__(self):
        return '<DockerClient %r>' % self.client.base_url

    def __del__(self):
        self.client.close()

    @property
    def api_version(self):
        return self.client.api_version

    def docker_info(self):
        return self.client.info()

    def pull_image(self, image, tag, stream=False):
        if stream:
            return self.client.pull(image, tag, auth_config=self.auth_config, stream=True)
        rst = self.client.pull(image, tag, auth_config=self.auth_config)
        last_message = json.loads(rst.split('\r\n')[-2])
        if last_message.get('error'):
            raise APIError(last_message['error'])

    def prune_images(self, filters=None):
        return self.client.prune_images(filters=filters)


class Container(DockerClient):
    def __init__(self, base_url, name):
        super().__init__(base_url)
        self.name = name
        self.host_config = {}

    def __repr__(self):
        return '<Container %r>' % self.name

    @property
    def info(self):
        cs = self.client.containers(all=True, filters={'name': self.name})
        info = AttrDict(cs[0]) if cs and self.api_version >= '1.21' else None
        if info is not None:
            info.running = info.State == 'running'
            if info.running and [x for x in self.client.top(self.name)['Processes'] if 'sleep 777d' in x]:
                info.Status = 'v_start exit'
        return info

    def stop(self, timeout=3):
        self.client.stop(self.name, timeout=timeout)

    def start(self):
        self.client.start(self.name)

    def restart(self, timeout=3):
        self.client.restart(self.name, timeout=timeout)

    def create(self, image, **kwargs):
        return self.client.create_container(image, host_config=self.host_config, **kwargs)

    def create_host_config(self, **kwargs):
        self.host_config = self.client.create_host_config(**kwargs)

    def remove(self):
        self.client.remove_container(self.name, force=True)

    def put_archive(self, path, data):
        return self.client.put_archive(self.name, path, data)

    def logs(self, stream=False, **kwargs):
        output = self.client.logs(self.name, stream=stream, **kwargs)
        return output if stream else output.decode()

    def exec_command(self, cmd, with_exit_code=False, user='root'):
        task = self.client.exec_create(self.name, cmd, user=user)
        output = self.client.exec_start(task['Id'], stream=False).decode()
        if with_exit_code:
            return self.client.exec_inspect(task['Id'])['ExitCode'], output
        return output

    def exec_command_with_base64(self, cmd, args_str='', timeout=30, token=None, with_exit_code=False, stream=False):
        token = token or uuid.uuid4().hex
        command = '/entrypoint.sh %d %s %s %s' % (timeout, token, base64.b64encode(cmd.encode()).decode(), args_str)
        task = self.client.exec_create(self.name, command)
        if with_exit_code:
            output = self.client.exec_start(task['Id'], stream=False).decode()
            return self.client.exec_inspect(task['Id'])['ExitCode'], output
        elif stream:
            return self.client.exec_start(task['Id'], stream=True)
        else:
            return self.client.exec_start(task['Id'], stream=False).decode()


class Registry(object):
    def __init__(self, base_url):
        self.api = base_url
        self.auth = (
            app.config['DOCKER_REGISTRY_AUTH'].get('username'),
            app.config['DOCKER_REGISTRY_AUTH'].get('password')
        )

    def list_tags(self, name):
        req_url = 'https://%s/v2/%s/tags/list' % (self.api, name)
        tags = requests.get(req_url, auth=self.auth).json().get('tags', [])
        tags = tags or []
        tags.reverse()
        return tags

    def delete(self, name, digest):
        req_url = 'https://%s/v2/%s/manifests/%s' % (self.api, name, digest)
        res = requests.delete(req_url, auth=self.auth)
        if res.status_code not in [202, 404]:
            raise Exception('Delete image error, code: %d content: %s' % (res.status_code, res.content))

    def list_images(self):
        req_url = 'https://%s/v2/_catalog' % self.api
        res = requests.get(req_url, auth=self.auth).json()
        return res.get('repositories', [])

    def get_tag_digest(self, name, tag):
        req_url = 'https://%s/v2/%s/manifests/%s' % (self.api, name, tag)
        res = requests.head(req_url, headers={'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}, auth=self.auth)
        return res.headers.get('Docker-Content-Digest')

    def get_last_modify_date(self, name, tag):
        req_url = 'https://%s/v2/%s/manifests/%s' % (self.api, name, tag)
        res = requests.get(req_url, auth=self.auth).json()
        last_history_date = json.loads(res['history'][0]['v1Compatibility'])['created'].split('.')[0]
        created = datetime.datetime.strptime(last_history_date, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
        return created.astimezone(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

    def __repr__(self):
        return '<Registry %r>' % self.api


class DockerImage(object):
    def __init__(self, base_url):
        self.client = APIClient(base_url=base_url, version='auto')
        self.full_name = None

    def build(self, path, name, tag):
        self.full_name = '{0}/{1}:{2}'.format(app.config['DOCKER_REGISTRY_SERVER'], name, tag)
        for item in self.client.build(path=path, tag=self.full_name, forcerm=False):
            detail = json.loads(item.decode().strip())
            if 'errorDetail' in detail:
                raise Exception('Build image error: ' + detail['errorDetail'].get('message', '未知错误'))

    def push(self, image=None):
        repository = image or self.full_name
        if repository is None:
            raise Exception('Push image error: argument <image> is missing.')
        for item in self.client.push(repository, auth_config=app.config['DOCKER_REGISTRY_AUTH'], stream=True):
            detail = json.loads(item.decode().strip())
            if 'errorDetail' in detail:
                raise Exception('Push image error: ' + detail['errorDetail'].get('message', '未知错误'))
            if 'aux' in detail:
                return detail['aux']['Digest']
        raise Exception('Push image error: 未知错误')

    def remove(self, image=None):
        repository = image or self.full_name
        if repository is None:
            raise Exception('Remove image error: argument <image> is missing.')
        self.client.remove_image(repository)


class Git(object):
    def __init__(self, work_tree_dir):
        self.work_tree = work_tree_dir
        self.git_dir = os.path.join(self.work_tree, '.git')
        self.base_command = 'git --git-dir=%s --work-tree=%s ' % (self.git_dir, self.work_tree)

    def _exec_command(self, *args):
        command = self.base_command + ' '.join(args)
        if args[0] == 'clone':
            command = 'git ' + ' '.join(args)
        status, output = subprocess.getstatusoutput(command)
        if status != 0:
            raise subprocess.SubprocessError(output)
        return output

    def clone(self, url):
        self._exec_command('clone', url, self.work_tree)

    def pull(self):
        self._exec_command('pull', '--all')

    def fetch_tags(self):
        self._exec_command('fetch', '--tags')

    def is_valid(self):
        return os.path.isdir(self.git_dir)

    @property
    def tags(self, count=5, refresh=True):
        if refresh:
            self.fetch_tags()
        output = self._exec_command(
            'for-each-ref',
            '--sort=-taggerdate',
            '--count={0}'.format(count),
            '--format=%(tag)',
            'refs/tags'
        )
        return output.strip().splitlines()

    def __repr__(self):
        return '<Git %r>' % self.work_tree

class MysqlClient(object):
    def __init__(self, ip=None, user=None, password=None, db=None, port=None):
        self.ip = ip
        self.user = user
        self.password = password
        self.db = db
        self.port = int(port)
        self.con = object

    @staticmethod
    def addDic(theIndex, word, value):
        theIndex.setdefault(word, []).append(value)

    def __enter__(self):
        self.con = pymysql.connect(
            host=self.ip,
            user=self.user,
            passwd=self.password,
            db=self.db,
            charset='utf8mb4',
            port=self.port
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def execute(self, sql=None):
        with self.con.cursor() as cursor:
            sqllist = sql
            cursor.execute(sqllist)
            result = cursor.fetchall()
            self.con.commit()
        return result

    def search(self, sql=None):
        data_dict=[]
        id = 0
        with self.con.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            sqllist = sql
            cursor.execute(sqllist)
            result = cursor.fetchall()
            for field in cursor.description:
                if id == 0:
                    data_dict.append({'title': field[0], "key": field[0], "fixed": "left", "width": 150})
                    id += 1
                else:
                    data_dict.append({'title': field[0], "key": field[0], "width": 200})
            len = cursor.rowcount
        return {'data': result, 'title': data_dict, 'len': len}

    def dic_data(self, sql=None):
        with self.con.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            sqllist = sql
            cursor.execute(sqllist)
            result = cursor.fetchall()
        return result

    def showtable(self, table_name):
        with self.con.cursor() as cursor:
            sqllist = '''
                    select aa.COLUMN_NAME,
                    aa.DATA_TYPE,aa.COLUMN_COMMENT, cc.TABLE_COMMENT 
                    from information_schema.`COLUMNS` aa LEFT JOIN 
                    (select DISTINCT bb.TABLE_SCHEMA,bb.TABLE_NAME,bb.TABLE_COMMENT 
                    from information_schema.`TABLES` bb ) cc  
                    ON (aa.TABLE_SCHEMA=cc.TABLE_SCHEMA and aa.TABLE_NAME = cc.TABLE_NAME )
                    where aa.TABLE_SCHEMA = '%s' and aa.TABLE_NAME = '%s';
                    ''' % (self.db, table_name)
            cursor.execute(sqllist)
            result = cursor.fetchall()
            td = [
                {
                    'Field': i[0], 
                    'Type': i[1],
                    'Extra': i[2],
                    'TableComment': i[3]
                } for i in result
                ]
        return td

    def gen_alter(self, table_name):
        with self.con.cursor() as cursor:
            sqllist = '''
                           select aa.COLUMN_NAME,aa.COLUMN_DEFAULT,aa.IS_NULLABLE,
                           aa.COLUMN_TYPE,aa.COLUMN_KEY,aa.COLUMN_COMMENT, cc.TABLE_COMMENT 
                           from information_schema.`COLUMNS` aa LEFT JOIN 
                           (select DISTINCT bb.TABLE_SCHEMA,bb.TABLE_NAME,bb.TABLE_COMMENT 
                           from information_schema.`TABLES` bb ) cc  
                           ON (aa.TABLE_SCHEMA=cc.TABLE_SCHEMA and aa.TABLE_NAME = cc.TABLE_NAME )
                           where aa.TABLE_SCHEMA = '%s' and aa.TABLE_NAME = '%s';
                           ''' % (self.db, table_name)
            cursor.execute(sqllist)
            result = cursor.fetchall()
            td = [
                {
                    'Field': i[0],
                    'Type': i[3],
                    'Null': i[2],
                    'Key': i[4],
                    'Default': i[1],
                    'Extra': i[5],
                    'TableComment': i[6]
                } for i in result
            ]
        return td

    def basename(self):
        with self.con.cursor() as cursor:
            cursor.execute('show databases')
            result = cursor.fetchall()
            data = [c for i in result for c in i]
            a = ["information_schema","performance_schema","mysql"]
            for i in a:
                if i in data:
                    data.remove(i)
            return data

    def index(self, table_name):
        with self.con.cursor() as cursor:
            cursor.execute('show keys from %s' % table_name)
            result = cursor.fetchall()
            di = [
                {
                    'Non_unique': '是', 
                    'key_name': i[2], 
                    'column_name': i[4], 
                    'index_type': i[10]
                }
                if i[1] == 0
                else 
                {
                    'Non_unique': '否', 
                    'key_name': i[2], 
                    'column_name': i[4], 
                    'index_type': i[10]
                }
                for i in result 
                ]

            dic = {}
            c = []
            for i in di:
                self.addDic(dic, i['key_name'], i['column_name'])
            for t in dic:
                """
                初始化第一个value
                将value 数据变为字符串
                转为字典对象数组
                """
                str1 = dic[t][0]

                for i in range(1, len(dic[t])):
                    str1 = str1 + ',' + dic[t][i]

                temp = {}
                for g in di:
                    if t == g['key_name']:
                        temp.setdefault('Non_unique', g['Non_unique'])
                        temp.setdefault('index_type', g['index_type'])
                temp.setdefault('column_name', str1)
                temp.setdefault('key_name', t)
                c.append(temp)
            return c

    def tablename(self):
        with self.con.cursor() as cursor:
            cursor.execute('show tables')
            result = cursor.fetchall()
            data = [c for i in result for c in i]
            return data

    def grant_priv(self,db_user,db_password,db_database,db_priv,is_create_user=1):
        sql1 = "create user '"+db_user+"'@'%' "+"identified by '"+db_password+"';"
        with self.con.cursor() as cursor:
            if db_priv == '0':
                sql2 = "grant select, lock tables, show view on "+db_database+".* to '"+db_user+"'@'%';"
            elif  db_priv == '1':
                sql2 = "grant select, insert, update, delete, create, drop, index, alter, create temporary tables, lock tables, execute, create view, show view, create routine, alter routine, event, trigger on "+db_database+".* to '"+db_user+"'@'%';"
            else:
                return false
            if is_create_user == 1:
                cursor.execute(sql1)
            cursor.execute(sql2)
            result = cursor.fetchall()
            data = [c for i in result for c in i]
            return data

    def revoke_priv(self,db_user,db_database,db_priv,is_drop_user=0):
        sql1 = "drop user '"+db_user+"'@'%';"
        sql2 = ''
        with self.con.cursor() as cursor:
            if is_drop_user == 1:
                cursor.execute(sql1)
            else:
                if db_priv == '0':
                    sql2 = "revoke select, lock tables, show view on "+db_database+".* from '"+db_user+"'@'%';"
                elif  db_priv == '1':
                    sql2 = "revoke select, insert, update, delete, create, drop, index, alter, create temporary tables, lock tables, execute, create view, show view, create routine, alter routine, event, trigger on "+db_database+".* from '"+db_user+"'@'%';"
                else:
                    return false
                cursor.execute(sql2)
            cursor.execute('flush privileges')
            result = cursor.fetchall()
            data = [c for i in result for c in i]
            return data

    def reset_password(self,db_user,db_password):
        sql = "update mysql.user set password=password('"+db_password+"') where user='"+db_user+"';"
        with self.con.cursor() as cursor:
            cursor.execute(sql)
            cursor.execute('flush privileges;')
            result = cursor.fetchall()
            data = [c for i in result for c in i]
            return data

class MongoConn(object):
    def __init__(self, ip=None, user=None, password=None, port=None, db=None):
        self.ip = ip
        self.user = user
        self.password = password
        self.db = db
        self.port = int(port)
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

    def get_db(self):
        conn = MongoClient(
        host=self.ip,
        port=self.port,
        username=self.user,
        password=self.password,
        authSource=self.db,
        authMechanism='SCRAM-SHA-1')
        return conn

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