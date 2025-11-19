import random
import ipaddress
from datafakegenerator.providers.base_provider import BaseProvider


class IpAddressV6CidrProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        ip = ipaddress.IPv6Address(random.randint(0, 2**128 - 1))
        prefix = self.get_random_data_by_list([32, 48, 64, 96, 128])
        return f"{ip}/{prefix}"
