import numpy as np
from datafakegenerator.providers.base_provider import BaseProvider


class NormalDistributionProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0,  mean: float = 0.0, std_dev: float = 1.0, decimals: int = 2, ** kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.mean = mean
        self.std_dev = std_dev
        self.decimals = decimals

    def generate_non_blank(self, row_data=None):
        return round(np.random.normal(self.mean, self.std_dev), self.decimals)
