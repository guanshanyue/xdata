from flask import Blueprint, request
from apps.users.models import  User, UserInfo, UserPriv
from libs.tools import json_response, JsonParser, Argument,list_to_json
from apps.setting import utils, Setting
import math
from public import db
from libs.decorators import require_permission
from libs.utils import MysqlClient
from apps.assets.utils import excel_parse
blueprint = Blueprint(__name__, __name__)


# @blueprint.route('/', methods=['GET'])
# @require_permission('users_info_view')
# def get():
#     form, error = JsonParser(Argument('page', type=int, default=1, required=False),
#                              Argument('pagesize', type=int, default=10, required=False),
#                              #Argument('host_query', type=dict, required=False), 
#                              Argument('host_query', type=dict, default={"name_field":""}, required=False),).parse(request.args)
#     if error is None:
#         #print('host_ng', form)
#         host_data = UserInfo.query
#         if form.page == -1:
#             return json_response({'data': [x.to_json() for x in host_data.all()], 'total': -1})
#         if form.host_query.get('name_field'):
#             host_data = host_data.filter(UserInfo.db_user.like('%{}%'.format(form.host_query['name_field'])))
#         result = host_data.limit(form.pagesize).offset((form.page - 1) * form.pagesize).all()
#         return json_response({'data': [x.to_json() for x in result], 'total': host_data.count()})
#     return json_response(message=error)

@blueprint.route('/', methods=['GET'])
@require_permission('users_info_view')
def get():
    form, error = JsonParser(Argument('page', type=int, default=1, required=False),
                             Argument('pagesize', type=int, default=10, required=False),
                             Argument('host_query', type=dict, default={"name_field":"","user_id":""}, required=False),).parse(request.args)
    if error is None:
        host_data = db.session().query(UserInfo,UserPriv).\
        filter(UserInfo.id == UserPriv.account_id,UserInfo.user_id == form.host_query['user_id'])\
        .with_entities(UserInfo.user_id,UserInfo.id,UserInfo.id,UserInfo.db_user, UserInfo.desc,UserPriv.db_database,UserPriv.db_priv)
        #host_data = host_data.filter(UserInfo.user_id == 1)
        if form.page == -1:
            return json_response({'data': [x.to_json() for x in host_data.all()], 'total': -1})
        if form.host_query.get('name_field'):
            host_data = host_data.filter(UserInfo.db_user.like('%{}%'.format(form.host_query['name_field'])))
        result = host_data.limit(form.pagesize).offset((form.page - 1) * form.pagesize).all()
        db_record = list_to_json(result,"user_id","account_id","priv_id","db_user", "desc", "db_database","db_priv")
        n = 0
        for i in db_record:
            if db_record[n]["db_priv"] == '0':
                db_record[n]["db_priv"]='只读'
            elif db_record[n]["db_priv"] == '1':
                db_record[n]["db_priv"]='读写'
            else:
                continue
            n = n + 1
        return json_response({'data':db_record,'total': host_data.count()})
    return json_response(message=error)

@blueprint.route('/', methods=['POST'])
@require_permission('users_info_add')
def post():
    form, error = JsonParser('user_id','db_user', 'db_password',
    						'db_database','db_priv',
                             Argument('desc', nullable=True, required=False)).parse()
    if error is None:
        if not User.query.filter_by(id=form.user_id).first():
            return json_response(message="管理员账号错误")
        if UserInfo.query.filter_by(user_id=form.user_id,db_user=form.db_user).first():
            return json_response(message="账号已存在，不能重复创建")
        cli = User.query.get_or_404(form.user_id)
        try:
            with MysqlClient(ip=cli.db_host, user=cli.db_user, password=cli.db_password, port=cli.db_port, db=form.db_database) as f:
                f.user_priv(form.db_user,form.db_password,form.db_database,form.db_priv)
        except Exception as e:
            return json_response(message='连接失败')
        host = UserInfo(user_id=form.user_id,db_user=form.db_user,db_password=form.db_password,desc=form.desc)
        host.save()
        userpriv = UserPriv(account_id=host.id,db_database=form.db_database,db_priv=form.db_priv)
        userpriv.save()
        return json_response(host)
    return json_response(message=error)

@blueprint.route('/<int:user_id>/database/', methods=['GET'])
@require_permission('users_info_valid | users_info_view')
def get_db(user_id):
    cli = User.query.get_or_404(user_id)
    try:
        with MysqlClient(ip=cli.db_host, user=cli.db_user, password=cli.db_password, port=cli.db_port) as f:
            res = f.basename()
            return json_response(res)
    except Exception as e:
        return json_response(message='连接失败')

@blueprint.route('/<int:account_id>/reset_password/', methods=['PUT'])
@require_permission('users_info_valid | users_info_edit')
def resetpassword(account_id):
    form, error = JsonParser('new_password').parse()
    if error is None:
        user_info = UserInfo.query.get_or_404(account_id)
        cli = User.query.get_or_404(user_info.user_id)
        try:
            with MysqlClient(ip=cli.db_host, user=cli.db_user, password=cli.db_password, port=cli.db_port) as f:
                res = f.reset_password(user_info.db_user,form.new_password)
                #return json_response(res)
        except Exception as e:
            return json_response(message='连接失败')
        data = user_info.update(db_password=form.new_password)
        return json_response(data)
    return json_response(message=error)


