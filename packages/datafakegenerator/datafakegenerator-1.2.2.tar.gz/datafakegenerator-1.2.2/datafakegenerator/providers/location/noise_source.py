from datafakegenerator.providers.base_provider import BaseProvider
import random


class NoiseSourceProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['noise'], **kwargs)

    def _determine_range(self, value):
        ranges = [
            (30, "20-30"),
            (50, "30-50"),
            (70, "60-70"),
            (85, "70-85"),
            (100, "85-100"),
            (120, "120+"),
        ]
        if isinstance(value, (int, float)):
            for upper, category in ranges:
                if value <= upper:
                    return category

    def generate_non_blank(self, row_data=None):

        noise_level = row_data.get('noise_level') if row_data else None
        noise_category = row_data.get('noise_category') if row_data else None

        if noise_level:
            return self.get_dataset_lookup('noise', 'Noise_Level_DB').get(
                self._determine_range(noise_level)).get('Source')

        if noise_category:
            return self.get_dataset_lookup('noise', 'Noise_Level_DB').get(noise_category).get('Category')

        return self.get_row_data_from_datasets('noise', 'Source')
