from datafakegenerator.providers.base_provider import BaseProvider
import random


class CreditScoreProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        return random.randint(300, 850)
