import numpy as np
from datafakegenerator.providers.base_provider import BaseProvider


class ExponentialDistributionProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, lam: float = 1.0, ** kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.lam = lam

    def generate_non_blank(self, row_data=None):
        return np.random.exponential(1.0 / self.lam)
