import random
import ipaddress
from datafakegenerator.providers.base_provider import BaseProvider


class IpAddressV4CidrProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        ip = ipaddress.IPv4Address(random.randint(0, 2**32 - 1))
        prefix = self.get_random_data_by_list([8, 16, 24, 32])
        return f"{ip}/{prefix}"
