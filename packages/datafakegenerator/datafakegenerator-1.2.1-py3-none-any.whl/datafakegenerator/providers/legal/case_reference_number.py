from datafakegenerator.providers.base_provider import BaseProvider
import random


class CaseReferenceNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        pattern = random.choice(
            ["supreme", "case_hash", "criminal", "civil", "admin"])

        if pattern == "supreme":
            number = random.randint(10000, 299999)
            return f"G.R. No. {number}"

        elif pattern == "case_hash":
            year = random.randint(10, 25)
            seq1 = random.randint(1, 999)
            seq2 = random.randint(1, 999)
            return f"Case #{year}-CR-{seq2:03d}"

        elif pattern == "criminal":
            year = random.randint(2010, 2025)
            seq = random.randint(1, 99999)
            return f"CR-{year}-{seq:05d}"

        elif pattern == "civil":
            year = random.randint(2010, 2025)
            seq = random.randint(1, 9999)
            return f"CV-{year}-{seq:04d}"

        elif pattern == "admin":
            year = random.randint(10, 25)
            seq = random.randint(1, 999)
            return f"ADMIN-{year}-{seq:03d}"
