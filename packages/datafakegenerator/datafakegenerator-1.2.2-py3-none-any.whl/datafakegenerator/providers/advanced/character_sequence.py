# providers/advanced/character_sequence_provider.py
from datafakegenerator.providers.base_provider import BaseProvider


class CharacterSequenceProvider(BaseProvider):
    """
    Generates random sequences of characters, digits, and symbols
    based on a format string that can include wildcard symbols:

    Wildcards:
      # → random digit (0-9)
      @ → random lowercase letter (a-z)
      ^ → random uppercase letter (A-Z)
      * → random digit or letter
      $ → random digit or lowercase letter
      % → random digit or uppercase letter
    """

    def __init__(self, *, format: str = "@@##%", blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.format = format

    def generate_non_blank(self, row_data=None):
        return "".join(self.sublify_char(c) for c in self.format)
