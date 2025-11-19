from datafakegenerator.providers.base_provider import BaseProvider
import random
import datetime
import string


class SkuProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        year = datetime.datetime.now().year
        letters = ''.join(random.choices(
            string.ascii_uppercase, k=random.randint(2, 3)))
        digits = ''.join(random.choices(string.digits, k=random.randint(3, 5)))

        formats = [
            f"SKU-{digits}-{letters}",
            f"PRD-{year}-{random.randint(100, 999)}",
            f"ITEM-{digits}-{letters}",
            f"SKU-{letters}-{digits}",
            f"INV-{digits}-{letters}",
            f"CODE-{year}-{letters}",
        ]
        return random.choice(formats)
