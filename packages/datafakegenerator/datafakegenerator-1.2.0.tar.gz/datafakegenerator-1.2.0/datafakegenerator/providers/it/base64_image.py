import os
import base64
import random
from datafakegenerator.providers.base_provider import BaseProvider


class Base64ImageProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def _random_bytes(self, length: int = 64) -> bytes:
        return os.urandom(length)

    def generate_non_blank(self) -> str:
        fmt = self.get_random_data_by_list(self.format['file']["image"])
        raw_bytes = self._random_bytes(random.randint(64, 256))
        b64_data = base64.b64encode(raw_bytes).decode("utf-8")
        return f"data:image/{fmt};base64,{b64_data}"
