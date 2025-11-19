from datafakegenerator.providers.base_provider import BaseProvider
import string
import random


class NftTokenIdProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, length: int = 16, hex_only: bool = False, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.length = length
        self.hex_only = hex_only

    def generate_non_blank(self, row_data=None):
        if self.hex_only:
            chars = '0123456789abcdef'
        else:
            chars = string.ascii_letters + string.digits

        return ''.join(random.choice(chars) for _ in range(self.length))
