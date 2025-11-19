from datafakegenerator.providers.base_provider import BaseProvider


class ShortHexColorProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['colors'], **kwargs)

    def generate_non_blank(self, row_data=None):
        color = row_data.get('color') if row_data else None
        hex_color = row_data.get('hex_color') if row_data else None

        if color:
            return self.get_dataset_lookup(
                'colors', 'Name').get(color).get('Hex')[0:4].lower()

        if hex_color:
            return self.get_dataset_lookup(
                'colors', 'Hex').get(hex_color).get('Hex')[0:4].lower()

        return self.get_row_data_from_datasets('colors', 'Hex')[0:4].lower()
