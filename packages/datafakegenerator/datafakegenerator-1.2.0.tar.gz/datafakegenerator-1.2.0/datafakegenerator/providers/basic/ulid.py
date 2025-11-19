import time
import os
import base64
from datafakegenerator.providers.base_provider import BaseProvider


class UlidProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        timestamp = int(time.time() * 1000)
        timestamp_bytes = timestamp.to_bytes(6, 'big')
        random_bytes = os.urandom(10)
        ulid_bytes = timestamp_bytes + random_bytes
        return self.encode_base32(ulid_bytes)
