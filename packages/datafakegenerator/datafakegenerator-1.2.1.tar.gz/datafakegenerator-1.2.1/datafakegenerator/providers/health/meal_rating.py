from datafakegenerator.providers.base_provider import BaseProvider
import random


class MealRatingProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        rating = round(random.uniform(1.0, 5.0), 1)
        return f"{rating}"
