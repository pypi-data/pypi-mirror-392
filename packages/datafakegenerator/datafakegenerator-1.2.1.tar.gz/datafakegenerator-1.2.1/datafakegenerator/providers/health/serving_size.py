from datafakegenerator.providers.base_provider import BaseProvider
import random


class ServingSizeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        quantity = random.randint(1, 3)
        units = [
            "cup", "cups", "tbsp", "tsp", "g", "mg", "slice", "plate", "bowl"
        ]

        unit = random.choice(units)
        if unit in ["g", "mg"]:
            return f"{random.randint(50, 500)}{unit}"

        return f"{quantity} {unit}"
