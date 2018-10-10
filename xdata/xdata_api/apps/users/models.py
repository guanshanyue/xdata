from public import db
from libs.model import ModelMixin
import datetime


class User(db.Model, ModelMixin):
    __tablename__ = 'user_hosts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    desc = db.Column(db.String(255))
    type = db.Column(db.String(50))
    zone = db.Column(db.String(50))
    db_host = db.Column(db.String(255))
    db_user = db.Column(db.String(128))
    db_password = db.Column(db.String(128))
    db_port = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % self.name

class UserInfo(db.Model, ModelMixin):
    __tablename__ = 'user_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id =  db.Column(db.Integer, db.ForeignKey('user_hosts.id'))
    db_user = db.Column(db.String(128))
    db_password = db.Column(db.String(128))
    desc = db.Column(db.String(255))

    __table_args__ = (
        db.Index('idx_user_id', 'user_id'),
    )

    def __repr__(self):
        return '<UserInfo %r>' % self.name

class UserPriv(db.Model, ModelMixin):
    __tablename__ = 'user_privileges'

    id = db.Column(db.Integer, primary_key=True)
    account_id =  db.Column(db.Integer, db.ForeignKey('user_accounts.id'))
    db_database = db.Column(db.String(128))
    db_priv = db.Column(db.String(128))

    __table_args__ = (
        db.UniqueConstraint('account_id', 'db_database', name='uniq_account_id_db_database'),
    )

    def __repr__(self):
        return '<UserInfo %r>' % self.name