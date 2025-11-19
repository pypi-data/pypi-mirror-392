import random
import ipaddress
from datafakegenerator.providers.base_provider import BaseProvider


class IpAddressV4Provider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        return str(ipaddress.IPv4Address(random.randint(0, 2**32 - 1)))
