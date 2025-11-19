from datafakegenerator.providers.base_provider import BaseProvider
from datetime import datetime


class UserCohortProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        quarter = self.get_random_data_by_list(['Q1', 'Q2', 'Q3', 'Q4'])
        year_range = self.get_random_data_by_list([y for y in range(
            int(datetime.now().year), int(datetime.now().year) + 5)])

        return f"{year_range}-{quarter}"
