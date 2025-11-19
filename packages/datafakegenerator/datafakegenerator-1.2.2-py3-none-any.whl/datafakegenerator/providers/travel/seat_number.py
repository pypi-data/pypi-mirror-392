from datafakegenerator.providers.base_provider import BaseProvider
import random


class SeatNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        row = random.randint(1, 60)
        seat_letter = random.choice(["A", "B", "C", "D", "E", "F"])
        return f"{row}{seat_letter}"
