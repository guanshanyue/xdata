import json
data = [
    [
        "test02",
        '1',
        "doms",
        "0"
    ],
    [
        "test03",
        '1',
        "doms",
        "0"
    ],
    [
        "test04",
        'null',
        "doms",
        "0"
    ],
    [
        "test05",
        "测试专用",
        "doms",
        "1"
    ]
]

# for i in data:
#     print(i)

# b = json.dumps(data)
# c = json.loads(b)

# print(b)
# print(c)

ret = []
for i in data:
    item = {}
    print(len(i))
    n = 0
    for j in i:
        if n == 0:
            item['db_user'] = j
        elif n == 1:
            item['desc'] = j
        elif n == 2:
            item['db_database'] = j
        elif n == 3:
            item['db_priv'] = j
        else:
            continue
        n = n+1
    ret.append(item)
#print(ret)
import json
#print(json.dumps(ret))

def list_to_json(data,*args):
    ret = []
    for i in data:
        item = {}
        n = 0
        if len(i)<=len(args):
            for j in i:
                item[args[n]] = j
                n = n+1
        ret.append(item)
    return ret

# print(list_to_json("db_user", "desc", "db_database","db_priv"))

# a=list_to_json("db_user", "desc", "db_database","db_priv")

# n =0
# for i in a:
#     if  a[n]["db_priv"] == '0':
#         a[n]["db_priv"]='只读'
#     elif a[n]["db_priv"] == '1':
#         a[n]["db_priv"]='读写'
#     else:
#         continue
#     n = n + 1
# print(a)

# def list_only_to_json(data):
#     ret = []
#     n = 1
#     for i in data:
#         item = {}
#         item[n] = i
#         ret.append(item)
#         n = n + 1
#     return ret

def list_only_to_json(data):
    ret = []
    n = 1
    for i in data:
        item = {}
        item['id'] = n
        item['name'] = i
        n = n + 1
        ret.append(item)
    return ret

data_result = [
        "information_schema",
        "192_168_1_76_3306_pref",
        "Yearning",
        "airflow",
        "doms",
        "flask_api",
        "inception",
        "mysql",
        "performance_schema",
        "pref",
        "redis_admin",
        "rest"]

data_result_01 = [
        "information_schema",
        "192_168_1_76_3306_pref"
    ],
#print(list_only_to_json(data_result))
a = ["information_schema","performance_schema"]
#data_result.remove("information_schema")
for i in a:
    if i in data_result:
        data_result.remove(i)
#data_result.remove("performance_schema")
for i in data_result:
    print(i)
#print(list_only_to_json(data_result))
li = [1, 2, 3, 4]
li.pop(2)
print(li)
# Output [1, 2, 4]


data_result = [
    {
        "account_id": 24,
        "db_database": "doms",
        "db_priv": "0",
        "id": 9
    },
    {
        "account_id": 24,
        "db_database": "airflow",
        "db_priv": "0",
        "id": 15
    }
]

# for i in data_result:
#     print(i['db_database'])

data_result = [
        {
            "id": 1,
            "name": "192_168_1_76_3306_pref"
        },
        {
            "id": 2,
            "name": "Yearning"
        }
    ]


data_result = [
        "information_schema",
        "192_168_1_76_3306_pref",
        "Yearning",
        "airflow",
        "doms",
        "flask_api",
        "inception",
        "mysql",
        "performance_schema",
        "pref",
        "redis_admin",
        "rest"]
 
delete_data = [
            {
                "db_database": "doms",
                "db_port": 3306
            },
            {
                "db_database": "airflow",
                "db_port": 3306
            }
        ]
def list_only_to_json(data,*agrs):
    ret = []
    n = 1
    for i in data:
        item = {}
        item['id'] = n
        item['name'] = i
        item['status'] = "0"
        n = n + 1
        ret.append(item)
    return ret

print(list_only_to_json(data_result))
dd = list_only_to_json(data_result)
item = []
for i in delete_data:
    item.append(i['db_database'])
print(item)



for i in dd:
    for j in item:
        if i['name'] == j:
            i['status'] = '1'
print(dd)




def __enter__(self):
    self.con = MongoClient(
        host=self.ip,
        port=self.port,
        username=self.user,
        password=self.password,
        authSource=self.db,
        authMechanism='SCRAM-SHA-1')
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    self.con.close()