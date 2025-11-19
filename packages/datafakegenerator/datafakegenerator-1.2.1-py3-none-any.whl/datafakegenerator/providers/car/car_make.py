from datafakegenerator.providers.base_provider import BaseProvider


class CarMakeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['cars'], **kwargs)
        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('cars', 'Model')

        car_model = row_data.get('car_model') if row_data else None

        return (
            self.lookup.get(car_model, {}).get('Make')
            or self.get_row_data_from_datasets('cars', 'Make')
        )
