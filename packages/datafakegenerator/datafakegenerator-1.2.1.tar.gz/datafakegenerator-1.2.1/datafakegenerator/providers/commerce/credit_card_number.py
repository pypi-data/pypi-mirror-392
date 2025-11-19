import random
from datafakegenerator.providers.base_provider import BaseProvider


class CreditCardNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def _luhn_is_valid(self, number: str) -> bool:
        digits = list(map(int, number))
        total = 0
        double = False
        for d in reversed(digits):
            if double:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
            double = not double
        return total % 10 == 0

    def _generate_cc(self, prefix: str = "4", length: int = 16) -> str:
        """
        Generate a single Luhn-valid mock credit card number.
        Default prefix "4" produces a Visa-like number; adjust prefix/length as needed.
        """
        if len(prefix) >= length:
            raise ValueError("Prefix length must be less than total length.")
        body = list(prefix) + [str(random.randint(0, 9))
                               for _ in range(length - len(prefix) - 1)]
        for check in range(10):
            candidate = "".join(body) + str(check)
            if self._luhn_is_valid(candidate):
                return candidate
        # fallback (very unlikely)
        return "".join(body) + "0"

    def generate_non_blank(self, row_data=None):
        return self._generate_cc()
