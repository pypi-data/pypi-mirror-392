from datafakegenerator.providers.base_provider import BaseProvider
import random


class FileSizeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        unit = self.get_random_data_by_list(self.it['file_size_units'])
        ranges = {
            "B": (100, 999999),
            "KB": (1, 1024),
            "MB": (0.1, 2048),
            "GB": (0.1, 512),
            "TB": (0.1, 20),
            "PB": (0.01, 1),
        }
        low, high = ranges[unit]
        value = random.uniform(low, high)
        return f"{value:.2f} {unit}"
