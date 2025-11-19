from datafakegenerator.providers.base_provider import BaseProvider
import random


class MemoryFootprintProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        unit = random.choice(["MB", "GB"])

        if unit == "MB":
            value = random.randint(50, 3000)
            return f"{value}MB"

        else:
            value = random.uniform(0.5, 32.0)
            formatted = f"{value:.1f}".rstrip("0").rstrip(".")
            return f"{formatted}GB"
