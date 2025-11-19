from datafakegenerator.providers.base_provider import BaseProvider
import random


class TimezoneOffsetProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, prefix: str = "UTC", **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.prefix = prefix

    def generate_non_blank(self, row_data=None):
        offset = random.randint(-12, 14)
        sign = "+" if offset >= 0 else ""
        return f"{self.prefix}{sign}{offset}"
