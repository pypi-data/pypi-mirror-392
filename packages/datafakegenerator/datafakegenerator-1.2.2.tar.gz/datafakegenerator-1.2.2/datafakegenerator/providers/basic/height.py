from datafakegenerator.providers.base_provider import BaseProvider
import random


class HeightProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        unit = self.get_random_data_by_list(self.basic['height_units'])

        if unit == "mm":
            value = round(random.uniform(100, 2500), 1)
        elif unit == "cm":
            value = round(random.uniform(10, 250), 1)
        elif unit == "m":
            value = round(random.uniform(0.3, 3.0), 2)
        elif unit == "in":
            value = round(random.uniform(4, 100), 1)
        elif unit == "ft":
            value = round(random.uniform(1, 8), 2)
        else:
            value = round(random.uniform(1, 100), 1)

        return f"{value} {unit}"
