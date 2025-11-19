from datafakegenerator.providers.base_provider import BaseProvider


class LicensePlateProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        plate_format = self.get_random_data_by_list(
            self.format['plate_number'])
        return "".join(self.sublify_char(c) for c in plate_format)
