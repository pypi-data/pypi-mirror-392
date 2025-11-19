import random
import string
from datafakegenerator.providers.base_provider import BaseProvider


class BitcoinAddressProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, ** kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        self.address_prefixes = ["1", "3", "bc1"]

    def _generate_base58(self, length: int) -> str:
        return "".join(self.get_random_data_by_list(self.base58_chars) for _ in range(length))

    def generate_non_blank(self, row_data=None):
        prefix = self.get_random_data_by_list(self.address_prefixes)

        if prefix == "bc1":
            core = "".join(self.get_random_data_by_list(string.ascii_lowercase + string.digits)
                           for _ in range(random.randint(25, 40)))
        else:
            core = self._generate_base58(random.randint(25, 34))

        return prefix + core
