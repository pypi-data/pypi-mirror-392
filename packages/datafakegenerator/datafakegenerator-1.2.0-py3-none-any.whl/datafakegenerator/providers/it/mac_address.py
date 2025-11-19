from datafakegenerator.providers.base_provider import BaseProvider
import random


class MacAddressProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        mac = [random.randint(0x00, 0xFF) for _ in range(6)]
        return ':'.join(f'{byte:02X}' for byte in mac)
