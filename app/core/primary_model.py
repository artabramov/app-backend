from app import db
from app.core.secondary_model import SecondaryModel
import time

SELECT_LIMIT = 5


class PrimaryModel(SecondaryModel):
    __abstract__ = True
    deleted = db.Column(db.Integer(), nullable=False, default=0, index=True)

    def delete(self):
        self.deleted = int(time.time())

    @property
    def is_deleted(self):
        return self.deleted > 0
