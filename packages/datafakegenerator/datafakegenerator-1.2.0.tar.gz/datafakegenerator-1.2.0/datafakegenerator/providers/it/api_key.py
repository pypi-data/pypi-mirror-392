from datafakegenerator.providers.base_provider import BaseProvider
import random
import string


class ApiKeyProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, prefix: str = None, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.prefix = prefix

    def generate_non_blank(self, row_data=None):
        chosen_prefix = self.prefix or random.choice(self.it['prefix'])
        chars = string.ascii_letters + string.digits
        key_body = ''.join(random.choice(chars) for _ in range(48))
        return f"{chosen_prefix}{key_body}"
