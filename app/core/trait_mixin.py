from app import db


class TraitMixin:
    def has_trait(self, trait_key):
        return any([True for trait in self.traits if trait.trait_key == trait_key])

    def get_trait(self, trait_key):
        traits_list = list(filter(lambda x: True if x.trait_key == trait_key else False, self.traits))
        return traits_list[0].trait_value if traits_list else None
