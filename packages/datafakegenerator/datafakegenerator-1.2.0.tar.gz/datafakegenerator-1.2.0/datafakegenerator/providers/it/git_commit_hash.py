from datafakegenerator.providers.base_provider import BaseProvider
import random


class GitCommitHashProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, short: bool = True, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.short = short

    def generate_non_blank(self, row_data=None):
        length = 7 if self.short else 40
        return ''.join(random.choices('0123456789abcdef', k=length))
