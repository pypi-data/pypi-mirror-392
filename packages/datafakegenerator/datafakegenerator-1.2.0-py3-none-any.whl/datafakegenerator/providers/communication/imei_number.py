from datafakegenerator.providers.base_provider import BaseProvider
import random


class ImeiNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def _luhn_check_digit(self, digits14: str) -> str:
        assert len(digits14) == 14 and digits14.isdigit()
        total = 0
        reverse_digits = digits14[::-1]
        for i, ch in enumerate(reverse_digits, start=1):
            d = int(ch)
            if i % 2 == 1:
                total += d
            else:
                doubled = d * 2
                total += doubled - 9 if doubled > 9 else doubled
        check = (10 - (total % 10)) % 10
        return str(check)

    def generate_non_blank(self, row_data=None):
        tac = f"{random.randint(0, 99999999):08d}"
        snr = f"{random.randint(0, 999999):06d}"
        body14 = tac + snr  # 14 digits
        check_digit = self._luhn_check_digit(body14)
        imei = body14 + check_digit
        return imei
