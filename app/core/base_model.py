from app import db
import time


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()), )
    updated_at = db.Column(db.Integer(), nullable=False, default=0, onupdate=lambda: int(time.time()))
    deleted_at = db.Column(db.Integer(), nullable=False, default=0, index=True)

    def delete(self, commit=True):
        self.deleted_at = int(time.time())
        if commit:
            db.session.commit()

