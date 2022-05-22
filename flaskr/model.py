from datetime import datetime
from flaskr import db


class Dataset(db.Model):
    __tablename__ = "dataset"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    data_row = db.Column(db.Integer, default=0)
    desc = db.Column(db.String(255), nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
