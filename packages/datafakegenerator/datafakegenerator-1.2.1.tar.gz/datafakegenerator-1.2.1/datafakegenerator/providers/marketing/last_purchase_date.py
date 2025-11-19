from datafakegenerator.providers.base_provider import BaseProvider
from datetime import datetime, timedelta
import random


class LastPurchaseDateProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, years_ago: int = 5, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.years_ago = years_ago

    def generate_non_blank(self, row_data=None):
        end_date = datetime.now() - timedelta(days=1)  # yesterday
        start_date = end_date - timedelta(days=365 * self.years_ago)
        random_date = start_date + (end_date - start_date) * random.random()
        return random_date.strftime("%Y-%m-%d")
