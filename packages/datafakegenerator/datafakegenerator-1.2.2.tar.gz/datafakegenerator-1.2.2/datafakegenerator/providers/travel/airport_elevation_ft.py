from datafakegenerator.providers.base_provider import BaseProvider


class AirportElevationFtProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['airport'], **kwargs)

    def generate_non_blank(self, row_data=None):
        airport_code = row_data.get('airport_code') if row_data else None
        airport_name = row_data.get('airport_name') if row_data else None

        if airport_code:
            return self.get_dataset_lookup('airport', 'iata_code').get(airport_code).get('elevation_ft')
        if airport_name:
            return self.get_dataset_lookup('airport', 'name').get(airport_name).get('elevation_ft')
        return self.get_row_data_from_datasets('airport', 'elevation_ft')
