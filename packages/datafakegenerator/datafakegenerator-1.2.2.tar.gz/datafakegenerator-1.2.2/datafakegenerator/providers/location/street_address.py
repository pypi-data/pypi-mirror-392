from datafakegenerator.providers.base_provider import BaseProvider
from providers.location.street_name import StreetNameProvider


class StreetAddressProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.street_name_provider = StreetNameProvider()

    def generate_non_blank(self, row_data=None):
        fmt = self.get_random_data_by_list(self.street['address_formats'])
        building_fmt = self.get_random_data_by_list(
            self.street['building_number_formats'])

        street_number = ''.join(self.sublify_char(c) for c in building_fmt)
        address = fmt.replace("{{street_number}}", street_number).replace(
            "{{street_name}}", self.street_name_provider.generate_non_blank())
        return address
