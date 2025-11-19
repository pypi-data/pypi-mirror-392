from datafakegenerator.providers.base_provider import BaseProvider
import random


class NoiseLevelProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['noise'], **kwargs)

    def _parse_level(self, level_str):
        if '-' in level_str:
            low, high = map(int, level_str.split('-'))
        elif '+' in level_str:
            low = int(level_str.replace('+', ''))
            high = low + 20
        else:
            low = high = int(level_str)
        return round(random.uniform(low, high), 1)

    def generate_non_blank(self, row_data=None):
        noise_source = row_data.get('noise_source') if row_data else None
        noise_category = row_data.get('noise_category') if row_data else None

        if noise_source:
            get_noise_level_DB = self.get_dataset_lookup(
                'noise', 'Source').get(noise_source).get('Noise_Level_DB')
            return self._parse_level(get_noise_level_DB)

        if noise_category:
            get_noise_level_DB = self.get_dataset_lookup(
                'noise', 'Category').get(noise_category).get('Noise_Level_DB')
            return self._parse_level(get_noise_level_DB)

        return round(random.uniform(20, 120), 1)
