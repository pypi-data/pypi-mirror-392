from datafakegenerator.providers.base_provider import BaseProvider


class ShoeSizeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, type: str = "US", **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.type = type

    def generate_non_blank(self, row_data=None):
        sizes_us = (
            "5", "5.5", "6", "6.5", "7", "7.5", "8", "8.5",
            "9", "9.5", "10", "10.5", "11", "11.5", "12", "13", "14"
        )
        sizes_eu = (
            "37", "38", "39", "40", "41", "42", "43", "44",
            "45", "46", "47", "48"
        )
        if self.type == "US":
            return self.get_random_data_by_list(sizes_us)
        else:
            return self.get_random_data_by_list(sizes_eu)
