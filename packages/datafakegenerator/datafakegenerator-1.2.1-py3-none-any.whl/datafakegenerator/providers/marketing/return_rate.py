from datafakegenerator.providers.base_provider import BaseProvider
import random


class ReturnRateProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        odd = random.random()

        if odd < 0.1:
            return f"{random.randint(0, 1000)}%"
        elif odd < 0.4:
            return f"{random.randint(0, 100)}%"
        else:
            return f"{random.randint(0, 50)}%"
