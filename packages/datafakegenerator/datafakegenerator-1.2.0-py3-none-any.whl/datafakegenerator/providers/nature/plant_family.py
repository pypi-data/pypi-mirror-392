from datafakegenerator.providers.base_provider import BaseProvider


class PlantFamilyProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['plants'], **kwargs)

    def generate_non_blank(self, row_data=None):
        plant_common_name = row_data.get(
            'plant_common_name') if row_data else None
        plant_scientific_name = row_data.get(
            'plant_scientific_name') if row_data else None

        if plant_common_name:
            return self.get_dataset_lookup('plants', 'plant_common_name').get(plant_common_name, {}).get('plant_family')

        if plant_scientific_name:
            return self.get_dataset_lookup('plants', 'plant_scientific_name').get(plant_scientific_name, {}).get('plant_family')

        return self.get_row_data_from_datasets('plants', 'plant_family')
