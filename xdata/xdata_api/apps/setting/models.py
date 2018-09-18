from public import db
from libs.model import ModelMixin


class GlobalConfig(db.Model, ModelMixin):
    __tablename__ = 'setting_configs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    desc = db.Column(db.String(255))
    value = db.Column(db.Text)

    def __repr__(self):
        return '<GlobalConfig %r>' % self.name
