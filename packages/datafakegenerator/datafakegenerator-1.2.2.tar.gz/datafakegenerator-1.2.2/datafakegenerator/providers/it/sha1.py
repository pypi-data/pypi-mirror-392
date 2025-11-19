from datafakegenerator.providers.base_provider import BaseProvider
import random
import hashlib
import string


class Sha1Provider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, length: int = 16, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.length = length

    def generate_non_blank(self, row_data=None):
        random_str = ''.join(random.choices(
            string.ascii_letters + string.digits, k=self.length))
        hashed = hashlib.sha1(random_str.encode('utf-8')).hexdigest()
        return hashed
