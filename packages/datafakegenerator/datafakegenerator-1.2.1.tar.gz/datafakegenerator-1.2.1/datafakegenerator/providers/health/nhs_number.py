import random
import string
from datafakegenerator.providers.base_provider import BaseProvider


class NhsNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def _calculate_check_digit(self, digits):
        total = sum(weight * digit for weight,
                    digit in zip(range(10, 1, -1), digits))
        remainder = total % 11
        check_digit = 11 - remainder
        if check_digit == 11:
            return 0
        elif check_digit == 10:
            return None
        return check_digit

    def generate_non_blank(self, row_data=None):
        digits = [random.randint(0, 9) for _ in range(8)]
        for ninth_digit in range(10):  # deterministic check, no infinite loop
            candidate = digits + [ninth_digit]
            check_digit = self._calculate_check_digit(candidate)
            if check_digit is not None:  # valid checksum found
                nhs_number = ''.join(map(str, candidate)) + str(check_digit)
                return f"{nhs_number[:3]} {nhs_number[3:6]} {nhs_number[6:]}"
