# providers/advanced/character_sequence_provider.py
from datafakegenerator.providers.base_provider import BaseProvider
import random


class DigitSequenceProvider(BaseProvider):

    def __init__(self, *, length: len = 8, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.length = length

    def generate_non_blank(self, row_data=None):
        return "".join(random.choices("0123456789", k=self.length))
