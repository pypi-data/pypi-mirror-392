from datafakegenerator.providers.base_provider import BaseProvider


class CustomerFeedbackScoreProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        return int(self.generate_number(min=1, max=10))
