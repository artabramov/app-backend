from app import db


class MetaMixin:
    def has_meta(self, meta_key):
        return any([True for meta in self.meta if meta.meta_key == meta_key])

    def get_meta(self, meta_key):
        meta_list = list(filter(lambda x: True if x.meta_key == meta_key else False, self.meta))
        return meta_list[0].meta_value if meta_list else None
