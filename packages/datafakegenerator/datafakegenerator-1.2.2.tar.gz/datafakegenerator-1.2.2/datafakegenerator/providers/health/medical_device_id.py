from datafakegenerator.providers.base_provider import BaseProvider
import random


class MedicalDeviceIdProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        prefixes = ["MD", "EQ", "ME", "DEV", "ICU", "SURG", "LAB"]
        prefix = random.choice(prefixes)
        number = random.randint(10000, 99999)
        return f"{prefix}-{number}"
