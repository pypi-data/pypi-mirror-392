from datafakegenerator.providers.base_provider import BaseProvider
import random


class BankBranchCodeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        prefix = random.choice(["001", "002", "003", "004", "005"])
        remaining_length = 12 - len(prefix)
        rest = "".join(str(random.randint(0, 9))
                       for _ in range(remaining_length))
        return prefix + rest
