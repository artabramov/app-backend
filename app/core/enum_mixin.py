from enum import Enum


class EnumMixin(Enum):
    @classmethod
    def get_value(cls, value):
        return cls._member_map_[value] if value in cls._member_map_ else value