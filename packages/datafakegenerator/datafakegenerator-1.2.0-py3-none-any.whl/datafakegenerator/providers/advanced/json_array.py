from datafakegenerator.providers.base_provider import BaseProvider
import random


class JsonArrayProvider(BaseProvider):
    def __init__(self, *, blank_percentage: float = 0.0, min_elements: int = 1, max_elements: int = 3, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.min_elements = min_elements
        self.max_elements = max_elements

    def generate_non_blank(self, row_data=None):
        num_elements = random.randint(self.min_elements, self.max_elements)
        return str([{} for _ in range(num_elements)])
