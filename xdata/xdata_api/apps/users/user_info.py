from flask import Blueprint, request
from apps.users.models import  User, UserInfo, UserPriv
from libs.tools import json_response, JsonParser, Argument
from apps.setting import utils, Setting
import math
from public import db
from libs.decorators import require_permission
from libs.utils import MysqlClient
from apps.assets.utils import excel_parse
blueprint = Blueprint(__name__, __name__)

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
            with MysqlClient(ip=cli.db_host, user=cli.db_user, password=cli.db_password, port=cli.db_port, db='doms') as f:
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
