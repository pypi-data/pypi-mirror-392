import random
from datafakegenerator.providers.base_provider import BaseProvider


class FlightNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['airlines'], **kwargs)

    def generate_non_blank(self, row_data=None):
        code = self.get_row_data_from_datasets('airlines', 'code')
        number = random.randint(1, 9999)
        return f"{code}{number}"
