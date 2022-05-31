from app import db
import time


class SecondaryModel(db.Model):
    __abstract__ = True
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()), )
    updated = db.Column(db.Integer(), nullable=False, default=0, onupdate=lambda: int(time.time()))
