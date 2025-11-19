from datafakegenerator.providers.base_provider import BaseProvider
import rstr


class RegularExpressionProvider(BaseProvider):

    def __init__(self, *, blank_percentage: float = 0.0, format: str = '', **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.format = format

    def generate_non_blank(self, row_data=None):
        if not self.format:
            return ''
        try:
            value = rstr.xeger(self.format)
            return value
        except Exception as e:
            return f"[Invalid regex: {e}]"
