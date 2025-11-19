from datafakegenerator.providers.base_provider import BaseProvider


class CityProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['countries'], **kwargs)
        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('countries', 'name')

        country = row_data.get('country') if row_data else None

        return (
            self.lookup.get(country, {}).get('capital')
            or self.get_row_data_from_datasets('countries', 'capital')
        )
