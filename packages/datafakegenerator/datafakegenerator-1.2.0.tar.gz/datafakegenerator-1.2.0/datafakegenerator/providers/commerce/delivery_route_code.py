from datafakegenerator.providers.base_provider import BaseProvider
import random
import string


class DeliveryRouteCodeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        route_prefixes = ["RT", "MX", "PH", "CN",
                          "EU", "US", "JP", "BR", "IN", "RU"]
        hub_codes = ["SEA", "LAX", "SIN", "MNL",
                     "DXB", "FRA", "HKG", "AMS", "JFK", "NRT"]
        pattern_type = random.choice(["simple", "airport"])

        if pattern_type == "simple":
            prefix = random.choice(route_prefixes)
            number = random.randint(1, 999)
            optional_letter = random.choice(
                ["", random.choice(string.ascii_uppercase)])
            return f"{prefix}-{number}{optional_letter}"

        else:  # Airport-to-airport style
            origin, destination = random.sample(hub_codes, 2)
            number = str(random.randint(1, 99)).zfill(2)
            return f"{origin}-{destination}-{number}"
