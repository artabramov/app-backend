from app import db
from datetime import datetime


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=False), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=False), default='1970-01-01 00:00:00', onupdate=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=False), default='1970-01-01 00:00:00', nullable=False, index=True)

    def delete(self, commit=True):
        self.deleted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if commit:
            db.session.commit()
