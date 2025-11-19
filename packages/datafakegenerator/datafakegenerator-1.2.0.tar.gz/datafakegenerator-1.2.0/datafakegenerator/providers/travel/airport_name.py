from datafakegenerator.providers.base_provider import BaseProvider


class AirportNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['airport'], **kwargs)

        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('airport', 'iata_code')

        airport_code = row_data.get('airport_code') if row_data else None
        return (
            self.lookup.get(airport_code, {}).get('name')
            or self.get_row_data_from_datasets('airport', 'name')
        )
