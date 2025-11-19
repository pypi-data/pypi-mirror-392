from datafakegenerator.providers.base_provider import BaseProvider


class CountryCodeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['countries'], **kwargs)

    def generate_non_blank(self, row_data=None):
        country = row_data.get('country') if row_data else None
        city = row_data.get('city') if row_data else None

        if country:
            return self.get_dataset_lookup('countries', 'name').get(country).get('iso2')
        if city:
            return self.get_dataset_lookup('countries', 'capital').get(city).get('iso2')

        return self.get_row_data_from_datasets('countries', 'iso2')
