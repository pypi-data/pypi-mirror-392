from datafakegenerator.providers.base_provider import BaseProvider
import random


class NoiseCategoryProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['noise'], **kwargs)

        self.lookup = self.get_dataset_lookup('noise', 'Source')
        self.categories_list = list(
            {row['Category'] for row in self.lookup.values()})

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
        noise_source = row_data.get('noise_source') if row_data else None

        if noise_level:
            return self.get_dataset_lookup('noise', 'Noise_Level_DB').get(
                self._determine_range(noise_level)).get('Source')

        if noise_source:
            return self.get_dataset_lookup('noise', 'Noise_Level_DB').get(noise_source).get('Category')

        return self.get_row_data_from_datasets('noise', 'Category')
