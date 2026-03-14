"""Simple user model for demo login."""


class User:
    def __init__(self, id_, role="compliance"):
        self.id = id_
        self.role = role

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
