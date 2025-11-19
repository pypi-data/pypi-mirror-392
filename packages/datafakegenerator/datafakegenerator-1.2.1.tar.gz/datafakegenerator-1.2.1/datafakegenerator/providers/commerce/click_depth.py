from datafakegenerator.providers.base_provider import BaseProvider
import random


class ClickDepthProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        r = random.random()
        if r < 0.70:
            return random.randint(1, 4)
        elif r < 0.95:
            return random.randint(5, 8)
        else:
            return random.randint(9, 12)
