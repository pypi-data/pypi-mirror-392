from datafakegenerator.providers.base_provider import BaseProvider
from providers.commerce.money import MoneyProvider


class ProductPriceProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        m = MoneyProvider(min=1, max=1000, currency='$')
        return m.generate_non_blank()
