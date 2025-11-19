import numpy as np
from datafakegenerator.providers.base_provider import BaseProvider


class BinomialDistributionProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, trials: int = 10, probability: float = 0.5, ** kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.trials = trials
        self.p = probability

    def generate_non_blank(self, row_data=None):
        return int(np.random.binomial(self.trials, self.p))
