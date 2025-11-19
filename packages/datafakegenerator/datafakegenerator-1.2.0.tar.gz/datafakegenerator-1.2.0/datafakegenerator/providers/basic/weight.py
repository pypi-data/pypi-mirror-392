from datafakegenerator.providers.base_provider import BaseProvider
import random


class WeightProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        unit = self.get_random_data_by_list(self.basic['weight_units'])

        if unit in ["g", "gram"]:
            value = round(random.uniform(1, 5000), 1)
        elif unit in ["kg", "kilogram"]:
            value = round(random.uniform(1, 200), 1)
        elif unit in ["oz"]:
            value = round(random.uniform(1, 5000), 1)
        elif unit in ["lb", "lbs", "pound"]:
            value = round(random.uniform(1, 440), 1)
        elif unit in ["st"]:
            value = round(random.uniform(1, 30), 1)
        elif unit in ["ton", "tonne"]:
            value = round(random.uniform(0.1, 100), 2)
        else:
            value = round(random.uniform(1, 100), 1)
        return f"{value} {unit}"
