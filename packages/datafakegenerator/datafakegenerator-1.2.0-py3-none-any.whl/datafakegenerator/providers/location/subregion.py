from datafakegenerator.providers.base_provider import BaseProvider


class SubregionProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['countries'], **kwargs)

    def generate_non_blank(self, row_data=None):
        country = row_data.get('country') if row_data else None
        city = row_data.get('city') if row_data else None

        if country:
            return self.get_dataset_lookup('countries', 'name').get(country).get('subregion')
        if city:
            return self.get_dataset_lookup('countries', 'capital').get(city).get('subregion')

        return self.get_row_data_from_datasets('countries', 'subregion')
