from datafakegenerator.providers.base_provider import BaseProvider
import random
import string


class FingerprintIdProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.format_dict = {
            "FP-Sequential": "FP" + "{:05d}",
            "FP-DateSeq": "FP-{date}-{seq}",
            "FP-Alphanumeric": "fp_" + "{alnum}",
            "User-FP": "{user}-FP{seq}",
            "UID-Numeric": "uid" + "{num}"
        }

    def generate_non_blank(self, row_data=None):
        fmt = self.get_random_data_by_list(list(self.format_dict.keys()))
        if fmt == "FP-Sequential":
            return f"FP{random.randint(1, 99999):05d}"
        elif fmt == "FP-DateSeq":
            date_str = "20251104"  # for example, could use datetime.today().strftime("%Y%m%d")
            seq = random.randint(1, 99)
            return f"FP-{date_str}-{seq}"
        elif fmt == "FP-Alphanumeric":
            alnum = ''.join(random.choices(
                string.ascii_lowercase + string.digits, k=8))
            return f"fp_{alnum}"
        elif fmt == "User-FP":
            user = f"EMP{random.randint(100, 999)}"
            seq = random.randint(1, 9)
            return f"{user}-FP{seq}"
        elif fmt == "UID-Numeric":
            return f"uid{random.randint(100000, 999999)}"
        else:
            return "FP_UNKNOWN"
