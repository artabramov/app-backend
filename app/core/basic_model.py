from app import db
from app.core.meta_model import MetaModel
import time

SELECT_LIMIT = 5


class BasicModel(MetaModel):
    __abstract__ = True
    deleted = db.Column(db.Integer(), nullable=False, default=0, index=True)

    def delete(self):
        self.deleted = int(time.time())

    @property
    def is_deleted(self):
        return self.deleted > 0
