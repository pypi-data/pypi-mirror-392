from datafakegenerator.providers.base_provider import BaseProvider


class FlightAirlineNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['airlines'], **kwargs)
        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('airlines', 'code')

        airlines_code = row_data.get(
            'flight_airline_code') if row_data else None

        return (
            self.lookup.get(airlines_code, {}).get('name')
            or self.get_row_data_from_datasets('airlines', 'name')
        )
