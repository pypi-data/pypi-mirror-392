import random
from datafakegenerator.providers.base_provider import BaseProvider


class UniversityProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['university'], **kwargs)

    def generate_non_blank(self, row_data=None):
        return self.get_row_data_from_datasets('university', 'university_name')
