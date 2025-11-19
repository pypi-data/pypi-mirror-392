from datafakegenerator.providers.base_provider import BaseProvider
import random


class PackageWeightProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        unit_ranges = {
            "mg": (100, 500000),
            "g": (1, 5000),
            "kg": (0.1, 200),
            "oz": (0.1, 500),
            "lb": (0.1, 400),
            "ton": (0.1, 10),
            "t": (0.1, 5)
        }

        unit = random.choice(list(unit_ranges.keys()))
        low, high = unit_ranges[unit]
        weight_value = round(random.uniform(low, high), 1)

        return f"{weight_value} {unit}"
