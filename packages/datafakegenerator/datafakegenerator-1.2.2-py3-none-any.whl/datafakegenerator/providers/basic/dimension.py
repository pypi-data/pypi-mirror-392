from datafakegenerator.providers.base_provider import BaseProvider
import random


class DimensionProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, type: str = "2D", **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.type = type

    def generate_non_blank(self, row_data=None):
        if self.type == "2D":
            width = round(random.uniform(1, 5000), 1)
            height = round(random.uniform(1, 5000), 1)
            return f"{width}x{height}"
        else:
            width = round(random.uniform(1, 500), 1)
            height = round(random.uniform(1, 500), 1)
            depth = round(random.uniform(1, 500), 1)
            return f"{width}x{height}x{depth}"
