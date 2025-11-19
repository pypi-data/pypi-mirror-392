from datafakegenerator.providers.base_provider import BaseProvider
import random


class PrescriptionIdProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        prefixes = [
            "RX", "MED", "SCRIPT", "DRUG", "PHARM", "RXN", "RXP", "MD"
        ]
        prefix = random.choice(prefixes)
        number = random.randint(100000, 999999)

        return f"{prefix}{number}"
