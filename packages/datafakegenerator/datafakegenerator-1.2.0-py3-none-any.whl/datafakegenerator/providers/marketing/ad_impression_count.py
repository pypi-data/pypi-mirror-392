from datafakegenerator.providers.base_provider import BaseProvider
import random


class AdImpressionCountProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def _format_number(self, num):
        if num < 1000:
            return str(num)
        elif num < 1_000_000:
            return f"{round(num / 1000, 1)}K"
        else:
            return f"{round(num / 1_000_000, 1)}M"

    def generate_non_blank(self, row_data=None):
        r = random.random()
        if r < 0.70:
            num = random.randint(10, 5_000)
        elif r < 0.95:
            num = random.randint(5_000, 500_000)
        else:
            num = random.randint(500_000, 10_000_000)

        return self._format_number(num)
