from datafakegenerator.providers.base_provider import BaseProvider
import random


class ExpenseAmountProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, min: float = 0, max: float = 1000, currency: str = '$', **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.min = min
        self.max = max
        self.currency = currency

    def generate_non_blank(self, row_data=None):
        amount = random.uniform(self.min, self.max)
        formatted_amount = f"{amount:.2f}"

        return formatted_amount
