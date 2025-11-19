from datafakegenerator.providers.base_provider import BaseProvider
import random


class DiscountValueProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, currency: str = '$', **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.currency = currency

    def generate_non_blank(self, row_data=None):
        style = random.choice(["percentage", "flat"])

        if style == "percentage":
            value = random.choice([5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 80])
            return f"{value}%"

        value = random.randint(1, 500)
        return f"${value} off"
