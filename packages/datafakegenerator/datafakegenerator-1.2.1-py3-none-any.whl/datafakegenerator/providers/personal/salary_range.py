from datafakegenerator.providers.base_provider import BaseProvider


class SalaryRangeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        salary_range = [
            "$15,000 - $20,000",
            "$20,000 - $30,000",
            "$30,000 - $45,000",
            "$40,000 - $60,000",
            "$60,000 - $80,000",
            "$80,000 - $120,000",
            "$120,000 - $180,000",
            "$200,000+"
        ]
        return self.get_random_data_by_list(salary_range)
