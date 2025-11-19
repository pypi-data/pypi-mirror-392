from datafakegenerator.providers.base_provider import BaseProvider
import random
import datetime


class InvoiceNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        prefixes = ["INV", "BILL", "RCPT", "PAY", "TXN"]
        prefix = random.choice(prefixes)
        year = datetime.datetime.now().year
        number = random.randint(1, 999999)

        # Randomly pick a format pattern
        formats = [
            f"{prefix}-{year}-{number:05d}",
            f"{prefix}-{number:06d}",
            f"{year}-{prefix}-{number:05d}",
            f"{prefix}{year}{number:04d}",
            f"{prefix.upper()}-{random.randint(10, 99)}-{number:04d}",
        ]
        return random.choice(formats)
