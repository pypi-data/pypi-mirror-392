import random
import string
from datafakegenerator.providers.base_provider import BaseProvider


class IbanProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, continent: string = None, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.IBAN_GROUPS = {
            "central_western_eu": {"pattern": {"bank": 8, "account": 10}, "length": 22, "code": "CW"},
            "southern_eu": {"pattern": {"bank": 4, "branch": 4, "account": 12}, "length": 27, "code": "SE"},
            "nordic": {"pattern": {"bank": 4, "account": 8}, "length": 15, "code": "ND"},
            "eastern_eu": {"pattern": {"bank": 8, "account": 16}, "length": 28, "code": "EE"},
            "uk_islands": {"pattern": {"bank": 4, "sort": 6, "account": 8}, "length": 22, "code": "UK"},
            "middle_east": {"pattern": {"bank": 4, "account": 14}, "length": 24, "code": "ME"},
            "africa": {"pattern": {"bank": 5, "branch": 5, "account": 10}, "length": 27, "code": "AF"},
            "asia_": {"pattern": {"bank": 4, "account": 14}, "length": 24, "code": "AS"},
        }
        self.continent = continent

    def _numify(self, s):
        return ''.join(str(ord(c.upper()) - 55) if c.isalpha() else c for c in s)

    def _mod97(self, s):
        r = 0
        for i in range(0, len(s), 9):
            r = (r * (10 ** len(s[i:i+9])) + int(s[i:i+9])) % 97
        return r

    def _compute_check(self, cc, bban):
        rearr = bban + cc + "00"
        num = self._numify(rearr)
        check = 98 - self._mod97(num)
        return f"{check:02d}"

    def generate_non_blank(self, row_data=None):
        g = self.IBAN_GROUPS[self.continent or random.choice(
            list(self.IBAN_GROUPS.keys()))]
        cc = g["code"]
        pattern = g["pattern"]

        bban_parts = []
        for part, length in pattern.items():
            chars = string.ascii_uppercase if "bank" in part else string.digits
            bban_parts.append(''.join(random.choices(chars, k=length)))
        bban = ''.join(bban_parts)

        check = self._compute_check(cc, bban)
        iban = f"{cc}{check}{bban}"
        return ' '.join(iban[i:i+4] for i in range(0, len(iban), 4))
