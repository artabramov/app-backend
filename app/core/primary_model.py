from app import db
import time

SELECT_LIMIT = 5


class PrimaryModel(db.Model):
    __abstract__ = True
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()), )
    updated = db.Column(db.Integer(), nullable=False, default=0, onupdate=lambda: int(time.time()))
    deleted = db.Column(db.Integer(), nullable=False, default=0, index=True)

    def delete(self):
        self.deleted = int(time.time())

    @property
    def is_deleted(self):
        return self.deleted > 0
