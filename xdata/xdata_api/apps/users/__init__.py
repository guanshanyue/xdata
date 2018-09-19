from apps.users import host
from apps.users import host_exec


def register_blueprint(app):
    app.register_blueprint(host.blueprint, url_prefix='/users/hosts')
    app.register_blueprint(host_exec.blueprint, url_prefix='/users/hosts_exec')
