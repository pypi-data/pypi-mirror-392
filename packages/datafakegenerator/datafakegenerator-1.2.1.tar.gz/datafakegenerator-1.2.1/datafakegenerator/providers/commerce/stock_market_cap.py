import random
from datafakegenerator.providers.base_provider import BaseProvider
from providers.commerce.money import MoneyProvider


class StockMarketCapProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        m = MoneyProvider(min=10_000_000, max=100_000_000_000, currency='$')
        value_str = m.generate_non_blank()
        value = float(value_str.replace('$', '').replace(',', '').strip())

        if value >= 1_000_000_000:
            formatted = f"${value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            formatted = f"${value / 1_000_000:.2f}M"
        else:
            formatted = f"${value / 1_000:.2f}K"
        return formatted
