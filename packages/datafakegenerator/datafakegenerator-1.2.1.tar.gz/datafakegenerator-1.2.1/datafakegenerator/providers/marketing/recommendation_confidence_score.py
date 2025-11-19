from datafakegenerator.providers.base_provider import BaseProvider
import random


class RecommendationConfidenceScoreProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, fmt: str = 'decimal', **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.fmt = fmt

    def generate_non_blank(self, row_data=None):

        if self.fmt == 'decimal':
            return round(random.uniform(0, 0.99), 2)
        else:
            return f"{random.randint(0, 99)}%"
