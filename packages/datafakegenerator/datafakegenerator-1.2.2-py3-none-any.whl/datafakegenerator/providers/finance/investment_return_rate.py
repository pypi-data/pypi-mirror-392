from datafakegenerator.providers.base_provider import BaseProvider
import random


class InvestmentReturnRateProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, min_return: float = -20.0, max_return: float = 20.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.min_return = min_return
        self.max_return = max_return

    def generate_non_blank(self, row_data=None):
        rate = round(random.uniform(self.min_return, self.max_return), 1)
        return f"{rate}%"
