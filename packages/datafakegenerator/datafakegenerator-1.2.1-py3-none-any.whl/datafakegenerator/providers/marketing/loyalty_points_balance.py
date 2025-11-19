from datafakegenerator.providers.base_provider import BaseProvider
import random


class LoyaltyPointsBalanceProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        r = random.random()
        if r < 0.75:
            # Most customers: normal everyday balances
            points = random.randint(10, 5000)
        elif r < 0.95:
            # Occasional high earners
            points = random.randint(5000, 50000)
        else:
            # Rare super loyal users
            points = random.randint(50000, 500000)

        return f"{points:,}"
