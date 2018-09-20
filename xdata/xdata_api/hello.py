# coding=utf-8
from flask import Flask
from flask_migrate import Migrate,MigrateCommand
from flask_script import Shell,Manager
from flask_sqlalchemy import SQLAlchemy
import config

from public import db
import apps.account.models
import apps.configuration.models
import apps.deploy.models
import apps.assets.models
import apps.schedule.models
import apps.setting.models
import apps.users.models

app = Flask(__name__)
app.config.from_object(config)
#db = SQLAlchemy(app)
manager = Manager(app)
#第一个参数是Flask的实例，第二个参数是Sqlalchemy数据库实例
migrate = Migrate(app,db) 

#manager是Flask-Script的实例，这条语句在flask-Script中添加一个db命令
#123
manager.add_command('db',MigrateCommand)
if __name__ == '__main__':
     manager.run()



