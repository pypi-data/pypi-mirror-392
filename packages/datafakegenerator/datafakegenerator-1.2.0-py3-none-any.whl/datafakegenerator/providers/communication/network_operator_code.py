from datafakegenerator.providers.base_provider import BaseProvider
import random


class NetworkOperatorCodeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        mcc = random.randint(200, 999)
        mnc = random.randint(0, 999)
        mnc_str = f"{mnc:02d}" if mnc < 100 else f"{mnc:03d}"
        return f"{mcc}{mnc_str}"
