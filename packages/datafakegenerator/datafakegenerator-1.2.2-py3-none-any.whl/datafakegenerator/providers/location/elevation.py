from datafakegenerator.providers.base_provider import BaseProvider
import random


class ElevationProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        if random.random() < 0.5:
            elevation = random.randint(0, 15000)
            return f"{elevation} ft"
        else:
            elevation = random.randint(0, 4500)
            return f"{elevation} m"
