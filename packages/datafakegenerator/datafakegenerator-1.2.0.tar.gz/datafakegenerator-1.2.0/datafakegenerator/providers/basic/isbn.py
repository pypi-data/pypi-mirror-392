import random
from datafakegenerator.providers.base_provider import BaseProvider


class IsbnProvider(BaseProvider):
    GROUP_CODES = [
        "0", "1",  # English
        "2",       # French
        "3",       # German
        "4",       # Japan
        "5",       # Russian
        "7",       # China
        "80", "81", "82", "83", "84", "85", "86", "87", "88", "89",  # Europe
        "600", "601", "602", "603", "604", "605"  # other regions
    ]

    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def _calculate_isbn10_check_digit(self, digits):
        total = sum((10 - i) * d for i, d in enumerate(digits))
        remainder = total % 11
        check = (11 - remainder) % 11
        return "X" if check == 10 else str(check)

    def _calculate_isbn13_check_digit(self, digits):
        total = sum(d if i % 2 == 0 else 3 * d for i, d in enumerate(digits))
        check = (10 - (total % 10)) % 10
        return str(check)

    def generate_non_blank(self, row_data=None):
        version = random.choice(["ISBN10", "ISBN13"])
        group = random.choice(self.GROUP_CODES)

        if version == "ISBN10":
            remaining_length = 9 - len(group)
            body_digits = [random.randint(0, 9)
                           for _ in range(remaining_length)]
            prefix_digits = [int(d) for d in group]
            digits = prefix_digits + body_digits
            check = self._calculate_isbn10_check_digit(digits)
            isbn = "".join(map(str, digits)) + check

            return f"{isbn[:len(group)]}-{isbn[len(group):len(group)+3]}-{isbn[len(group)+3:-1]}-{isbn[-1]}"

        else:
            prefix = random.choice([978, 979])  # EAN prefix
            prefix_digits = [int(x) for x in str(prefix)]
            group_digits = [int(x) for x in group]
            remaining_length = 12 - len(prefix_digits) - len(group_digits)
            body_digits = [random.randint(0, 9)
                           for _ in range(remaining_length)]
            digits = prefix_digits + group_digits + body_digits
            check = self._calculate_isbn13_check_digit(digits)
            isbn = "".join(map(str, digits)) + check

            return f"{isbn[:3]}-{isbn[3:3+len(group)]}-{isbn[3+len(group):3+len(group)+4]}-{isbn[3+len(group)+4:-1]}-{isbn[-1]}"
