from datafakegenerator.providers.base_provider import BaseProvider
import random


class SensorReadingProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        value = random.uniform(0.01, 200.00)
        return f"{value:.2f}"
