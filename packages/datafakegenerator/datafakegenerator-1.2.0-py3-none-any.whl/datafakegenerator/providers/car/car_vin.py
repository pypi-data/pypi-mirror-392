import re
from datafakegenerator.providers.base_provider import BaseProvider


class CarVinProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        vin_chars = "1234567890ABCDEFGHJKLMNPRSTUVWXYZ"

        def bothify(t): return re.sub(
            r"\?", lambda _: self.get_random_data_by_list(vin_chars), t)

        def char_weight(c): return int(c) if c.isdigit() else (
            ord(c) - 64 if ord(c) <= 73 else
            ord(c) - 73 if ord(c) <= 82 else
            ord(c) - 81
        )

        def vin_weight(s, w): return sum(char_weight(
            c) * w[i] for i, c in enumerate(s[:len(w)]))

        front = bothify("????????")
        rear = bothify("????????")

        checksum_val = (vin_weight(front, [
                        8, 7, 6, 5, 4, 3, 2, 10]) + vin_weight(rear, [9, 8, 7, 6, 5, 4, 3, 2])) % 11
        checksum = "X" if checksum_val == 10 else str(checksum_val)

        return front + checksum + rear
