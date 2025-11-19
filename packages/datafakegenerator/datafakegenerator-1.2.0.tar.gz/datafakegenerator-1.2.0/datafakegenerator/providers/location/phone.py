from datafakegenerator.providers.base_provider import BaseProvider


class PhoneProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, format: str = "###-###-####", **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.format = format

    def generate_non_blank(self, row_data=None):
        return "".join(self.sublify_char(c) for c in self.format)
