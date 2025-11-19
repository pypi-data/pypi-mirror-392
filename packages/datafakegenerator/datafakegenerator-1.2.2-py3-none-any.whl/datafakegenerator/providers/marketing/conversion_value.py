from datafakegenerator.providers.base_provider import BaseProvider
import random


class ConversionValueProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        style = random.choice(["currency", "credits"])

        if style == "currency":
            r = random.random()
            if r < 0.85:
                amount = round(random.uniform(1, 500), 2)
            else:
                amount = round(random.uniform(100, 100000), 2)

            return f"${amount:,.2f}"

        else:
            credits = random.randint(1, 500)
            return f"{credits} credits"
