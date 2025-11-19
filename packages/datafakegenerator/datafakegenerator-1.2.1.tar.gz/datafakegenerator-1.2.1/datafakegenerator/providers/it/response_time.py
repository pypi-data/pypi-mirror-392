from datafakegenerator.providers.base_provider import BaseProvider
import random


class ResponseTimeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        if random.random() < 0.7:
            ms = random.randint(10, 1000)
            return f"{ms}ms"
        else:
            s = round(random.uniform(0.5, 5), 2)
            return f"{s}s"
