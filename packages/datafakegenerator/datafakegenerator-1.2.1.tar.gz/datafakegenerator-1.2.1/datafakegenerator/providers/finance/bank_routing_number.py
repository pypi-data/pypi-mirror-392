import random
from datafakegenerator.providers.base_provider import BaseProvider


class BankRoutingNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self) -> str:
        digits = [random.randint(0, 9) for _ in range(8)]
        checksum = sum(digits) % 10  # simplified checksum
        digits.append(checksum)
        return ''.join(str(d) for d in digits)
