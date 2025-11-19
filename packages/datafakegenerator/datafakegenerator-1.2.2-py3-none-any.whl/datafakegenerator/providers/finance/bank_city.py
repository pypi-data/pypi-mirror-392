from datafakegenerator.providers.base_provider import BaseProvider


class BankCityProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['bank'], **kwargs)
        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('bank', 'bank')

        bank_name = row_data.get('bank_name') if row_data else None

        return (
            self.lookup.get(bank_name, {}).get('city')
            or self.get_row_data_from_datasets('bank', 'city')
        )
