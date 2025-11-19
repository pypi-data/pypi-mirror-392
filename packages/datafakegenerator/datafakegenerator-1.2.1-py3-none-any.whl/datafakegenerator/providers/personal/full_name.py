from datafakegenerator.providers.base_provider import BaseProvider


class FullNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        first_name = self.get_random_data_by_list(self.person['first_name']['female'] +
                                                  self.person['first_name']['male'])
        last_name = self.get_random_data_by_list(self.person['last_name'])
        return f"{first_name} {last_name}"
