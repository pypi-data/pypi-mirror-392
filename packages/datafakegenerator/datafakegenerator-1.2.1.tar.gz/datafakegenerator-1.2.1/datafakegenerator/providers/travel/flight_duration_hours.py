import random
from datafakegenerator.providers.base_provider import BaseProvider


class FlightDurationHoursProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['countries'], **kwargs)

    def generate_non_blank(self, row_data=None):
        return random.uniform(10.5, 25.75)
