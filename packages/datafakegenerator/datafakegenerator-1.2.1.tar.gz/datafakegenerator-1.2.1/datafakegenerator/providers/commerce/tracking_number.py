from datafakegenerator.providers.base_provider import BaseProvider
import random
import string


class TrackingNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        prefixes = ["UPS", "FDX", "DHL", "LBC",
                    "USPS", "JNT", "NINJA", "GRB", "XDE"]
        prefix = random.choice(prefixes)
        numeric_part = ''.join(random.choices(
            string.digits, k=random.randint(8, 12)))

        suffix = ''.join(random.choices(
            string.ascii_uppercase, k=random.choice([0, 2, 3])))
        formats = [
            f"{prefix}{numeric_part}{suffix}",
            f"{prefix}-{numeric_part}-{suffix}" if suffix else f"{prefix}-{numeric_part}",
            f"{numeric_part}{suffix}",
            f"{prefix}{numeric_part}"
        ]

        return random.choice(formats)
