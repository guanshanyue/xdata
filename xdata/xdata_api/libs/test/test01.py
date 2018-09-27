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

def list_to_json(*args):
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

print(list_to_json("db_user", "desc", "db_database","db_priv"))

a=list_to_json("db_user", "desc", "db_database","db_priv")

n =0
for i in a:
    if  a[n]["db_priv"] == '0':
        a[n]["db_priv"]='只读'
    elif a[n]["db_priv"] == '1':
        a[n]["db_priv"]='读写'
    else:
        continue
    n = n + 1
print(a)

