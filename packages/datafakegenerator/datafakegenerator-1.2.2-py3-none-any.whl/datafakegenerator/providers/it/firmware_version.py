from datafakegenerator.providers.base_provider import BaseProvider
import random


class FirmwareVersionProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.format_dict = {
            "SemVer": "major.minor.patch, e.g., 1.0.3",
            "PrefixedV": "vMajor.Minor.Patch, e.g., v2.5.1",
            "FW_Prefix": "FW_Major.Minor.Patch, e.g., FW_3.1.4",
            "ShortVersion": "Major.Minor, e.g., 4.2",
            "BuildNumber": "Numeric build, e.g., 1023"
        }

    def generate_non_blank(self, row_data=None):
        fmt = random.choice(list(self.format_dict.keys()))

        if fmt == "SemVer":
            return f"{random.randint(0, 5)}.{random.randint(0, 10)}.{random.randint(0, 20)}"
        elif fmt == "PrefixedV":
            return f"v{random.randint(0, 5)}.{random.randint(0, 10)}.{random.randint(0, 20)}"
        elif fmt == "FW_Prefix":
            return f"FW_{random.randint(0, 5)}.{random.randint(0, 10)}.{random.randint(0, 20)}"
        elif fmt == "ShortVersion":
            return f"{random.randint(0, 5)}.{random.randint(0, 10)}"
        elif fmt == "BuildNumber":
            return str(random.randint(1000, 9999))
        else:
            return "0.0.0"
