from datafakegenerator.providers.base_provider import BaseProvider


class EmailAddressProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        return (
            self.format['email']
            .replace('{{user_name}}', self.generate_username(row_data))
            .replace('{{domain_name}}', self.get_random_data_by_list(self.it['domains']))
        )
