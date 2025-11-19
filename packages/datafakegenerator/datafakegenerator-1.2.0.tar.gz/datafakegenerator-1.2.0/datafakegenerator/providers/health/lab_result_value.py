from datafakegenerator.providers.base_provider import BaseProvider
import random


class LabResultValueProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        if random.random() < 0.4:
            return str(random.randint(1, 300))
        else:
            return f"{round(random.uniform(1.0, 300.0), 1)}"
