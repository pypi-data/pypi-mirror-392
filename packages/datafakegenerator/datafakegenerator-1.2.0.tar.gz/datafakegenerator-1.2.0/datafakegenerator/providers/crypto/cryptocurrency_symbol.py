from datafakegenerator.providers.base_provider import BaseProvider


class CryptocurrencySymbolProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['cryptocurrency'], **kwargs)
        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('cryptocurrency', 'name')

        cryptocurrency_name = row_data.get(
            'cryptocurrency_name') if row_data else None

        return (
            self.lookup.get(cryptocurrency_name, {}).get('symbol')
            or self.get_row_data_from_datasets('cryptocurrency', 'symbol')
        )
