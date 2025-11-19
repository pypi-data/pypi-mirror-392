from datafakegenerator.providers.base_provider import BaseProvider


class FakeCompanyNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.company_suffix = ["Inc", "and Sons", "LLC", "Group", "PLC", "Ltd"]

    def generate_non_blank(self, row_data=None):
        pattern = self.get_random_data_by_list(self.format['company'])
        rand_last_name = self.get_random_data_by_list(self.person['last_name'])
        rand_suffix = self.get_random_data_by_list(self.company_suffix)

        company_name = pattern
        while "{{last_name}}" in company_name:
            company_name = company_name.replace(
                "{{last_name}}", rand_last_name, 1)

        return company_name.replace("{{company_suffix}}", rand_suffix)
