import random
import string
from datafakegenerator.providers.base_provider import BaseProvider


class EthereumAddressProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self) -> str:

        hex_chars = string.hexdigits.lower()[:16]  # '0123456789abcdef'
        address_body = ''.join(self.get_random_data_by_list(
            hex_chars) for _ in range(40))

        address = '0x' + ''.join(
            c.upper() if random.random() < 0.3 else c for c in address_body
        )

        return address
