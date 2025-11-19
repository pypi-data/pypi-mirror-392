from datafakegenerator.providers.base_provider import BaseProvider


class CustomListProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, custom_format: str = '', **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.custom_format = custom_format.split(',')

    def generate_non_blank(self, row_data=None):
        return self.get_random_data_by_list(self.custom_format)
