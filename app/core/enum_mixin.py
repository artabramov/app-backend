from enum import Enum
from marshmallow import ValidationError


class EnumMixin(Enum):
    @classmethod
    def get_obj(cls, **kwargs):
        key = list(kwargs.keys())[0]
        value = kwargs[key]
        if value in cls._member_map_:
             return cls._member_map_[value]
        else:
            raise ValidationError({key: ['incorrect value for enum.']})
