from datafakegenerator.providers.base_provider import BaseProvider
import random


class InGameCurrencyBalanceProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, max: int = 99999, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.max = max

    def generate_non_blank(self, row_data=None):
        return random.randint(0, self.max)
