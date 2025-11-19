from datafakegenerator.providers.base_provider import BaseProvider
import random


class DeliveryTimeWindowProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        start_hour = random.choice(range(7, 19))  # 7AM to 6PM
        end_hour = start_hour + random.choice([2, 3, 4])  # 2–4 hour window

        fmt = (
            lambda h: f"{h if h <= 12 else h - 12}{'AM' if h < 12 else 'PM'}")
        return f"{fmt(start_hour)}-{fmt(end_hour)}"
