from datafakegenerator.providers.base_provider import BaseProvider
import random


class BarcodeUpcProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        return ''.join(str(random.randint(0, 9)) for _ in range(12))
