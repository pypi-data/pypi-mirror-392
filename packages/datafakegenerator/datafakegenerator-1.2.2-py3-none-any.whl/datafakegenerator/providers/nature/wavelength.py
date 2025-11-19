from datafakegenerator.providers.base_provider import BaseProvider


class WavelengthProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        return f"{int(self.generate_number(0, 1000))}nm"
