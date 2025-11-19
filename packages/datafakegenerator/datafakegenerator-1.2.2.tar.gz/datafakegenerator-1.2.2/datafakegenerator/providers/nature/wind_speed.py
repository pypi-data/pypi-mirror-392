from datafakegenerator.providers.base_provider import BaseProvider
import random


class WindSpeedProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, unit: str = "mph", **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.unit = unit or self.get_random_data_by_list(
            ["mph", "km/h", "m/s"])

    def generate_non_blank(self, row_data=None):
        speed = round(random.uniform(0, 200), 1)
        return f"{speed} {self.unit}"
