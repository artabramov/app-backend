from app import db


class PropMixin:
    def has_prop(self, prop_key):
        return any([True for prop in self.props if prop.prop_key == prop_key])

    def get_prop(self, prop_key):
        props_list = list(filter(lambda x: True if x.prop_key == prop_key else False, self.props))
        return props_list[0].prop_value if props_list else None
