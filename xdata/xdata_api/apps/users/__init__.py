from apps.users import user
from apps.users import host_exec
from apps.users import user_info
from apps.users import mongodb

def register_blueprint(app):
    app.register_blueprint(user.blueprint, url_prefix='/users/hosts')
    app.register_blueprint(host_exec.blueprint, url_prefix='/users/hosts_exec')
    app.register_blueprint(user_info.blueprint, url_prefix='/users/user_info')
    app.register_blueprint(mongodb.blueprint, url_prefix='/users/mongodb')

