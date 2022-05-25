from app import db


class TermMixin:
    def has_term(self, term_key):
        return any([True for term in self.terms if term.term_key == term_key])

    def get_term(self, term_key):
        terms_list = list(filter(lambda x: True if x.term_key == term_key else False, self.terms))
        return terms_list[0].term_value if terms_list else None
