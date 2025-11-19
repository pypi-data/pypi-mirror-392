from datafakegenerator.providers.base_provider import BaseProvider
import random
import string


class JsonWebTokenProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        def random_base64url(length): return ''.join(random.choices(
            string.ascii_letters + string.digits + "-_", k=length))
        header = random_base64url(8)
        payload = random_base64url(16)
        signature = random_base64url(32)

        return f"{header}.{payload}.{signature}"
