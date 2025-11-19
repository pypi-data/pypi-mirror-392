from datafakegenerator.providers.base_provider import BaseProvider


class AppVersionProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        num_choice_format = self.get_random_data_by_list(['#.##', '#.#.#'])
        return "".join(self.sublify_char(f) for f in num_choice_format)
