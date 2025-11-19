from datafakegenerator.providers.base_provider import BaseProvider
from providers.basic.time import TimeProvider


class FlightDepartureTimeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        return TimeProvider(fmt="12 Hour").generate_non_blank()
