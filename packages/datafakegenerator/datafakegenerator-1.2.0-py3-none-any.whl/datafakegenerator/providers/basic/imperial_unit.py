from datafakegenerator.providers.base_provider import BaseProvider


class ImperialUnitProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        return self.get_random_data_by_liste(self.basic['imperial_units'])
