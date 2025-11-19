from datafakegenerator.providers.base_provider import BaseProvider
import random


class AirportTerminalProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        prefix = random.choice(["Terminal", 'T'])
        number = int(random.randint(1, 5))

        return f"{prefix} {number}" if prefix == "Terminal" else f"{prefix}{number}"
