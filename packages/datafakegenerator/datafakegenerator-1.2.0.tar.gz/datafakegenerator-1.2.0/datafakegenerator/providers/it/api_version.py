from datafakegenerator.providers.base_provider import BaseProvider
import random


class ApiVersionProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        major = random.randint(1, 10)
        if random.random() < 0.5:
            minor = random.randint(0, 9)
            return f"v{major}.{minor}"
        else:
            return f"v{major}"
