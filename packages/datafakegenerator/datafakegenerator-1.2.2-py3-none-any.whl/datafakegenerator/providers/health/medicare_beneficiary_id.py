import random
import string
from datafakegenerator.providers.base_provider import BaseProvider


class MedicareBeneficiaryIdProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def _rand_digit(self, non_zero=False):
        return str(random.randint(1, 9) if non_zero else random.randint(0, 9))

    def generate_non_blank(self, row_data=None):

        allowed_letters = ''.join(
            c for c in string.ascii_uppercase if c not in 'SLOIBZ')

        pattern = ['C', 'A', 'N', 'N', 'A', 'N', 'N', 'A', 'A', 'N', 'A']

        mbi = ''.join(
            self._rand_digit(True) if p == 'C' else
            self._rand_digit() if p == 'N' else
            self.get_random_data_by_list(allowed_letters)
            for p in pattern
        )

        formatted_mbi = f"{mbi[:4]}-{mbi[4:7]}-{mbi[7:]}"
        return formatted_mbi
