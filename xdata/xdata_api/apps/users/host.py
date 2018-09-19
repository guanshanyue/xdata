from flask import Blueprint, request
from apps.users.models import  User, UserInfo
from libs.tools import json_response, JsonParser, Argument
from apps.setting import utils, Setting
import math
from public import db
from libs.decorators import require_permission
from libs.utils import MysqlClient
from apps.assets.utils import excel_parse


blueprint = Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET'])
@require_permission('users_host_view')
def get():
    form, error = JsonParser(Argument('page', type=int, default=1, required=False),
                             Argument('pagesize', type=int, default=10, required=False),
                             #Argument('host_query', type=dict, required=False), 
                             Argument('host_query', type=dict, default={"name_field":"","zone_field":""}, required=False),).parse(request.args)
    if error is None:
        #print('host_ng', form)
        host_data = User.query
        if form.page == -1:
            return json_response({'data': [x.to_json() for x in host_data.all()], 'total': -1})
        if form.host_query.get('name_field'):
            host_data = host_data.filter(Host.name.like('%{}%'.format(form.host_query['name_field'])))
        if form.host_query.get('zone_field'):
            host_data = host_data.filter_by(zone=form.host_query['zone_field'])

        result = host_data.limit(form.pagesize).offset((form.page - 1) * form.pagesize).all()
        return json_response({'data': [x.to_json() for x in result], 'total': host_data.count()})
    return json_response(message=error)

@blueprint.route('/', methods=['POST'])
@require_permission('users_host_add')
def post():
    form, error = JsonParser('name', 'type', 'zone', 'db_host', 'db_user', 'db_password','db_port',
                             Argument('desc', nullable=True, required=False)).parse()
    if error is None:
        host = User(**form)
        host.save()
        return json_response(host)
    return json_response(message=error)


@blueprint.route('/<int:user_id>', methods=['DELETE'])
@require_permission('users_host_del')
def delete(user_id):
    host = User.query.get_or_404(user_id)
    if UserInfo.query.filter_by(user_id=user_id).first():
        return json_response(message='请先取消与应用的关联后，再尝试删除该主机。')
    host.delete()
    return json_response()


@blueprint.route('/<int:user_id>', methods=['PUT'])
@require_permission('users_host_edit')
def put(user_id):
    form, error = JsonParser('name', 'type', 'zone', 'db_host', 'db_user', 'db_password','db_port',
                             Argument('desc', nullable=True, required=False)).parse()
    if error is None:
        host = User.query.get_or_404(user_id)
        host.update(**form)
        return json_response(host)
    return json_response(message=error)

@blueprint.route('/zone/', methods=['GET'])
@require_permission('users_host_valid | users_host_exec')
def fetch_groups():
    zones = db.session.query(User.zone.distinct().label('zone')).all()
    return json_response([x.zone for x in zones])

@blueprint.route('/type/', methods=['GET'])
@require_permission('users_host_valid | users_host_exec')
def fetch_types():
    types = db.session.query(User.type.distinct().label('type')).all()
    return json_response([x.type for x in types])

#检验数据库是否能正常连接
@blueprint.route('/<int:user_id>/valid', methods=['GET'])
@require_permission('users_host_valid')
def get_valid(user_id):
    cli = User.query.get_or_404(user_id)
    try:
        with MysqlClient(ip=cli.db_host, user=cli.db_user, password=cli.db_password, port=cli.db_port):
            return json_response()
    except Exception as e:
        return json_response(message='连接失败')

    

