from datafakegenerator.providers.base_provider import BaseProvider
import random
import string


class PostalCodeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0,  **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

        self.country_formats = {
            # 🌏 Asia-Pacific
            "PH": lambda: str(random.randint(1000, 9999)),  # Philippines
            # Japan
            "JP": lambda: f"{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "IN": lambda: str(random.randint(100000, 999999)),  # India
            "CN": lambda: str(random.randint(100000, 999999)),  # China
            "SG": lambda: str(random.randint(100000, 999999)),  # Singapore
            # Hong Kong (non-official)
            "HK": lambda: str(random.randint(100000, 999999)),
            # South Korea
            "KR": lambda: f"{random.randint(100, 999)}-{random.randint(100, 999)}",
            "AU": lambda: str(random.randint(200, 9999)),  # Australia
            "NZ": lambda: str(random.randint(1000, 9999)),  # New Zealand
            "TH": lambda: str(random.randint(10000, 99999)),  # Thailand
            "MY": lambda: str(random.randint(10000, 99999)),  # Malaysia

            # 🌎 Americas
            "US": self._generate_us_zip,
            "CA": self._generate_ca_postal,
            "MX": lambda: str(random.randint(10000, 99999)),  # Mexico
            # Brazil
            "BR": lambda: f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
            # Argentina
            "AR": lambda: f"{random.randint(1000, 9999)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}",
            "CL": lambda: str(random.randint(1000000, 9999999)),  # Chile
            "CO": lambda: str(random.randint(100000, 999999)),  # Colombia
            "PE": lambda: str(random.randint(10000, 99999)),  # Peru

            # 🌍 Europe
            "UK": self._generate_uk_postcode,
            "DE": lambda: str(random.randint(10000, 99999)),  # Germany
            "FR": lambda: str(random.randint(10000, 95999)),  # France
            "ES": lambda: str(random.randint(1000, 52999)).zfill(5),  # Spain
            "IT": lambda: str(random.randint(10000, 98100)),  # Italy
            # Netherlands
            "NL": lambda: f"{random.randint(1000, 9999)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}",
            # Sweden
            "SE": lambda: f"{random.randint(100, 999)} {random.randint(10, 99)}",
            "NO": lambda: str(random.randint(1000, 9999)),  # Norway
            # Poland
            "PL": lambda: f"{random.randint(10, 99)}-{random.randint(100, 999)}",
            "CH": lambda: str(random.randint(1000, 9999)),  # Switzerland

            # 🌍 Middle East & Africa
            "AE": lambda: str(random.randint(10000, 99999)),  # UAE (approx.)
            "SA": lambda: str(random.randint(10000, 99999)),  # Saudi Arabia
            "ZA": lambda: str(random.randint(1000, 9999)),  # South Africa
            "EG": lambda: str(random.randint(11111, 99999)),  # Egypt
            "KE": lambda: str(random.randint(10000, 99999)),  # Kenya
        }

        self.available_countries = list(self.country_formats.keys())

    def _generate_us_zip(self):
        """US ZIP or ZIP+4"""
        if random.random() < 0.2:
            return f"{random.randint(10000, 99999)}-{random.randint(1000, 9999)}"
        return str(random.randint(10000, 99999))

    def _generate_ca_postal(self):
        """Canadian postal code: A1A 1A1"""
        letters = string.ascii_uppercase
        digits = string.digits
        return f"{random.choice(letters)}{random.choice(digits)}{random.choice(letters)} {random.choice(digits)}{random.choice(letters)}{random.choice(digits)}"

    def _generate_uk_postcode(self):
        """UK postal code (simplified realistic pattern)"""
        letters = string.ascii_uppercase
        digits = string.digits
        return f"{random.choice(letters)}{random.choice(letters)}{random.choice(digits)} {random.choice(digits)}{random.choice(letters)}{random.choice(letters)}"

    def generate_non_blank(self, row_data=None):
        country = random.choice(self.available_countries)
        postal_code = self.country_formats[country]()
        return f"{country}-{postal_code}"
