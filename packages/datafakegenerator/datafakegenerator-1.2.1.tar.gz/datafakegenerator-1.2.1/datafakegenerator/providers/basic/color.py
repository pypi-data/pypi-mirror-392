from datafakegenerator.providers.base_provider import BaseProvider


class ColorProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['colors'], **kwargs)

    def generate_non_blank(self, row_data=None):
        hex_color = row_data.get('hex_color') if row_data else None
        short_hex_color = row_data.get('short_hex_color') if row_data else None

        if hex_color:
            return self.get_dataset_lookup(
                'colors', 'Hex').get(hex_color).get('Name')

        if short_hex_color:
            return self.get_dataset_lookup(
                'colors', 'Hex').get(short_hex_color).get('Name')[0:4].lower()

        return self.get_row_data_from_datasets('colors', 'Name')
