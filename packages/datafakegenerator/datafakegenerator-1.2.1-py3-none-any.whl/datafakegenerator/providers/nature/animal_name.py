from datafakegenerator.providers.base_provider import BaseProvider


class AnimalNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['animals'], **kwargs)
        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup(
                'animals', 'animal_scientific_name')

        animal_scientific_name = row_data.get(
            'animal_name') if row_data else None

        return (
            self.lookup.get(animal_scientific_name, {}).get('animal_name')
            or self.get_row_data_from_datasets('animals', 'animal_name')
        )
