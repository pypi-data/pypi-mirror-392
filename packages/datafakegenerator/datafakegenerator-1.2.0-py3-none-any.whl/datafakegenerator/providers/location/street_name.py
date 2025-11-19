from datafakegenerator.providers.base_provider import BaseProvider


class StreetNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        fmt = self.get_random_data_by_list(self.street['street_formats'])
        street_suffix = self.get_random_data_by_list(self.street['suffix'])

        name_mix_gender = self.person['first_name']['female'] + \
            self.person['first_name']['male']
        first_name = self.get_random_data_by_list(name_mix_gender)
        last_name = self.get_random_data_by_list(self.person['last_name'])

        street_name = fmt.replace("{{first_name}}", first_name).replace(
            "{{last_name}}", last_name).replace("{{street_suffix}}", street_suffix)
        return street_name
