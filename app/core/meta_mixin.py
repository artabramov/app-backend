from app import db


class MetaMixin:

    def has_meta(self, meta_key):
        return any([True for meta in self.meta if meta.meta_key == meta_key])

    def set_meta(self, parent_id, meta_key, meta_value):
        #meta_value = meta_data[meta_key]
        #user_meta = UserMeta(user.id, meta_key, meta_value)

        #term_obj = term_class()
        term = self.__class__.__dict__['term_class'](parent_id, meta_key, meta_value)
        db.session.add(term)
        db.session.flush()
        db.session.commit()
        return term

    def get_meta(self, meta_key):
        meta_list = list(filter(lambda x: True if x.meta_key == meta_key else False, self.meta))
        return meta_list[0].meta_value if meta_list else None

    def del_meta(self, meta_key):
        pass
