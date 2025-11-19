from datafakegenerator.providers.base_provider import BaseProvider
import bcrypt
import random
import string


class PasswordHashProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, min_length: int = 8, max_length: int = 16, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.min_length = min_length
        self.max_length = max_length

    def generate_non_blank(self, row_data=None):
        length = random.randint(self.min_length, self.max_length)
        all_chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.<>?"
        plain_password = "".join(random.choices(all_chars, k=length))
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")
