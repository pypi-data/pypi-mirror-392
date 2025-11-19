from datafakegenerator.providers.base_provider import BaseProvider


class DiscountPercentageProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        return f"{int(self.generate_number(min=5, max=95))}%"
